import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Generates and saves plots to visualise the latency data
def generate_plots(csv_file, plot_prefix):
    # Load data
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"\nError: '{csv_file}' not found. NOT generating plots for {csv_file}.")
        return
    
    print(f"Generating plots for '{csv_file}'...")

    # Ensure the required columns exist
    if 'Array_Size_Bytes' not in df.columns or 'Latency' not in df.columns:
        print(f"Error: Required columns 'Array_Size_Bytes' and 'Latency' not found in {csv_file}.")
        return

    # Extract data from columns
    array_sizes = df['Array_Size_Bytes']
    latencies = df['Latency']
    access_instance = np.arange(len(df))

    # Compute latency means for each array size
    means = df.groupby('Array_Size_Bytes')['Latency'].mean().reset_index()

    # Plot 1: Scatter Plot - Latency vs Array Size
    plt.clf()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(array_sizes, latencies, s=8, alpha=0.4)
    ax.plot(means['Array_Size_Bytes'], means['Latency'], color='red', linewidth=2, marker='o', label='Average Latency')
    ax.set_xscale('log', base=2)
    ax.set_yscale('log')
    ax.set_xlabel('Array Size (Bytes) [Log₂ Scale]')
    ax.set_ylabel('Latency (ns) [Log₁₀ Scale]')
    ax.set_title(f'Scatter Plot: Latency vs Array Size ({plot_prefix})')
    ax.legend()
    ax.grid(True, which="both", ls="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'plots/{plot_prefix}_scatter_latency_vs_size.png', dpi=300)
    plt.close()

    # Plot 2: Scatter Plot - Latency vs Access Instance
    plt.clf()
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(latencies, access_instance, s=8, alpha=0.4)
    ax.set_xscale('log')
    ax.set_xlabel('Latency (ns) [Log₁₀ Scale]')
    ax.set_ylabel('Access Instance')
    ax.set_title(f'Scatter Plot: Latency vs Access Instance ({plot_prefix})')
    ax.grid(True, which="both", ls="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'plots/{plot_prefix}_scatter_latency_vs_access.png', dpi=300)
    plt.close()

if __name__ == "__main__":
    # Generate plots using the latency data
    generate_plots("data/cleaned_access_times.csv", "cleaned")
    generate_plots("data/access_times.csv", "raw")
    print("Plots saved in 'plots/'.")