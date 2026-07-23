import os
import pandas as pd
import numpy as np
from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Load data
df = pd.read_csv('data/cleaned_access_times.csv')
X = df[['Latency']].values

# Determine optimal number of components using BIC (testing 1 to 5 components)
bics = []
n_components_range = range(1, 6)
for n in n_components_range:
    gmm = GaussianMixture(n_components=n, random_state=42)
    gmm.fit(X)
    bics.append(gmm.bic(X))
optimal_n = n_components_range[np.argmin(bics)]
print(f"\nOptimal number of clusters based on BIC: {optimal_n}")

# Create the model
gmm = GaussianMixture(n_components=optimal_n, random_state=42, n_init=5)

# Fit the model and assign clusters to the data
df['Cluster'] = gmm.fit_predict(X)

# Dynamic Hardware-Independent Labeling via Cumulative Weight Splitting
cluster_info = []
for i in range(optimal_n):
    cluster_info.append({
        'cluster_id': i,
        'mean': gmm.means_[i][0],
        'weight': gmm.weights_[i]
    })

# Sort clusters by mean latency in ascending order
cluster_info = sorted(cluster_info, key=lambda x: x['mean'])

# Mark the boundary where cumulative execution probability crosses 55%
cumulative_weight = 0.0
mapping = {}
for c in cluster_info:
    cumulative_weight += c['weight']
    if cumulative_weight <= 0.55:
        mapping[c['cluster_id']] = "CACHED (VOLATILE)"
    else:
        mapping[c['cluster_id']] = "PERSISTED"

# Save the cluster mapping definition along with the model
model_payload = {
    'gmm_model': gmm,
    'cluster_mapping': mapping
}
os.makedirs('models', exist_ok=True)
joblib.dump(model_payload, 'models/persistence_model.pkl')

print("\n--- Latency Cluster Profiles ---")
for c in cluster_info:
    status = mapping[c['cluster_id']]
    print(f"Cluster {c['cluster_id']} [{status}]: Mean = {c['mean']:.2f} ns | Weight = {c['weight']:.2%}")

plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='Latency', hue='Cluster', palette='viridis', bins=50, kde=True)
plt.title('Memory Access Latency Clusters (GMM)')
plt.xlabel('Latency (ns)')
plt.ylabel('Frequency')

os.makedirs('plots', exist_ok=True)
plt.savefig('plots/clusters.png', bbox_inches='tight')
plt.close()
print("\nPlot successfully saved to 'plots/clusters.png'.")