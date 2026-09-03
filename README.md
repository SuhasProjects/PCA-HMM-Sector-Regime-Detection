# Regime Detection & Cross-Sector Covariance Analysis

## Overview

This project is aiming to investigate how the structure of the U.S. equity market changes across different market regimes. Using daily returns from 400+ S&P 500 equities spanning multiple sectors, I use Principal Component Analysis (PCA) to reduce the dimensionality of the market and identify its main sources of variation. I then apply K-means clustering to the PCA-transformed data to identify distinct market states.

The ultimate goal is to use these identified states to initialize a Hidden Markov Model (HMM), estimate regime transition dynamics using the Baum-Welch algorithm, and analyze how market regimes affect volatility and PCA loadings across sectors, and how sector regimes affect each other.

## Questions I Aim to Answer

- What are the dominant sources of variation across S&P 500 equity returns?
- Can observations in PCA space be separated into distinct market states?
- How does market covariance structure change across different regimes?
- Do different sectors exhibit different regime dynamics?
- How do PCA loadings and cross-sector relationships change as the market transitions between regimes?
- What implications do these regime-dependent relationships have for portfolio construction and risk management?

## Methodology

### 1. Data Collection

Daily historical price data is collected for 400+ S&P 500 equities using `yfinance`. The stocks span a broad range of sectors, allowing the analysis to capture both market-wide and sector-specific behavior.

Prices are converted into daily returns, which form the basis for the subsequent statistical analysis.

### 2. Principal Component Analysis

PCA is applied to the standardized return data to identify the dominant directions of variation across equities.

The principal components provide a lower-dimensional representation of the market while preserving the largest sources of variation. I examine the explained variance and PCA structure to determine an appropriate number of components for subsequent analysis.

The resulting PCA projections provide a reduced-dimensional representation of market behavior that can be used for clustering and regime identification.

I chose to use 3 Principal Components since they explain 47.32% of variation in the returns. The fourth principal component explains less than half of the variance explained by the third, prompting me to choose this cutoff. 

### 3. K-means Clustering

K-means clustering is applied to the PCA-transformed observations to identify distinct groups of market behavior.

Rather than selecting the number of clusters arbitrarily, I evaluate different values of `k` using the **silhouette coefficient**. The silhouette score measures how well each observation fits within its assigned cluster relative to neighboring clusters.

The selected number of clusters provides an estimate of the number of distinct market states to use when initializing the HMM.

### 4. HMM Initialization

The K-means results will be used to initialize the parameters of a Gaussian Hidden Markov Model.

Cluster assignments and cluster statistics provide initial estimates for the HMM's state-dependent parameters, while the observed sequence of cluster assignments provides information for initializing the transition structure.

The Baum-Welch algorithm will then be used to estimate the HMM parameters and infer the latent market regimes.

### 5. Regime Analysis

After fitting the HMM, I will analyze how market characteristics vary across inferred regimes, including:

- PCA loadings
- Volatility
- Cross-sector correlations
- Regime persistence and transitions
- Sector-specific regime behavior

The goal is to determine whether the identified regimes correspond to economically meaningful differences in market structure.

## Current Progress

- [x] Collect historical data for 400+ S&P 500 equities
- [x] Calculate daily returns
- [x] Standardize return data
- [x] Perform PCA
- [x] Evaluate the number of principal components to retain
- [x] Project observations into PCA space
- [x] Perform K-means clustering
- [x] Evaluate cluster counts using silhouette analysis
- [x] Select the number of K-means clusters
- [ ] Initialize HMM parameters from K-means results
- [ ] Implement Baum-Welch parameter estimation
- [ ] Infer latent market regimes
- [ ] Analyze regime-dependent covariance and PCA structure
- [ ] Compare regime dynamics across sectors
- [ ] Evaluate portfolio and risk-management implications

## Tools & Technologies

- **Python**
- NumPy
- pandas
- scikit-learn
- Matplotlib
- yfinance
- hmmlearn
- VS Code

## Project Structure

```text
├── Main/
├── Downloading Data/
├── Silhouette Algorithm/
├── README.md
└── ...
