import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from hmmlearn.hmm import GaussianHMM

def PCA(filename, n_components, print_components=False):

    # Read data while preserving dates
    data = pd.read_csv(filename, index_col=0)

    # Convert dates to datetime
    dates = pd.to_datetime(data.index)

    # Get stock return data
    data_wo_names = data.to_numpy(dtype=np.float64)
    ticker_names = data.columns.to_numpy()

    # Standardize each stock
    mean = np.mean(data_wo_names, axis=0)
    std_dev = np.std(data_wo_names, axis=0)

    data_std = (data_wo_names - mean) / std_dev

    # Calculate covariance matrix
    cov_matrix = np.cov(data_std.T)

    # Eigendecomposition
    values, vectors = np.linalg.eigh(cov_matrix)

    # Sort eigenvalues from largest to smallest
    sorted_indices = np.argsort(values)[::-1]

    values_sorted = values[sorted_indices]
    vectors_sorted = vectors[:, sorted_indices]

    # Select requested number of principal components
    pca_components = vectors_sorted[:, :n_components]

    # Fix PC1 sign ambiguity
    # Make PC1 point in the direction of positive average stock movement
    if np.mean(pca_components[:, 0]) < 0:
        pca_components[:, 0] *= -1

    # Project standardized data onto principal components
    projected_data = np.dot(data_std, pca_components)

    # Create loadings DataFrame
    loadings = pd.DataFrame(
        pca_components,
        index=ticker_names,
        columns=[f"PC{i+1}" for i in range(n_components)]
    )

    if print_components:

        print("TOP 5 ASSETS ON PC1 (Overall Market)")
        print(loadings['PC1'].sort_values(ascending=False).head())

        if n_components >= 2:
            print("\n")
            print("TOP 5 POSITIVE LOADINGS ON PC2")
            print(loadings['PC2'].sort_values(ascending=False).head())

            print("\n")
            print("TOP 5 NEGATIVE LOADINGS ON PC2")
            print(loadings['PC2'].sort_values().head())

        if n_components >= 3:
            print("\n")
            print("TOP 5 POSITIVE LOADINGS ON PC3")
            print(loadings['PC3'].sort_values(ascending=False).head())

            print("\n")
            print("TOP 5 NEGATIVE LOADINGS ON PC3")
            print(loadings['PC3'].sort_values().head())

    return projected_data, dates, loadings
def calculate_bic(model, X):
    K = model.n_components
    D = X.shape[1]
    n = len(X)

    # Number of free parameters

    # Initial state probabilities
    start_params = K - 1

    # Transition matrix
    transition_params = K * (K - 1)

    # Means
    mean_params = K * D

    # Full covariance matrices
    covariance_params = K * (D * (D + 1) / 2)

    num_params = (
        start_params
        + transition_params
        + mean_params
        + covariance_params
    )

    log_likelihood = model.score(X)

    bic = -2 * log_likelihood + num_params * np.log(n)

    return bic, log_likelihood, num_params
def run_HMM(X, K, means=None, n_restarts=20, n_iter=1000, covariance_type="full"):
    best_model = None
    best_log_likelihood = -np.inf

    for seed in range(n_restarts):

        if means is not None:
            model = GaussianHMM(
                n_components=K,
                covariance_type=covariance_type,
                n_iter=n_iter,
                random_state=seed,
                init_params="stc"
            )

            model.means_ = np.asarray(means)

        else:
            model = GaussianHMM(
                n_components=K,
                covariance_type=covariance_type,
                n_iter=n_iter,
                random_state=seed
            )

        try:
            model.fit(X)
            log_likelihood = model.score(X)

            if (
                model.monitor_.converged
                and log_likelihood > best_log_likelihood
            ):
                best_log_likelihood = log_likelihood
                best_model = model

        except ValueError:
            # Skip numerically invalid runs
            continue

    if best_model is None:
        raise RuntimeError("No HMM runs converged successfully.")

    hidden_states = best_model.predict(X)

    return best_model, hidden_states
def total_variance_by_regime(filename, regime_series):
    data = pd.read_csv(filename, index_col=0)
    dates = pd.to_datetime(data.index)
    values = data.to_numpy(dtype=np.float64)

    mean = np.mean(values, axis=0)
    std_dev = np.std(values, axis=0)
    data_std = (values - mean) / std_dev

    df = pd.DataFrame(data_std, index=dates).join(regime_series, how="inner")

    total_var = {}
    for regime in sorted(df["Regime"].unique()):
        regime_data = df[df["Regime"] == regime].drop(columns="Regime")
        total_var[regime] = regime_data.to_numpy().var(axis=0, ddof=1).sum()

    return total_var
sectors = {
    'tech',
    'finance',
    'communication_services',
    'consumer_discretionary',
    'health_care',
    'industrials',
    'consumer_staples',
    'energy',
    'utilities',
    'materials',
    'real_estate'
}




#BIC calculated number of clusters is 4

projected_data, market_dates, market_loadings = PCA("Data Files/market_data.csv", 3, False)

#DF of PC1s of sector
sector_pc1s = pd.DataFrame()
for sector_name in sectors:
    data, dates, loadings = PCA(f"Data Files/{sector_name}_data.csv", 1 )
    sector_pc1s[sector_name] = pd.Series(data[:, 0], index=dates)



#find regimes
model, hidden_states = run_HMM(
    projected_data,
    K=4,
    n_restarts=10
)


# Calculate PC1 standard deviation within each original HMM regime
regime_volatility = {}

for regime in range(4):

    # Select observations belonging to this regime
    regime_data = projected_data[hidden_states == regime]

    # PC1 is the first column
    pc1_volatility = np.std(regime_data[:, 0])

    regime_volatility[regime] = pc1_volatility


