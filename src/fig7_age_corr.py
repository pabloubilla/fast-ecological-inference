import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import numpy as np
import os

def plot_candidate_age_correlations(info_path, avg_age_path, save_path):
    """
    Generate correlation plots between candidate/voter age and metadata variables.

    Parameters:
    - info_path: CSV file path with candidate metadata
    - avg_age_path: CSV file path with average age of voters per candidate
    - save_path: output path to save the figure (PDF)
    """

    # --- Load and prepare data ---
    df1 = pd.read_csv(info_path)
    df2 = pd.read_csv(avg_age_path)

    df1['Candidate'] = df1['Candidate'].str.strip().str.upper()
    df2['Candidate'] = df2['Candidate'].str.strip().str.upper()

    candidate_rename = {
        "YASNA PROVOSTE": "Yasna Provoste",
        "GABRIEL BORIC": "Gabriel Boric",
        "FRANCO ALDO PARISI": "Franco Parisi",
        "JOSE ANTONIO KAST": "José A. Kast",
        "EDUARDO ARTES": "Eduardo Artés",
        "MARCO ENRIQUEZ-OMINAMI": "M. Enríquez-Ominami",
        "SEBASTIAN SICHEL": "Sebastián Sichel",
        "NULO BLANCO": "Null/Blank"
    }

    variable_rename = {
        'Edad_partidos': "Candidate's party age",
        'Edad_cargo_publico': "Years in public office",
        'Edad': "Candidate's age",
        'Edad_apoyo': "Average age of supporting parties",
    }

    df1['Candidate'] = df1['Candidate'].replace(candidate_rename)
    df2['Candidate'] = df2['Candidate'].replace(candidate_rename)

    df_merged = pd.merge(df1, df2, on='Candidate', how='inner')

    cols = ['Edad', 'Edad_cargo_publico', 'Edad_partidos', 'Edad_apoyo']
    for col in cols:
        df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce')

    df_long = df_merged.melt(
        id_vars=['Candidate', 'AvgAge'],
        value_vars=cols,
        var_name='Variable',
        value_name='Value'
    ).dropna()

    df_long['Variable'] = df_long['Variable'].replace(variable_rename)
    col_display = [variable_rename[c] for c in cols]

    # --- Candidate colors and order ---
    candidate_order = [
        "Eduardo Artés",
        "M. Enríquez-Ominami",
        "Gabriel Boric",
        "Yasna Provoste",
        "Franco Parisi",
        "Sebastián Sichel",
        "José A. Kast",
    ]

    candidate_palette = {
        "Eduardo Artés":        '#8B4513',
        "M. Enríquez-Ominami":  '#228B22',
        "Gabriel Boric":        '#1E90FF',
        "Yasna Provoste":       '#9370DB',
        "Franco Parisi":        '#FFA500',
        "Sebastián Sichel":     '#FF69B4',
        "José A. Kast":         '#FF0000'
    }

    # --- Plot setup ---
    fig_widths = [4, 4, 4, 4, 1.5]
    fig, axes = plt.subplots(1, 5, figsize=(12, 3),
                             gridspec_kw={'width_ratios': fig_widths},
                             sharey=True)

    for i, variable in enumerate(col_display):
        ax = axes[i]
        data = df_long[df_long['Variable'] == variable]

        # Scatter for each candidate
        for cand in candidate_order:
            d = data[data['Candidate'] == cand]
            if not d.empty:
                ax.scatter(d['Value'], d['AvgAge'],
                           color=candidate_palette[cand],
                           edgecolor='k', s=70)

        # Regression line and correlation
        if len(data) > 1:
            sns.regplot(
                x='Value', y='AvgAge', data=data, ax=ax,
                scatter=False, color='grey', ci=None, truncate=False,
                line_kws={'linewidth': 2, 'linestyle': 'dashed'}
            )
            r, _ = pearsonr(data['Value'], data['AvgAge'])
            ax.annotate(f"$\\rho={r:.2f}$",
                        xy=(.55, .3), 
                        xycoords='axes fraction',
                        color='black',
                        # bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black")
                        )

        ax.set_xlabel(variable)
        ax.set_ylabel("Average Voter Age" if i == 0 else "")
        ax.set_title("")

    # --- Legend ---
    axes[-1].axis('off')
    handles = [plt.Line2D([0], [0], marker='o', color='w', label=c,
                markerfacecolor=candidate_palette[c], markeredgecolor='k', markersize=10)
               for c in candidate_order]
    axes[-1].legend(handles=handles, title="Candidate", loc='center left',
                    frameon=True, edgecolor='black')

    # --- Save and display ---
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.show()


# --- Main ---
if __name__ == "__main__":
    plot_candidate_age_correlations(
        info_path="data/info_candidates.csv",
        avg_age_path="output/figure7/average_age_total.csv",
        save_path="figures/fig7-age-corr.pdf"
    )
