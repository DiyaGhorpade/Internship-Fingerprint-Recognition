# services/analytics_engine.py
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.graphics.mosaicplot import mosaic
from scipy.stats import chi2_contingency
import os

# Read dataset
df = pd.read_csv("blood_fingerprint_FULL.csv")

# --- LOAD DATA ---
df = pd.read_csv("blood_fingerprint_FULL.csv")

# Normalize column names to avoid case issues
df.columns = df.columns.str.lower()

# Rename to standard names used by engine
rename_map = {
    "fingerprint_type": "FingerprintType",
    "blood_type": "BloodGroup",
    "bloodgroup": "BloodGroup",
    "file_path": "FilePath",
    "filename": "FileName"
}

df = df.rename(columns=rename_map)

# Now enforce categories
df["FingerprintType"] = df["FingerprintType"].astype("category")
df["BloodGroup"] = df["BloodGroup"].astype("category")


# Convert to categorical
df["FingerprintType"] = df["FingerprintType"].astype("category")
df["BloodGroup"] = df["BloodGroup"].astype("category")

# Directory for saving plots
STATIC_DIR = "static/analytics"
os.makedirs(STATIC_DIR, exist_ok=True)

def save_plot(fig, filename):
    filepath = os.path.join(STATIC_DIR, filename)
    fig.savefig(filepath, bbox_inches='tight')
    plt.close(fig)
    return filepath


