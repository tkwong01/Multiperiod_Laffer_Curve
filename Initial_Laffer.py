### Part 1: Convert from Wide to Long
import os
from pathlib import Path
import numpy as np
import pandas as pd

# File paths
world_bank_data = "/Users/tkwong01/Desktop/LafferCurve/P_Data_Extract_From_World_Development_Indicators-6/ec94fcfc-30e1-436e-b7cb-c6dc601b8881_Data.csv"
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




### Part 2: Plot
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. Load the cleaned data
output_file_path = output_dir / "Long_Data.csv"
df_final = pd.read_csv(output_file_path)

# 2. USER SPECIFICATION: Define your 3 variables here
# 'x_var' must be 'Year'. 
# 'y_var' and 'z_var' should be columns (Series Names) present in your Long_Data.csv
x_var = "Year"
y_var = "Tax revenue (% of GDP)"  # <-- Replace with your second variable
z_var = "Revenue, excluding grants (% of GDP)"  # <-- Replace with your third variable (acts as "elevation")

# [Optional] Filter for a specific country if your dataset contains many countries
# country_to_plot = "United States"
# df_plot = df_final[df_final["Country Name"] == country_to_plot].dropna(subset=[x_var, y_var, z_var])

# Drop missing values across the three specified variables to ensure clean plotting
df_plot = df_final.dropna(subset=[x_var, y_var, z_var])

# ---------------------------------------------------------
# OPTION A: 3D Topographic Surface Plot
# ---------------------------------------------------------
# Create a 3D subplot (using subplots to avoid .figure() call)
fig_3d, ax_3d = plt.subplots(
    subplot_kw={"projection": "3d"}, figsize=(11, 8)
)

# Plot the surface using triangulation ('terrain' or 'viridis' colormaps work great for topography)
surf = ax_3d.plot_trisurf(
    df_plot[x_var],
    df_plot[y_var],
    df_plot[z_var],
    cmap="terrain",
    edgecolor="none",
    antialiased=True,
)

# Add labels and titles with padding to ensure they don't overlap
ax_3d.set_xlabel(x_var, fontsize=10, labelpad=10)
ax_3d.set_ylabel(y_var, fontsize=10, labelpad=10)
ax_3d.set_zlabel(z_var, fontsize=10, labelpad=10)
ax_3d.set_title(
    f"3D Topographic Surface\n{z_var} vs {x_var} and {y_var}",
    fontsize=12,
    pad=20,
)

# Add a color bar indicating the "elevation" (Z-variable intensity)
fig_3d.colorbar(surf, ax=ax_3d, shrink=0.6, aspect=12, pad=0.1)

plt.tight_layout()
output_plot_3d = output_dir / "topography_3d_surface.png"
plt.savefig(output_plot_3d, dpi=300)
print(f"3D Surface plot saved to '{output_plot_3d}'!")


# ---------------------------------------------------------
# OPTION B: 2D Topographic Contour Map (Traditional Map Look)
# ---------------------------------------------------------
fig_2d, ax_2d = plt.subplots(figsize=(10, 8))

# Create filled contour levels representing topographic elevation
contour = ax_2d.tricontourf(
    df_plot[x_var], df_plot[y_var], df_plot[z_var], levels=20, cmap="terrain"
)

# Add contour lines to enhance the topographic appearance
lines = ax_2d.tricontour(
    df_plot[x_var],
    df_plot[y_var],
    df_plot[z_var],
    levels=20,
    colors="black",
    linewidths=0.5,
    alpha=0.5,
)

# Add labels, titles, and colorbar
ax_2d.set_xlabel(x_var, fontsize=11)
ax_2d.set_ylabel(y_var, fontsize=11)
ax_2d.set_title(
    f"2D Topographic Contour Map of {z_var}", fontsize=13, pad=15
)
fig_2d.colorbar(contour, ax=ax_2d, label=z_var)

plt.tight_layout()
output_plot_2d = output_dir / "topography_2d_contour.png"
plt.savefig(output_plot_2d, dpi=300)
print(f"2D Contour map saved to '{output_plot_2d}'!")