# Sort original regimes from highest PC1 volatility to lowest
sorted_regimes = sorted(
    regime_volatility,
    key=regime_volatility.get,
    reverse=True
)


# Create mapping:
# original HMM state -> volatility-ranked state
regime_mapping = {
    old_state: new_state
    for new_state, old_state in enumerate(sorted_regimes)
}


# Relabel hidden states according to volatility ranking
ordered_states = np.array([
    regime_mapping[state]
    for state in hidden_states
])



# PRINT REGIME INFORMATION


print("\nREGIME ORDER BY PC1 VOLATILITY")

for new_regime, old_regime in enumerate(sorted_regimes):

    print(
        f"Regime {new_regime}: "
        f"PC1 volatility = {regime_volatility[old_regime]:.4f} "
        f"(original HMM state {old_regime})"
    )



# CREATE DATED REGIME SERIES


regime_series = pd.Series(
    ordered_states,
    index=market_dates,
    name="Regime"
)



# COMBINE WITH SECTOR PC1 DATA


combined = sector_pc1s.join(
    regime_series,
    how="inner"
)



# REGIME-SPECIFIC CORRELATION MATRICES


for regime in range(4):

    regime_data = combined[
        combined["Regime"] == regime
    ]

    correlation_matrix = regime_data.drop(
        columns="Regime"
    ).corr()

    print(f"\nREGIME {regime}")
    print(
        f"PC1 volatility: "
        f"{regime_volatility[sorted_regimes[regime]]:.4f}"
    )

    #print(correlation_matrix)

explained_variance_by_sector = {}

for sector_name in sectors:
    total_var = total_variance_by_regime(f"Data Files/{sector_name}_data.csv", regime_series)

    sector_series = sector_pc1s[sector_name].to_frame("PC1").join(regime_series, how="inner")

    explained_ratios = {}
    for regime in range(4):
        pc1_var = sector_series[sector_series["Regime"] == regime]["PC1"].var(ddof=1)
        explained_ratios[regime] = pc1_var / total_var[regime]

    explained_variance_by_sector[sector_name] = explained_ratios

explained_df = pd.DataFrame(explained_variance_by_sector).T
explained_df.columns = [f"Regime {r}" for r in explained_df.columns]
print("\nPC1 EXPLAINED VARIANCE BY SECTOR, BY REGIME")
print(explained_df.round(3))



#drawing
for regime in range(4):

    regime_data = combined[
        combined["Regime"] == regime
    ]

    correlation_matrix = regime_data.drop(
        columns="Regime"
    ).corr()

    plt.figure(figsize=(10, 8))

    plt.imshow(
        correlation_matrix,
        vmin=-1,
        vmax=1,
        cmap="coolwarm"
    )

    plt.colorbar(label="Correlation")

    plt.xticks(
        range(len(correlation_matrix.columns)),
        correlation_matrix.columns,
        rotation=90
    )

    plt.yticks(
        range(len(correlation_matrix.columns)),
        correlation_matrix.columns
    )

    # Add correlation values
    for i in range(len(correlation_matrix)):
        for j in range(len(correlation_matrix)):
            plt.text(
                j,
                i,
                f"{correlation_matrix.iloc[i, j]:.2f}",
                ha="center",
                va="center"
            )

    plt.title(f"Sector PC1 Correlation — Regime {regime}")

    plt.tight_layout()
    plt.show()





print("\nHMM state means:")
print(model.means_)

print("\nHMM transition matrix:")
print(model.transmat_)

print("\nHMM state counts:")
print(np.bincount(hidden_states))

print("\nLog likelihood:")
print(model.score(projected_data))

print("\nConverged:")
print(model.monitor_.converged)



# PLOT 1: All PCs with HMM regimes


K = model.n_components

fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

pc_names = ["PC1", "PC2", "PC3"]

for pc in range(3):

    axes[pc].plot(
        projected_data[:, pc],
        linewidth=1,
        alpha=0.6,
        label=pc_names[pc]
    )

    # Plot every HMM state
    for state in range(K):

        mask = hidden_states == state

        axes[pc].scatter(
            np.where(mask)[0],
            projected_data[mask, pc],
            s=5,
            label=f"State {state}"
        )

    axes[pc].set_ylabel(pc_names[pc])
    axes[pc].set_title(f"{pc_names[pc]} with HMM Regimes")
    axes[pc].legend()

axes[-1].set_xlabel("Time")

plt.tight_layout()
plt.show()



# PLOT 2: Distribution of each PC within each regime


fig, axes = plt.subplots(3, 1, figsize=(12, 10))

for pc in range(3):

    for state in range(K):

        state_data = projected_data[hidden_states == state, pc]

        axes[pc].hist(
            state_data,
            bins=40,
            alpha=0.5,
            label=f"State {state}"
        )

    axes[pc].set_xlabel(pc_names[pc])
    axes[pc].set_ylabel("Frequency")
    axes[pc].set_title(f"{pc_names[pc]} Distribution by HMM State")
    axes[pc].legend()

plt.tight_layout()
plt.show()



# PLOT 3: State-specific variance for each PC


variances = np.diagonal(model.covars_, axis1=1, axis2=2)

x = np.arange(3)
width = 0.8 / K

plt.figure(figsize=(10, 6))

for state in range(K):

    plt.bar(
        x + state * width,
        variances[state],
        width,
        label=f"State {state}"
    )

plt.xticks(
    x + width * (K - 1) / 2,
    pc_names
)

plt.xlabel("Principal Component")
plt.ylabel("Variance")
plt.title("PC Variance Across HMM Regimes")
plt.legend()

plt.tight_layout()
plt.show()
