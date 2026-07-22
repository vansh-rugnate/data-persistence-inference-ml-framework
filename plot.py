import pandas as pd
import matplotlib.pyplot as plt
import os

# Ensure plots directory exists
os.makedirs('plots', exist_ok=True)


def generate_plots(csv_file, plot_prefix):
    # Load dataset
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: '{csv_file}' not found. Skipping...")
        return

    print(f"\nProcessing {csv_file}")

    # Automatically identify the latency column
    latency_col = [col for col in df.columns if 'latency' in col.lower()]

    if latency_col:
        latency_data = df[latency_col[0]]
        print(f"Using column '{latency_col[0]}' for latency data.")
    else:
        latency_data = df.iloc[:, 0]
        print(f"No column containing 'latency' found. Defaulting to first column: '{df.columns[0]}'")

    # X-axis is access instance (row number)
    access_instance = df.index

    # --- Plot A: Scatter Plot ---
    plt.clf()

    plt.scatter(
        access_instance,
        latency_data,
        alpha=0.6,
        s=1,
        color='blue'
    )

    plt.yscale('log')

    plt.xlabel('Access Instance (Row Number)')
    plt.ylabel('Latency (ns)')
    plt.title(f'Plot A: Latency vs. Access Instance ({plot_prefix})')
    plt.grid(True, which="both", ls="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(f'plots/{plot_prefix}_plot_a.png', dpi=300)
    plt.clf()

    # --- Plot B: Histogram ---
    plt.hist(
        latency_data,
        bins=200,
        alpha=0.75,
        color='orange',
        edgecolor='black',
        log=True
    )

    plt.xlabel('Latency (ns)')
    plt.ylabel('Frequency (Log Scale)')
    plt.title(f'Plot B: Histogram of Latencies ({plot_prefix})')
    plt.grid(True, which="both", ls="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(f'plots/{plot_prefix}_plot_b.png', dpi=300)
    plt.clf()

    print(f"Saved {plot_prefix} plots successfully.")


# Generate plots for cleaned dataset
generate_plots(
    'data/cleaned_access_times.csv',
    'cleaned_access_times'
)

# Generate plots for uncleaned dataset
generate_plots(
    'data/access_times.csv',
    'raw_access_times'
)

print("\nAll plots generated successfully in plots/.")

"""
import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the dataset
try:
    df = pd.read_csv('data/cleaned_access_times.csv')
except FileNotFoundError:
    print("Error: 'cleaned_access_times.csv' not found. Please ensure the file is in the working directory.")
    exit(1)

# Automatically identify the latency column
latency_col = [col for col in df.columns if 'latency' in col.lower()]
if latency_col:
    latency_data = df[latency_col[0]]
    print(f"Using column '{latency_col[0]}' for latency data.")
else:
    latency_data = df.iloc[:, 0]
    print(f"No column containing 'latency' found. Defaulting to the first column: '{df.columns[0]}'")

# The X-axis for Plot A is the access instance (just the row number / index)
access_instance = df.index

# --- Plot A: Scatter Plot ---
plt.clf()  # Ensure a clean slate without using plt.figure()

# Create the scatter plot (using a small marker size 's' and alpha for density clarity)
plt.scatter(access_instance, latency_data, alpha=0.6, s=1, color='blue')

# Set Y-axis to a logarithmic scale as required
plt.yscale('log')

# Labels and titles
plt.xlabel('Access Instance (Row Number)')
plt.ylabel('Latency (ns)')
plt.title('Plot A: Latency vs. Access Instance')
plt.grid(True, which="both", ls="--", alpha=0.5)

# Save Plot A ensuring labels are not truncated or overlapping
plt.tight_layout()
plt.savefig('plots/plot_a.png', dpi=300)
plt.clf()

# --- Plot B: Histogram ---
# Using a high number of bins (e.g., 200) allows distinct spikes to show up.
# Setting log=True for the frequency axis prevents the massive L1/L2 peaks from completely hiding the RAM peaks.
plt.hist(latency_data, bins=200, alpha=0.75, color='orange', edgecolor='black', log=True)

# Labels and titles
plt.xlabel('Latency (ns)')
plt.ylabel('Frequency (Log Scale)')
plt.title('Plot B: Histogram of Latencies (Cache & RAM Peaks)')
plt.grid(True, which="both", ls="--", alpha=0.5)

# Save Plot B ensuring labels are not truncated or overlapping
plt.tight_layout()
plt.savefig('plots/plot_b.png', dpi=300)
plt.clf()

print("Plots saved successfully in plots/ as 'plot_a.png' and 'plot_b.png'.")
"""