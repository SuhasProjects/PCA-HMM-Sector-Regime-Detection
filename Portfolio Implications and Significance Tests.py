import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from scipy.stats import norm


# ============================================================
# PCA
# ============================================================

def PCA(filename, n_components):

    data = pd.read_csv(filename, index_col=0)

    dates = pd.to_datetime(data.index)
    values = data.to_numpy(dtype=float)
    ticker_names = data.columns

    # Standardize each stock
    data_std = (values - values.mean(axis=0)) / values.std(axis=0)

    # Eigendecomposition of covariance matrix
    cov_matrix = np.cov(data_std.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

    # Sort largest -> smallest
    order = np.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, order]

    # Select PCs
    components = eigenvectors[:, :n_components]

    # Fix PC1 sign
    if components[:, 0].mean() < 0:
        components[:, 0] *= -1

    # Project data
    projected_data = data_std @ components

    # Loadings
    loadings = pd.DataFrame(
        components,
        index=ticker_names,
        columns=[f"PC{i+1}" for i in range(n_components)]
    )

    return projected_data, dates, loadings

def run_HMM(X, K, n_restarts=10, n_iter=1000):

    best_model = None
    best_log_likelihood = -np.inf

    for seed in range(n_restarts):

        model = GaussianHMM(
            n_components=K,
            covariance_type="full",
            n_iter=n_iter,
            random_state=seed
        )

        try:
            model.fit(X)

            if model.monitor_.converged:

                log_likelihood = model.score(X)

                if log_likelihood > best_log_likelihood:
                    best_model = model
                    best_log_likelihood = log_likelihood

        except ValueError:
            continue

    if best_model is None:
        raise RuntimeError("No HMM runs converged.")

    return best_model, best_model.predict(X)

def fisher_z_test(r1, n1, r2, n2):

    z1 = np.arctanh(r1)
    z2 = np.arctanh(r2)

    standard_error = np.sqrt(
        1 / (n1 - 3)
        + 1 / (n2 - 3)
    )

    z = (z1 - z2) / standard_error

    p_value = 2 * (
        1 - norm.cdf(abs(z))
    )

    return z, p_value

def min_variance_weights(cov_matrix):

    covariance = cov_matrix.to_numpy()

    # Pseudoinverse is more stable when sectors are highly correlated
    inv_cov = np.linalg.pinv(covariance)

    ones = np.ones(len(covariance))

    weights = (
        inv_cov @ ones
        / (ones @ inv_cov @ ones)
    )

    return pd.Series(
        weights,
        index=cov_matrix.index
    )

sectors = [
    "tech",
    "finance",
    "communication_services",
    "consumer_discretionary",
    "health_care",
    "industrials",
    "consumer_staples",
    "energy",
    "utilities",
    "materials",
    "real_estate"
]


# ============================================================
# MARKET PCA
# ============================================================

projected_data, market_dates, market_loadings = PCA(
    "market_data.csv",
    3
)


# ============================================================
# SECTOR PC1s
# ============================================================

sector_pc1s = pd.DataFrame(index=market_dates)

for sector in sectors:

    data, dates, _ = PCA(
        f"{sector}_data.csv",
        1
    )

    sector_pc1s[sector] = pd.Series(
        data[:, 0],
        index=dates
    )


# HMM REGIMES

model, hidden_states = run_HMM(
    projected_data,
    K=4
)


# RANK REGIMES BY PC1 VOLATILITY

regime_volatility = {
    state: projected_data[
        hidden_states == state,
        0
    ].std()
    for state in range(4)
}

sorted_states = sorted(
    regime_volatility,
    key=regime_volatility.get,
    reverse=True
)

# Original HMM state -> volatility-ranked regime
regime_mapping = {
    old: new
    for new, old in enumerate(sorted_states)
}

ordered_states = np.array([
    regime_mapping[state]
    for state in hidden_states
])

regime_series = pd.Series(
    ordered_states,
    index=market_dates,
    name="Regime"
)


# REGIME PERSISTENCE

expected_duration = {}

for new_regime, old_regime in enumerate(sorted_states):

    persistence = model.transmat_[
        old_regime,
        old_regime
    ]

    expected_duration[new_regime] = (
        1 / (1 - persistence)
    )

duration_df = pd.DataFrame.from_dict(
    expected_duration,
    orient="index",
    columns=["Expected Duration (days)"]
)

duration_df.index.name = "Regime"


# COMBINE DATA

combined = sector_pc1s.join(
    regime_series,
    how="inner"
)

# Add overall market PC1
combined["Market PC1"] = projected_data[:, 0]

# Put Market PC1 first
correlation_columns = [
    "Market PC1"
] + sectors

# CORRELATION MATRICES


correlation_matrices = {}

for regime in range(4):

    regime_data = combined[
        combined["Regime"] == regime
    ]

    correlation_matrices[regime] = (
        regime_data[correlation_columns].corr()
    )

# CORRELATION HEATMAPS