def run_analytics():
    # Frequency table
    ct = pd.crosstab(df["FingerprintType"], df["BloodGroup"])

    # Chi-square test
    chi2, p, dof, expected = chi2_contingency(ct)
    expected_df = pd.DataFrame(expected, index=ct.index, columns=ct.columns)

    # Standardized residuals
    residuals = (ct - expected) / np.sqrt(expected)
    residuals_df = pd.DataFrame(residuals, index=ct.index, columns=ct.columns)

    # Correlation (only encoded columns)
    df_enc = df[['FingerprintType', 'BloodGroup']].copy()
    df_enc['FingerprintType'] = df_enc['FingerprintType'].cat.codes
    df_enc['BloodGroup'] = df_enc['BloodGroup'].cat.codes
    corr = df_enc.corr()

    ### 📊 PLOTS GENERATION ###

    # Heatmap - Clean + formatted
    fig = plt.figure(figsize=(8,6), dpi=150)
    sns.heatmap(
        ct,
        annot=True,
        fmt="d",  # <-- no scientific notation
        cmap="viridis",
        cbar=True,
        linewidths=0.4,
        linecolor="black"
    )

    plt.title("Fingerprint vs Blood Group Frequency", fontsize=14)
    plt.xlabel("Blood Group", fontsize=12)
    plt.ylabel("Fingerprint Type", fontsize=12)

    plt.xticks(rotation=30, ha="right", fontsize=10)
    plt.yticks(fontsize=10)

    plt.tight_layout()
    heatmap_path = save_plot(fig, "heatmap.png")

    

    #Fingerprint Pattern Count Distribution
    counts = df["FingerprintType"].value_counts()
    fig = plt.figure(figsize=(6,4), dpi=150)
    plt.bar(counts.index.astype(str), counts.values, color="teal")
    plt.title("Fingerprint Pattern Distribution")
    plt.xlabel("Fingerprint Type")
    plt.ylabel("Count")
    pattern_dist_path = save_plot(fig, "pattern_distribution.png")

    #Percentage heatmap
    fig = plt.figure(figsize=(8,6), dpi=150)
    sns.heatmap(ct.div(ct.sum(axis=0), axis=1)*100, annot=True, fmt=".1f", cmap="coolwarm")
    plt.title("% Fingerprint Distribution by Blood Group", fontsize=14)
    plt.xlabel("Blood Group", fontsize=12)
    plt.ylabel("Fingerprint Type", fontsize=12)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    percent_heatmap_path = save_plot(fig, "percent_heatmap.png")

    # Probability Distribution Histograms
    prob_cols = ["p_arc", "p_whorl", "p_loop"]  # lowercase after normalization
    prob_cols_exist = [col for col in prob_cols if col in df.columns]
    
    print(f"Available columns: {df.columns.tolist()}")
    print(f"Looking for: {prob_cols}")
    print(f"Found: {prob_cols_exist}")
    
    if prob_cols_exist:
        fig, axes = plt.subplots(1, len(prob_cols_exist), figsize=(12, 4), dpi=150)
        if len(prob_cols_exist) == 1:
            axes = [axes]
        
        for i, col in enumerate(prob_cols_exist):
            data = df[col].dropna()
            print(f"{col}: {len(data)} values, range [{data.min():.3f}, {data.max():.3f}]")
            axes[i].hist(data, bins=20, color="steelblue", edgecolor="black", alpha=0.7)
            axes[i].set_title(col.upper(), fontsize=11, fontweight='bold')
            axes[i].set_xlabel("Probability", fontsize=9)
            axes[i].set_ylabel("Frequency", fontsize=9)
            axes[i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        prob_dist_path = save_plot(fig, "probability_distribution.png")
    else:
        print("WARNING: No probability columns found!")
        prob_dist_path = None
 
    # Log Odds Ratio Heatmap
    # Calculate log odds ratio: log(observed / (total - observed))
    total = ct.sum().sum()

    log_odds = pd.DataFrame(index=ct.index, columns=ct.columns)
    print("\nLog Odds Ratios:")
    for fp in ct.index:
        for bg in ct.columns:
            observed = ct.loc[fp, bg]
            other = total - observed
            
            if other != 0 and observed > 0:
                odds = observed / other
                log_odds.loc[fp, bg] = np.log(odds)
                print(f"{fp} vs {bg}: {log_odds.loc[fp, bg]:.4f}")
            else:
                log_odds.loc[fp, bg] = np.nan
                print(f"{fp} vs {bg}: NaN")
    log_odds = log_odds.astype(float)

    fig = plt.figure(figsize=(8, 6), dpi=150)
    sns.heatmap(
        log_odds,
        annot=True,
        fmt=".3f",
        cmap="RdBu_r",
        center=0,
        cbar_kws={'label': 'Log Odds Ratio'},
        linewidths=0.5,
        linecolor='gray'
    )
    plt.title("Log Odds Ratio: Fingerprint vs Blood Group", fontsize=14, fontweight='bold')
    plt.xlabel("Blood Group", fontsize=12)
    plt.ylabel("Fingerprint Type", fontsize=12)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    log_odds_path = save_plot(fig, "log_odds.png")

    ### 🧠 Correlation Heatmap (Encoded Labels)
    df_enc = df.copy()
    df_enc['FingerprintType'] = df_enc['FingerprintType'].cat.codes
    df_enc['BloodGroup'] = df_enc['BloodGroup'].cat.codes

    # Drop non-numeric columns if exist
    drop_cols = [c for c in ['FilePath', 'FileName'] if c in df_enc.columns]
    df_enc_numeric = df_enc.drop(columns=drop_cols)

    fig = plt.figure(figsize=(5,4), dpi=150)
    sns.heatmap(df_enc_numeric.corr(), annot=True, cmap="viridis", center=0)
    plt.title("Correlation Matrix (Encoded Labels)")
    corr2_path = save_plot(fig, "correlation_encoded.png")


    # Bar Chart
    fig = ct.plot(kind="bar").get_figure()
    bar_path = save_plot(fig, "barplot.png")

    # Mosaic Plot
    fig, ax = plt.subplots(figsize=(6,5))
    mosaic(df, ["BloodGroup", "FingerprintType"], ax=ax)
    plt.title("Mosaic Plot: Blood Group vs Fingerprint Type")
    mosaic_path = save_plot(fig, "mosaic.png")


    # Residuals Heatmap
    fig = plt.figure(figsize=(6,4))
    sns.heatmap(residuals_df, annot=True, cmap="coolwarm", center=0)
    residuals_path = save_plot(fig, "residuals.png")

    


    ### ✅ RETURN CLEAN OUTPUT ###
    return {
        "tables": {
            "expected": expected_df.to_dict(),
            "chi_square": {"chi2": float(chi2), "p": float(p), "dof": int(dof)},
            "residuals": residuals_df.to_dict(),
            "correlation": corr.to_dict(),
        },
        "plots": {
            "heatmap": heatmap_path,
            "percent_heatmap": percent_heatmap_path,
            "barplot": bar_path,
            "mosaic": mosaic_path,
            "residuals": residuals_path,
            "correlation_encoded": corr2_path,
            "pattern_distribution": pattern_dist_path,
            "probability_distribution":prob_dist_path,
            "log_odds":log_odds_path
        }
    }
