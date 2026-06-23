import pandas as pd
from rapidfuzz import process, fuzz
from pathlib import Path

class ICD10Linker:
    _instance = None

    def __new__(cls):
        CURRENT_DIR = Path(__file__).parent
        csv_path = CURRENT_DIR / "data" / "codes.csv"
        if cls._instance is None:
            cls._instance = super(ICD10Linker, cls).__new__(cls)
            # Load the CSV - Assuming columns: Code_Short, Type, Code_Full, Description, Long_Desc, Category
            # Based on your data: A010,4,A0104,"Typhoid arthritis"
            cls._instance.df = pd.read_csv(
               csv_path, 
                names=["Short", "Type", "Full", "Desc", "Long", "Cat"], 
                header=0)
            # Create a list of descriptions for fast matching
            cls._instance.descriptions = cls._instance.df['Desc'].tolist()
            cls._instance.linked_data = {}
        return cls._instance

    def __init__(self):
        pass

    def link(cls, query_text, threshold=80):
        if query_text in cls._instance.linked_data:
            return cls.linked_data[query_text]
        
        # Find the best match in the 70k descriptions
        match = process.extractOne(query_text, cls._instance.descriptions, scorer=fuzz.WRatio)
        
        if match and match[1] >= threshold:
            matched_desc = match[0]
            row = cls._instance.df[cls._instance.df['Desc'] == matched_desc].iloc[0]
            
            result = {
                "icd10": row['Full'],
                "description": row['Desc'],
                "confidence": match[1]
            }
            cls._instance.linked_data[query_text] = result
            return result
        
        result = {"icd10": "Unknown"}
        cls._instance.linked_data[query_text] = result
        return result

# Example usage:
# if __name__ == "__main__":
# icd_linker = ICD10Linker()
# result = icd_linker.link("Typhoid")
# print(result)
