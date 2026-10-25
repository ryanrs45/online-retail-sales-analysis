from pathlib import Path
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
CHARTS = ROOT / "visualizations"

REPORTS.mkdir(exist_ok=True)
CHARTS.mkdir(exist_ok=True)

df = pd.read_csv(
    ROOT / "data" / "clean_sales.csv",
    dtype={
        "InvoiceNo": "string",
        "StockCode": "string",
        "CustomerID": "string"
    },
    parse_dates=["InvoiceDate"]
)

sns.set_theme(style="whitegrid")


def save_chart(filename):
    plt.tight_layout()
    plt.savefig(CHARTS / filename, dpi=180, bbox_inches="tight")
    plt.close()


# Descriptive statistics.
numeric = ["Quantity", "UnitPrice", "Revenue"]
df[numeric].describe().to_csv(REPORTS / "descriptive_statistics.csv")

# Correlation uses measured values, not numeric customer/order IDs.
correlation = df[numeric].corr()
correlation.to_csv(REPORTS / "correlation.csv")

# Flag potential outliers without automatically deleting them.
q1 = df["Revenue"].quantile(0.25)
q3 = df["Revenue"].quantile(0.75)
iqr = q3 - q1
lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr

outliers = df[
    (df["Revenue"] < lower) | (df["Revenue"] > upper)
]
outliers.to_csv(REPORTS / "revenue_outliers.csv", index=False)

# Summary tables.
monthly = df.groupby("Month")["Revenue"].sum().sort_index()
countries = df.groupby("Country")["Revenue"].sum().sort_values(
    ascending=False
)
products = df.groupby("StockCode")["Revenue"].sum().sort_values(
    ascending=False
)
orders = df.groupby("InvoiceNo")["Revenue"].sum()

monthly.to_csv(REPORTS / "monthly_sales.csv")
countries.to_csv(REPORTS / "country_sales.csv")
products.to_csv(REPORTS / "product_sales.csv")

# 1. Monthly sales.
plt.figure(figsize=(11, 5))
monthly.plot(marker="o")
plt.title("Monthly Sales Before Returns (GBP)")
plt.xlabel("Month")
plt.ylabel("Sales (GBP)")
plt.xticks(rotation=45)
save_chart("01_monthly_sales.png")

# 2. Top countries.
plt.figure(figsize=(10, 6))
countries.head(10).sort_values().plot.barh()
plt.title("Top 10 Countries by Sales Before Returns")
plt.xlabel("Sales (GBP)")
plt.ylabel("Country")
save_chart("02_top_countries.png")

# 3. Top products, grouped by stable product code.
plt.figure(figsize=(10, 6))
products.head(10).sort_values().plot.barh()
plt.title("Top 10 Product Codes by Sales Before Returns")
plt.xlabel("Sales (GBP)")
plt.ylabel("Product code")
save_chart("03_top_products.png")

# 4. Distribution: logarithmic scale preserves large orders.
plt.figure(figsize=(10, 5))
sns.histplot(orders, bins=50, log_scale=True)
plt.title("Distribution of Order Sales Before Returns")
plt.xlabel("Order sales (GBP, logarithmic scale)")
plt.ylabel("Number of orders")
save_chart("04_order_distribution.png")

# 5. Correlation heatmap.
plt.figure(figsize=(7, 5))
sns.heatmap(correlation, annot=True, fmt=".3f", cmap="coolwarm",
            vmin=-1, vmax=1)
plt.title("Correlation of Sales-Line Numerical Variables")
save_chart("05_correlation.png")

# 6. Outlier visualization.
plt.figure(figsize=(10, 4))
sns.boxplot(x=df["Revenue"])
plt.xscale("log")
plt.title("Sales-Line Revenue Spread and Potential Outliers")
plt.xlabel("Revenue (GBP, logarithmic scale)")
save_chart("06_revenue_boxplot.png")

total = df["Revenue"].sum()
uk_share = countries.get("United Kingdom", 0) / total * 100

print("\nEDA RESULTS")
print(f"Sales before returns: GBP {total:,.2f}")
print(f"Distinct sales invoices: {df['InvoiceNo'].nunique():,}")
print(f"Known customers: {df['CustomerID'].nunique():,}")
print(f"Average sales per invoice: GBP {orders.mean():,.2f}")
print(f"UK share of sales: {uk_share:.2f}%")
print(f"Highest-sales month: {monthly.idxmax()}")
print(f"Top product code: {products.index[0]}")
print(f"IQR upper threshold: GBP {upper:.2f}")
print(f"Potential outlier rows: {len(outliers):,}")
print("\nSix charts saved in visualizations.")
print("Statistics and summary tables saved in reports.")
print("\nNote: December 2011 ends on 9 December and is incomplete.")
print("Revenue correlations partly reflect Quantity × UnitPrice.")