import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from aux_functions import read_simulated_instances


def plot_EM_error_boxplot(
    df,
    save_dir='images',
    save_name='EM_error_boxplot.pdf',
    filter_I=100
):
    method_order = ['exact', 'mcmc_100', 'mcmc_1000', 'mvn_cdf', 'mvn_pdf', 'mult']
    method_names = ['EXACT', 'MCMC 100', 'MCMC 1000', 'MVN CDF', 'MVN PDF', 'MULT']
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown']

    df.loc[df['status'] != 0, 'mean_error'] = np.nan
    df_filtered = df[df['I'] == filter_I].dropna(subset=['mean_error'])

    g = sns.FacetGrid(
        df_filtered,
        col="C",
        row="G",
        margin_titles=True,
        sharey=True,
        sharex=False,
        height=2,
        aspect=1.2,
    )

    g.map_dataframe(
        sns.boxplot,
        x="method",
        y="mean_error",
        order=method_order,
        palette=colors,
        showfliers=True
    )

    g.set_axis_labels("", "")
    g.set_xticklabels(rotation=90, ha="right")
    g.set(xticks=range(len(method_order)), xticklabels=method_names)

    for ax, col_name in zip(g.axes[0], g.col_names):
        ax.text(
            0.5, 1.05,
            f"C = {col_name}",
            ha="center",
            va="center",
            transform=ax.transAxes,
            bbox=dict(facecolor="white", edgecolor="black", pad=5),
            fontsize=10, fontweight='bold'
        )

    for ax, row_name in zip(g.axes[:, -1], g.row_names):
        ax.text(
            1.05, 0.5,
            f"G = {row_name}",
            ha="center",
            va="center",
            rotation=-90,
            transform=ax.transAxes,
            bbox=dict(facecolor="white", edgecolor="black", pad=5),
            fontsize=10, fontweight='bold'
        )

    for row_idx, row_axes in enumerate(g.axes):
        for col_idx, ax in enumerate(row_axes):
            if row_idx != len(g.row_names) - 1:
                ax.set_xticks([])
                ax.set_xticklabels([])

    g.fig.text(0.5, -0.01, "E-Step Method", ha='center', fontsize=10)
    g.fig.text(-0.01, 0.5, "MAE", va='center', rotation='vertical', fontsize=10)
    g.set_titles(col_template='', row_template='')

    plt.tight_layout()
    os.makedirs(save_dir, exist_ok=True)
    plt.savefig(os.path.join(save_dir, save_name), bbox_inches="tight")
    plt.show()

# Main execution
if __name__ == '__main__':
    data_dir = 'results'         # Folder with .json results
    save_dir = 'figures'          # Output folder for plots
    save_name = 'fig2-em-error.pdf'
    I_filter = 100               # Fixed number of individuals

    df = read_simulated_instances()
    plot_EM_error_boxplot(df, save_dir=save_dir, save_name=save_name, filter_I=I_filter)
