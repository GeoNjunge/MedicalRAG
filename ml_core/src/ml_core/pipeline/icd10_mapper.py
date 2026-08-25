import string

import pandas as pd
from rapidfuzz import fuzz, process
from pathlib import Path

from ml_core.logging_utils import CentralizedLogger

logger = CentralizedLogger.get_logger(__name__)


class ICD10Linker:
    _instance = None
    _MATCH_THRESHOLD = 88
    _SUBJECT_ROOT_PENALTY = 35
    _TOP_CANDIDATES = 15
    _PUNCT_TABLE = str.maketrans("", "", string.punctuation)
    _PRIMARY_SUBJECT_ROOTS = frozenset(
        {
            "typhoid",
            "paratyphoid",
            "tuberculosis",
            "tuberculous",
            "salmonella",
            "cholera",
            "malaria",
            "dengue",
            "influenza",
            "syphilis",
            "gonorrhea",
            "shigella",
            "ebola",
            "rabies",
            "measles",
            "mumps",
            "rubella",
            "pertussis",
            "diphtheria",
            "tetanus",
            "anthrax",
            "plague",
            "leprosy",
            "histoplasmosis",
            "candidiasis",
            "cryptococcosis",
            "aspergillosis",
            "coccidioidomycosis",
            "brucellosis",
            "leptospirosis",
            "toxoplasmosis",
            "trichinosis",
            "schistosomiasis",
            "filariasis",
            "hookworm",
            "ascariasis",
            "amebiasis",
            "giardiasis",
            "cryptosporidiosis",
            "cyclosporiasis",
            "listeriosis",
            "botulism",
            "clostridium",
            "staphylococcus",
            "streptococcus",
            "pneumococcus",
            "meningococcus",
            "legionella",
            "mycobacterium",
            "nocardiosis",
            "actinomycosis",
        }
    )
    _PRIORITY_OVERRIDE_SPECS = (
        (("hfpef", "heart failure"), "I509"),
        (("essential hypertension", "hypertension"), "I10"),
        (("acute kidney injury", "aki"), "N179"),
    )

    def __new__(cls):
        current_dir = Path(__file__).parent
        csv_path = current_dir / "data" / "codes.csv"
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            df = pd.read_csv(
                csv_path,
                names=["Short", "Type", "Full", "Desc", "Long", "Cat"],
                header=0,
            )
            cls._instance.df = df
            cls._instance.linked_data = {}

            desc_norms = []
            cat_norms = []
            search_targets = []
            for _, row in df.iterrows():
                desc_norm = cls._normalize(row["Desc"])
                cat_norm = cls._normalize(row["Cat"])
                desc_norms.append(desc_norm)
                cat_norms.append(cat_norm)
                search_targets.append(f"{desc_norm} {cat_norm}".strip())

            cls._instance._desc_norms = desc_norms
            cls._instance._cat_norms = cat_norms
            cls._instance._search_targets = search_targets
            cls._instance._override_rows = cls._build_override_rows(df)
        return cls._instance

    def __init__(self):
        pass

    @staticmethod
    def _normalize(text) -> str:
        if text is None or (isinstance(text, float) and pd.isna(text)):
            return ""
        lowered = str(text).lower()
        no_punct = lowered.translate(ICD10Linker._PUNCT_TABLE)
        return " ".join(no_punct.split())

    @classmethod
    def _extract_subject_roots(cls, *texts: str) -> set[str]:
        roots: set[str] = set()
        for text in texts:
            for token in cls._normalize(text).split():
                if token in cls._PRIMARY_SUBJECT_ROOTS:
                    roots.add(token)
        return roots

    @classmethod
    def _build_override_rows(cls, df: pd.DataFrame) -> list[tuple[tuple[str, ...], pd.Series]]:
        rows: list[tuple[tuple[str, ...], pd.Series]] = []
        for terms, code_full in cls._PRIORITY_OVERRIDE_SPECS:
            matches = df[df["Full"] == code_full]
            if matches.empty:
                logger.warning("Priority override code %s not found in ICD-10 dataset", code_full)
                continue
            rows.append((terms, matches.iloc[0]))
        return rows

    @staticmethod
    def _token_scorer(query: str, candidate: str, score_cutoff: float = 0) -> float:
        return float(fuzz.token_set_ratio(query, candidate))

    def _apply_subject_penalty(
        self, query_norm: str, desc_norm: str, cat_norm: str, score: float
    ) -> float:
        roots = self._extract_subject_roots(desc_norm, cat_norm)
        if not roots:
            return score
        adjusted = score
        for root in roots:
            if root not in query_norm:
                adjusted -= self._SUBJECT_ROOT_PENALTY
        return max(adjusted, 0.0)

    def _find_best_match(self, query_norm: str) -> tuple[int, float] | None:
        candidates = process.extract(
            query_norm,
            self._search_targets,
            scorer=self._token_scorer,
            limit=self._TOP_CANDIDATES,
        )
        best_idx = None
        best_score = 0.0
        for _, raw_score, idx in candidates:
            adjusted = self._apply_subject_penalty(
                query_norm,
                self._desc_norms[idx],
                self._cat_norms[idx],
                raw_score,
            )
            if adjusted > best_score:
                best_score = adjusted
                best_idx = idx
        if best_idx is None:
            return None
        return best_idx, best_score

    @staticmethod
    def _matches_override_term(query_norm: str, term: str) -> bool:
        if " " in term:
            return term in query_norm
        return query_norm == term or term in query_norm.split()

    def _try_priority_override(self, query_norm: str) -> dict | None:
        for terms, row in self._override_rows:
            if any(self._matches_override_term(query_norm, term) for term in terms):
                return {
                    "icd10": row["Full"],
                    "description": row["Desc"],
                    "confidence": self._MATCH_THRESHOLD,
                }
        return None

    def link(self, query_text, threshold=None):
        if threshold is None:
            threshold = self._MATCH_THRESHOLD

        if query_text in self.linked_data:
            return self.linked_data[query_text]

        query_norm = self._normalize(query_text)
        if not query_norm:
            result = {"icd10": "Unknown"}
            self.linked_data[query_text] = result
            return result

        match = self._find_best_match(query_norm)
        if match and match[1] >= threshold:
            idx, confidence = match
            row = self.df.iloc[idx]
            result = {
                "icd10": row["Full"],
                "description": row["Desc"],
                "confidence": confidence,
            }
            self.linked_data[query_text] = result
            return result

        override = self._try_priority_override(query_norm)
        if override:
            self.linked_data[query_text] = override
            return override

        result = {"icd10": "Unknown"}
        self.linked_data[query_text] = result
        return result
