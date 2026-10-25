from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

print("Reading Excel. Please wait...")
raw = pd.read_excel(DATA / "Online Retail.xlsx")

# Preserve inspection evidence.
raw.head(20).to_csv(REPORTS / "before_cleaning.csv", index=False)
raw.isna().sum().to_csv(REPORTS / "missing_values_before.csv")

# Remove exact repeated rows across all original columns.
df = raw.drop_duplicates().copy()

# Standardize identifiers and text without inventing customer IDs.
for column in ["InvoiceNo", "StockCode", "Description", "Country"]:
    df[column] = df[column].astype("string").str.strip()
    df[column] = df[column].replace("", pd.NA)

df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
)
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
df["CustomerID"] = pd.to_numeric(
    df["CustomerID"], errors="coerce"
).astype("Int64")

# Keep missing customer IDs. Exclude them only from customer counts.
df["CustomerKnown"] = df["CustomerID"].notna()
df["Description"] = df["Description"].fillna("Unknown product")
df["Country"] = df["Country"].fillna("Unknown")

# Separate unusable records from valid transaction records.
invalid = (
    df["InvoiceNo"].isna()
    | df["StockCode"].isna()
    | df["InvoiceDate"].isna()
    | df["Quantity"].isna()
    | df["UnitPrice"].isna()
    | df["Quantity"].eq(0)
    | df["UnitPrice"].le(0)
)

excluded = df.loc[invalid].copy()
valid = df.loc[~invalid].copy()

# Cancellation invoices and negative quantities are kept separately.
is_return = (
    valid["InvoiceNo"].str.upper().str.startswith("C", na=False)
    | valid["Quantity"].lt(0)
)

returns = valid.loc[is_return].copy()
sales = valid.loc[~is_return].copy()

# Revenue here means positive sales before returns, not net revenue.
sales["Revenue"] = (
    sales["Quantity"] * sales["UnitPrice"]
).round(2)
sales["Month"] = sales["InvoiceDate"].dt.strftime("%Y-%m")

sales.to_csv(DATA / "clean_sales.csv", index=False)
returns.to_csv(DATA / "returns_cancellations.csv", index=False)
excluded.to_csv(DATA / "excluded_records.csv", index=False)

sales.head(20).to_csv(REPORTS / "after_cleaning.csv", index=False)
sales.isna().sum().to_csv(REPORTS / "missing_values_after.csv")

summary = pd.Series({
    "Original rows": len(raw),
    "Exact duplicates removed": len(raw) - len(df),
    "Excluded invalid/nonpositive-price rows": len(excluded),
    "Return/cancellation rows": len(returns),
    "Positive sales rows": len(sales),
    "Sales rows missing CustomerID": sales["CustomerID"].isna().sum()
})

summary.to_csv(REPORTS / "cleaning_summary.csv", header=["Count"])

assert len(df) == len(excluded) + len(returns) + len(sales)

print("\nCLEANING SUMMARY")
print(summary.to_string())

print("\nSALES BEFORE RETURNS (GBP)")
print(f"{sales['Revenue'].sum():,.2f}")

print("\nFiles saved in data and reports folders.")