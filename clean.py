import pandas as pd
from sklearn.neighbors import LocalOutlierFactor

def filter_latency_outliers(input_csv, output_csv):
    # Ensure the latency file exists
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"\nError: The file '{input_csv}' was not found. Could not clean the latency data.")
        return
    
    # Ensure the 'Latency' column exists
    if 'Latency' not in df.columns:
        raise ValueError("The dataset must contain a 'Latency' column.")

    # Reshape the Latency column for LOF algorithm
    X = df[['Latency']].values

    # Initialize the LOF model
    lof = LocalOutlierFactor(n_neighbors=100, contamination=0.1, n_jobs=-1)

    # Fit the model and predict labels: 1 for inliers, -1 for outliers
    df['Anomaly_Tag'] = lof.fit_predict(X)

    # Remove the outlier rows and the Anomaly_Tag column
    df_clean = df[df['Anomaly_Tag'] == 1].drop(columns=['Anomaly_Tag'])

    # Save the filtered results to a new CSV file
    df_clean.to_csv(output_csv, index=False)

    # Print summary metrics
    total_rows = len(df)
    clean_rows = len(df_clean)
    outliers_removed = total_rows - clean_rows
    print("\nOutlier Removal Summary:")
    print(f"Total benchmark latencies: {total_rows}")
    print(f"Cleaned latencies: {clean_rows}")
    print(f"Outliers successfully removed: {outliers_removed}")

if __name__ == "__main__":
    input_file = "data/access_times.csv"
    output_file = "data/cleaned_access_times.csv"
    # Execute the outlier filtering
    filter_latency_outliers(input_file, output_file)