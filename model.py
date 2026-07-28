import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Load data
df = pd.read_csv('data/cleaned_access_times.csv')
X = df[['Latency']].values
X_log = np.log10(X)

optimal_n = 4

# Create and fit the K-Means model
kmeans = KMeans(n_clusters=optimal_n, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(X_log)

# Extract detailed physical boundaries of each cluster in linear nanoseconds
cluster_stats = []
for i in range(optimal_n):
    c_data = df[df['Cluster'] == i]['Latency']
    if len(c_data) > 0:
        cluster_stats.append({
            'cluster_id': i,
            'mean': c_data.mean(),
            'min': c_data.min(),
            'max': c_data.max(),
            'weight': len(c_data) / len(df)
        })

# Sort clusters by minimum latency to guarantee correct physical ordering (L1 -> L2 -> SLC -> DRAM)
cluster_stats = sorted(cluster_stats, key=lambda x: x['min'])

# Assign explicit Hardware Tier Labels based on physical speed hierarchy
hardware_tiers = ["L1 Cache", "L2 Cache", "SLC", "DRAM"]

# Dynamic Hardware-Independent Labeling (Empty Space Detection)
significant_clusters = [c for c in cluster_stats if c['weight'] > 0.03]

max_empty_space = 0
split_threshold = 0

for i in range(len(significant_clusters) - 1):
    current_cluster = significant_clusters[i]
    next_cluster = significant_clusters[i+1]
    
    empty_space = next_cluster['min'] - current_cluster['max']
    
    if empty_space > max_empty_space:
        max_empty_space = empty_space
        split_threshold = current_cluster['max'] + (empty_space / 2)

# Apply mappings
persistence_mapping = {}
hardware_mapping = {}

for idx, c in enumerate(cluster_stats):
    tier_name = hardware_tiers[idx]
    status = "CACHED (VOLATILE)" if c['mean'] < split_threshold else "PERSISTED"
    
    c['tier_name'] = tier_name
    c['status'] = status
    
    hardware_mapping[c['cluster_id']] = tier_name
    persistence_mapping[c['cluster_id']] = status

# Save both mappings in the payload
model_payload = {
    'model': kmeans,
    'cluster_mapping': persistence_mapping, # Used by infer.py for binary accuracy
    'hardware_mapping': hardware_mapping # Used for explicit hardware tiering
}
os.makedirs('models', exist_ok=True)
joblib.dump(model_payload, 'models/persistence_model.pkl')

for c in cluster_stats:
    print(f"Cluster {c['cluster_id']} [{c['tier_name']} | {c['status']}]: Mean = {c['mean']:.2f} ns | Weight = {c['weight']:.2%}")

# Generate a plot visualising the clusters
plt.figure(figsize=(10, 6))

palette = sns.color_palette('viridis', optimal_n)

# Add vertical colour bands to highlight cluster regions based on physical min/max
for idx, c in enumerate(cluster_stats):
    plt.axvspan(
        c['min'],
        c['max'],
        alpha=0.15,
        color=palette[idx]
    )

# Create scatter plot of each memory access instance
for idx, c in enumerate(cluster_stats):
    cluster_data = df[df['Cluster'] == c['cluster_id']]
    
    plt.scatter(
        cluster_data['Latency'],
        cluster_data.index,
        s=10,
        color=palette[idx],
        label=f"{c['tier_name']} (Cluster {c['cluster_id']}) [{c['status']}]",
        alpha=0.7
    )

# Force x-axis to render logarithmically
plt.xscale('log')

plt.title('Memory Access Latency Clusters by Hardware Tier (K-Means)')
plt.xlabel('Latency (ns) [Logarithmic Scale]')
plt.ylabel('Access Instance')

plt.legend()

os.makedirs('plots', exist_ok=True)
plt.savefig('plots/clusters.png', bbox_inches='tight')
plt.close()
print("\nPlot successfully saved to 'plots/clusters.png'.")