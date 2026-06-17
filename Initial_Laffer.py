# Part 1
import os
from pathlib import Path
import numpy as np
import pandas as pd

# File paths
world_bank_data = "/Users/tkwong01/Desktop/LafferCurve/DataBank_Data/02ab50f0-5eb0-409c-b700-1a9dbed2df10_Data.csv"
output_dir = Path("output")
results_dir = output_dir / "results"

# Create directories natively in Python if they don't exist
output_dir.mkdir(parents=True, exist_ok=True)
results_dir.mkdir(parents=True, exist_ok=True)

# 1. Load your downloaded CSV file
df = pd.read_csv(world_bank_data)

# FIX 1: Drop the World Bank footer metadata rows
df = df.dropna(subset=["Series Code"])

# 2. Unpivot the year columns into a single 'Year' column
id_vars = ["Country Name", "Country Code", "Series Name", "Series Code"]
df_long = df.melt(id_vars=id_vars, var_name="Year", value_name="Value")

# FIX 2: Clean up the 'Year' column (extracts just the 4 digits and turns them into integers)
df_long["Year"] = df_long["Year"].str.extract(r"(\d{4})").astype(int)

# FIX 3: Convert the values to numeric BEFORE pivoting
df_long["Value"] = pd.to_numeric(
    df_long["Value"].replace("..", np.nan), errors="coerce"
)

# 3. Pivot the 'Series Name' so each indicator gets its own column
df_final = df_long.pivot_table(
    index=["Country Name", "Country Code", "Year"],
    columns="Series Name",
    values="Value",
    aggfunc="first",
).reset_index()

# Clean up the column index name header left over from pivoting
df_final.columns.name = None

# Save your clean data directly into the 'output' directory
output_file_path = output_dir / "Long_Data.csv"
df_final.to_csv(output_file_path, index=False)

print(f"Data successfully cleaned and saved to '{output_file_path}'!")
