import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_plots(csv_file, plot_prefix):
    # Load dataset
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"\nError: '{csv_file}' not found. NOT generating plots for {csv_file}.")
        return

    print(f"\nGenerating plots for '{csv_file}'...")

    # Extract the latency data column
    latency_data = df['Latency']

    # Extract the access instance (row number)
    access_instance = df.index

    # Generate a Scatter Plot
    plt.clf()
    plt.scatter(
        latency_data,
        access_instance,
        alpha=0.6,
        s=1,
        color='blue'
    )
    plt.xscale('log')
    plt.xlabel('Latency (ns) [Log Scale]')
    plt.ylabel('Access Instance')
    plt.title(f'Scatter Plot: Access Instance vs. Latency ({plot_prefix})')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f'plots/{plot_prefix}_scatter_plot.png', dpi=300)
    plt.clf()

    # Generate a Histogram
    # Create log-spaced bins for the X-axis based on data min/max
    min_val = max(1, latency_data.min()) # Prevent log(0) errors
    max_val = latency_data.max()
    log_bins = np.logspace(np.log10(min_val), np.log10(max_val), 200)

    plt.hist(
        latency_data,
        bins=log_bins,
        alpha=0.75,
        color='orange',
        edgecolor='black',
        log=True
    )
    plt.xscale('log')
    plt.xlabel('Latency (ns) [Log Scale]')
    plt.ylabel('Frequency [Log Scale]')
    plt.title(f'Histogram: Frequency vs Latency ({plot_prefix})')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f'plots/{plot_prefix}_histogram.png', dpi=300)
    plt.clf()

    print(f"Saved {plot_prefix} plots successfully.")


# Generate plots for cleaned dataset
generate_plots("data/cleaned_access_times.csv", "cleaned_access_times")

# Generate plots for uncleaned dataset
generate_plots("data/access_times.csv", "raw_access_times")

print("\nAll plots saved successfully in 'plots/'.")