for regime in range(4):

    corr = correlation_matrices[regime]

    plt.figure(figsize=(11, 9))

    plt.imshow(
        corr,
        vmin=-1,
        vmax=1,
        cmap="coolwarm"
    )

    plt.colorbar(
        label="Correlation"
    )

    plt.xticks(
        range(len(corr.columns)),
        corr.columns,
        rotation=90
    )

    plt.yticks(
        range(len(corr.columns)),
        corr.columns
    )

    # Add correlation values
    for i in range(len(corr)):

        for j in range(len(corr)):

            plt.text(
                j,
                i,
                f"{corr.iloc[i, j]:.2f}",
                ha="center",
                va="center"
            )

    plt.title(
        f"Sector PC1 Correlation — Regime {regime}"
    )

    plt.tight_layout()
    plt.show()



# FISHER Z-TEST
# Compare highest-volatility regime (0) against lowest-volatility regime (3)

high_vol = combined[
    combined["Regime"] == 0
][sectors]

low_vol = combined[
    combined["Regime"] == 3
][sectors]

high_corr = high_vol.corr()
low_corr = low_vol.corr()

n_high = len(high_vol)
n_low = len(low_vol)

fisher_results = []

for i in range(len(sectors)):

    for j in range(i + 1, len(sectors)):

        sector_1 = sectors[i]
        sector_2 = sectors[j]

        r_high = high_corr.loc[
            sector_1,
            sector_2
        ]

        r_low = low_corr.loc[
            sector_1,
            sector_2
        ]

        z, p_value = fisher_z_test(
            r_high,
            n_high,
            r_low,
            n_low
        )

        fisher_results.append({
            "Sector 1": sector_1,
            "Sector 2": sector_2,
            "High-Vol Correlation": r_high,
            "Low-Vol Correlation": r_low,
            "Difference": r_high - r_low,
            "Z": z,
            "p-value": p_value
        })


fisher_df = pd.DataFrame(
    fisher_results
)



# BONFERRONI CORRECTION


num_tests = len(fisher_df)

fisher_df["Adjusted p-value"] = np.minimum(
    fisher_df["p-value"] * num_tests,
    1
)

fisher_df["Significant"] = (
    fisher_df["Adjusted p-value"] < 0.05
)



# REGIME-CONDITIONAL MINIMUM-VARIANCE PORTFOLIOS


portfolio_weights = {}

for regime in range(4):

    regime_data = combined[
        combined["Regime"] == regime
    ][sectors]

    # Minimum variance requires covariance,
    # not correlation
    covariance_matrix = regime_data.cov()

    portfolio_weights[regime] = (
        min_variance_weights(
            covariance_matrix
        )
    )


weights_df = pd.DataFrame(
    portfolio_weights
)

weights_df.columns = [
    f"Regime {regime}"
    for regime in range(4)
]



# MINIMUM-VARIANCE PORTFOLIO VOLATILITY

portfolio_volatility = {}

for regime in range(4):

    regime_data = combined[
        combined["Regime"] == regime
    ][sectors]

    covariance_matrix = regime_data.cov()

    weights = (
        portfolio_weights[regime]
        .to_numpy()
    )

    covariance = (
        covariance_matrix
        .to_numpy()
    )

    variance = (
        weights
        @ covariance
        @ weights
    )

    portfolio_volatility[regime] = np.sqrt(
        variance
    )


portfolio_volatility = pd.Series(
    portfolio_volatility,
    name="Minimum-Variance Portfolio Volatility"
)



# MINIMUM-VARIANCE PORTFOLIO VISUALIZATION


weights_df.T.plot(
    kind="bar",
    figsize=(12, 7)
)

plt.axhline(
    0,
    linewidth=0.8
)

plt.ylabel(
    "Portfolio Weight"
)

plt.xlabel(
    "Regime"
)

plt.title(
    "Minimum-Variance Portfolio Weights by Regime"
)

plt.legend(
    title="Sector",
    bbox_to_anchor=(1.05, 1),
    loc="upper left"
)

plt.tight_layout()
plt.show()




#Other Visualizations
print("\nEXPECTED REGIME DURATION")
print(duration_df.round(2))

print("\nFISHER Z-TEST: HIGH-VOLATILITY VS LOW-VOLATILITY")

significant_results = fisher_df[
    fisher_df["Significant"]
].sort_values("Adjusted p-value")

print(
    significant_results[
        [
            "Sector 1",
            "Sector 2",
            "High-Vol Correlation",
            "Low-Vol Correlation",
            "Difference",
            "Adjusted p-value"
        ]
    ].round(4)
)

print(
    f"\nSignificant pairs: "
    f"{len(significant_results)} / {len(fisher_df)}"
)


print("\nLARGEST CORRELATION INCREASES")

print(
    fisher_df
    .sort_values("Difference", ascending=False)
    .head(10)[
        [
            "Sector 1",
            "Sector 2",
            "High-Vol Correlation",
            "Low-Vol Correlation",
            "Difference",
            "Adjusted p-value"
        ]
    ]
    .round(4)
)


print("\nMINIMUM-VARIANCE PORTFOLIO VOLATILITY")
print(portfolio_volatility.round(4))