import pandas as pd
import numpy as np
import joblib

# Load payload
payload = joblib.load('models/persistence_model.pkl')
model = payload['model']
persistence_mapping = payload['cluster_mapping']
hardware_mapping = payload['hardware_mapping']

# Load test data
test_df = pd.read_csv('data/test_latencies.csv')

# Transform linear latency test data to logarithmic
X_test_log = np.log10(test_df[['Latency']].values)

# Predict test data clusters
test_df['Predicted_Cluster'] = model.predict(X_test_log)

# Apply hardware tier mapping and persistence mapping to test data clusters
test_df['Inferred_Tier'] = test_df['Predicted_Cluster'].map(hardware_mapping)
test_df['Inferred_Status'] = test_df['Predicted_Cluster'].map(persistence_mapping)

# Calculate model accuracy
correct_predictions = (test_df['Inferred_Status'] == test_df['Ground_Truth']).sum()
accuracy = (correct_predictions / len(test_df)) * 100
print(f"Model Accuracy on new writes: {accuracy:.2f}% ({correct_predictions}/{len(test_df)} correct)")

print(f"{'Latency':<10} | {'Ground_Truth':<20} | {'Inferred_Tier':<12} | {'Inferred_Status':<20}")
print("-" * 72)
for idx, row in test_df.head(15).iterrows():
    print(f"{row['Latency']:<10} | {row['Ground_Truth']:<20} | {row['Inferred_Tier']:<12} | {row['Inferred_Status']:<20}")