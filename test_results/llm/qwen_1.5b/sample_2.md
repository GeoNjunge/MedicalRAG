### Key Findings

- **Glucose:** 104.00 mg/dL (High, 70.0 - 99.9)
- **HbA1c:** 5.8% (Abnormal, <5.7)
- **Potassium:** 6.1 mEq/L (Critical High, 3.5-5.1)
- **Total Cholesterol:** 215 mg/dL (High, 100-199)
- **LDL:** 145 mg/dL (High, <100)
- **HDL:** 42 mg/dL (Low, >40)

### Summary of Diseases and Severity Levels

- **Diabetes Mellitus:** Elevated HbA1c
- **Hyperlipidemia:** Elevated Total Cholesterol, LDL, and HDL
- **Hyperkalemia:** Potassium Level Abnormal

### Summary of Laboratory Results

- **Glucose:** 104.00 mg/dL (High, 70.0 - 99.9)
- **HbA1c:** 5.8% (Abnormal, <5.7)
- **Potassium:** 6.1 mEq/L (Critical High, 3.5-5.1)
- **Total Cholesterol:** 215 mg/dL (High, 100-199)
- **LDL:** 145 mg/dL (High, <100)
- **HDL:** 42 mg/dL (Low, >40)

### Summary of Mismatches

- **Decimal Separator:** Uses both . (104.00) and , (5,8) as decimal separators.
- **Nested Table:** The LIPIDS_SUBTABLE is embedded inside the main table structure using empty cells and > prefixing.
- **Date Format:** Header uses DD-MMM-YYYY, but the footer might use YYYY.MM.DD.
- **Non-Standard Units:** x10^3/uL vs cells/mm3 (see below).
- **Language:** "NOM" (French) vs "GENDER" (English).

### Notes

- **Hemolysis:** Detected in Potassium sample, Result 6.1 might be skewed +15%.
- **Comments:** "Patient reported 'feeling dizzy'; BP was 140/90." Verified By: Dr. J. Smith_ID#9821, Report Printed: 2026.03.24 @ 14:49:10.