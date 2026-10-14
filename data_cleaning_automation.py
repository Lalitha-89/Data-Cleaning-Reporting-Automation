
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Find the project folder
folder = Path(__file__).resolve().parent

# Load sales data
df = pd.read_csv(folder / "sales_data.csv")

print("Original dataset:")
print(df)

# Count data problems
original_rows = len(df)
duplicates = int(df.duplicated().sum())
missing_values = int(df.isnull().sum().sum())

# Remove duplicate rows
df = df.drop_duplicates().copy()

# Clean text columns
for col in ["Customer", "Product", "City"]:
    df[col] = df[col].apply(
        lambda x: x.strip() if isinstance(x, str) else x
    )
    df[col] = df[col].replace("", pd.NA)

# Correct data types
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

# Fill missing values
df["Quantity"] = df["Quantity"].fillna(df["Quantity"].median())
df["City"] = df["City"].fillna("Unknown")

# Standardize text
df["Customer"] = df["Customer"].str.title()
df["Product"] = df["Product"].str.title()
df["City"] = df["City"].str.title()

# Convert dates
df["OrderDate"] = pd.to_datetime(df["OrderDate"], errors="coerce")

# Remove rows with essential information missing
df = df.dropna(
    subset=["OrderID", "Customer", "Product", "Price", "OrderDate"]
).copy()

# Calculate revenue
df["Revenue"] = df["Quantity"] * df["Price"]

# Save cleaned data
df.to_csv(folder / "cleaned_sales_data.csv", index=False)

# Create summaries
product_summary = df.groupby("Product", as_index=False).agg(
    Total_Quantity=("Quantity", "sum"),
    Total_Revenue=("Revenue", "sum")
).sort_values("Total_Revenue", ascending=False)

summary = pd.DataFrame({
    "Metric": [
        "Original Rows",
        "Duplicate Rows Removed",
        "Missing Values Before Cleaning",
        "Final Rows",
        "Total Revenue"
    ],
    "Value": [
        original_rows,
        duplicates,
        missing_values,
        len(df),
        round(df["Revenue"].sum(), 2)
    ]
})

city_summary = df.groupby("City", as_index=False).agg(
    Total_Revenue=("Revenue", "sum")
)

# Generate Excel report
with pd.ExcelWriter(folder / "cleaning_report.xlsx") as writer:
    df.to_excel(writer, sheet_name="Cleaned Data", index=False)
    summary.to_excel(writer, sheet_name="Summary", index=False)
    product_summary.to_excel(writer, sheet_name="Product Analysis", index=False)
    city_summary.to_excel(writer, sheet_name="City Analysis", index=False)

# Create chart
plt.figure(figsize=(9, 5))
plt.bar(product_summary["Product"], product_summary["Total_Revenue"])
plt.title("Total Revenue by Product")
plt.xlabel("Product")
plt.ylabel("Revenue (Rs.)")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(folder / "sales_summary.png", dpi=300)
plt.close()

print("\nDATA CLEANING COMPLETED SUCCESSFULLY!")
print("Original rows:", original_rows)
print("Duplicates removed:", duplicates)
print("Missing values found:", missing_values)
print("Final rows:", len(df))
print("Total revenue: Rs.", round(df["Revenue"].sum(), 2))
print("\nGenerated files:")
print("cleaned_sales_data.csv")
print("cleaning_report.xlsx")
print("sales_summary.png")
