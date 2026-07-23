import pandas as pd
import joblib

# Load the inference model package
payload = joblib.load('models/persistence_model.pkl')
gmm = payload['gmm_model']
mapping = payload['cluster_mapping']

# Load experimental verification data
test_df = pd.read_csv('data/test_latencies.csv')
X_test = test_df[['Latency']].values

# Predict clusters
test_df['Predicted_Cluster'] = gmm.predict(X_test)
test_df['Inferred_Status'] = test_df['Predicted_Cluster'].map(mapping)

correct_predictions = (test_df['Inferred_Status'] == test_df['Ground_Truth']).sum()
accuracy = (correct_predictions / len(test_df)) * 100

print("\n=== Persistence Inference Engine ===")
print(f"Model Accuracy on new writes: {accuracy:.2f}% ({correct_predictions}/{len(test_df)} correct)\n")

print("--- Sample Inference Results ---")
print(f"{'Latency':<10} | {'Ground_Truth':<20} | {'Inferred_Status':<20}")
print("-" * 55)
for idx, row in test_df.head(15).iterrows():
    print(f"{row['Latency']:<10} | {row['Ground_Truth']:<20} | {row['Inferred_Status']:<20}")