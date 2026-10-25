from pathlib import Path
import pandas as pd

project_folder = Path(__file__).resolve().parent
file_path = project_folder / "data" / "Online Retail.xlsx"

print("Reading the Excel file. Please wait...")
df = pd.read_excel(file_path)

print("\nROWS AND COLUMNS")
print(df.shape)

print("\nCOLUMN NAMES")
print(df.columns.tolist())

print("\nDATA TYPES")
print(df.dtypes)

print("\nFIRST FIVE ROWS")
print(df.head().to_string(index=False))

print("\nMISSING VALUES")
print(df.isna().sum())

print("\nEXACT DUPLICATE ROWS")
print(df.duplicated().sum())

print("\nNUMERICAL SUMMARY")
print(df[["Quantity", "UnitPrice"]].describe())

print("\nDATE RANGE")
print(df["InvoiceDate"].min(), "to", df["InvoiceDate"].max())