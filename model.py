import os
import pandas as pd
import numpy as np
from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load the cleaned data
df = pd.read_csv('data/cleaned_access_times.csv')
X = df[['Latency']].values

# 2. Determine optimal number of components using BIC (testing 1 to 5 components)
bics = []
n_components_range = range(1, 6)
for n in n_components_range:
    gmm = GaussianMixture(n_components=n, random_state=42)
    gmm.fit(X)
    bics.append(gmm.bic(X))

optimal_n = n_components_range[np.argmin(bics)]
print(f"Optimal number of clusters based on BIC: {optimal_n}")

# 3. Fit the model with the optimal components
gmm = GaussianMixture(n_components=optimal_n, random_state=42)
df['Cluster'] = gmm.fit_predict(X)

# 4. Print Summary Statistics
print("\n--- Latency Cluster Profiles ---")
for i in range(optimal_n):
    cluster_data = df[df['Cluster'] == i]['Latency']
    print(f"Cluster {i}: Mean = {gmm.means_[i][0]:.2f} ns | Weight = {gmm.weights_[i]:.2%} | Count = {len(cluster_data)}")

# 5. Visualize and Save the Clusters
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='Latency', hue='Cluster', palette='viridis', bins=50, kde=True)
plt.title('Memory Access Latency Clusters (GMM)')
plt.xlabel('Latency (ns)')
plt.ylabel('Frequency')

# Create the plots directory if it doesn't exist, then save the file
os.makedirs('plots', exist_ok=True)
plt.savefig('plots/clusters.png', bbox_inches='tight')
plt.close()

print("\nPlot successfully saved to plots/clusters.png")
