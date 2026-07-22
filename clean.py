import pandas as pd
from sklearn.neighbors import LocalOutlierFactor

def filter_latency_outliers(input_csv, output_csv, contamination=0.02, n_neighbors=20):
    """
    Filters outliers from the benchmark timing dataset using Local Outlier Factor (LOF).
    
    Parameters:
    - input_csv (str): Path to the source CSV file containing 'Latency' values.
    - output_csv (str): Path where the cleaned CSV will be saved.
    - contamination (float): The proportion of outliers expected in the dataset (e.g., 0.02 for 2%).
    - n_neighbors (int): Number of neighbors to use for local density evaluation.
    """
    try:
        # Load the benchmark data using pandas
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: The file '{input_csv}' was not found.")
        return None

    # Ensure the 'Latency' column exists
    if 'Latency' not in df.columns:
        raise ValueError("The dataset must contain a 'Latency' column.")

    # LOF expects a 2D array-like input, so we extract and reshape the Latency column
    X = df[['Latency']].values

    # Initialize the LOF model
    # - contamination specifies the expected fraction of anomalous timing anomalies (e.g., system noise)
    # - n_neighbors determines the neighborhood size for density estimation
    lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)

    # Fit the model and predict labels: 1 for inliers, -1 for outliers
    df['Anomaly_Tag'] = lof.fit_predict(X)

    # Separate the clean records from the anomalies
    df_clean = df[df['Anomaly_Tag'] == 1].drop(columns=['Anomaly_Tag'])
    df_outliers = df[df['Anomaly_Tag'] == -1]

    # Save the filtered results to a new CSV file
    df_clean.to_csv(output_csv, index=False)

    # Summary metrics
    total_points = len(df)
    clean_points = len(df_clean)
    outliers_removed = total_points - clean_points

    print("=== Outlier Removal Summary ===")
    print(f"Total benchmark iterations: {total_points}")
    print(f"Cleaned observations saved: {clean_points}")
    print(f"Outliers successfully removed: {outliers_removed} ({contamination * 100:.1f}%)")
    print("\n--- Cleaned Latency Statistics ---")
    print(df_clean['Latency'].describe())
    
    return df_clean

if __name__ == "__main__":
    # Specify files using relative paths
    input_file = "data/access_times.csv"
    output_file = "data/cleaned_access_times.csv"
    
    # Execute the filtering
    filter_latency_outliers(input_file, output_file, contamination=0.01, n_neighbors=20)