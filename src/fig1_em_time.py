import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import ticker
import os

from aux_functions import read_simulated_instances



def plot_EM_time(
    df,
    save_dir='figures',
    save_name='EM_time.pdf',
    filter_I=100
):
    method_order = ['exact', 'mcmc_100', 'mcmc_1000', 'mvn_cdf', 'mvn_pdf', 'mult']
    method_names = ['EXACT', 'MCMC 100', 'MCMC 1000', 'MVN CDF', 'MVN PDF', 'MULT']
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown']
    markers = ['*', 'o', 'v', '^', 's', 'D']

    df.loc[df['status'] != 0, 'time'] = np.nan

    df_time = df.groupby(['I', 'B', 'G', 'C', 'method'])['time'].agg(
        time='mean',
        std='std',
        p25=lambda x: x.quantile(0.25),
        p75=lambda x: x.quantile(0.75)
    ).reset_index()

    df_time = df_time.dropna(subset=['time'])
    df_time = df_time[df_time['I'] == filter_I]
    df_time['C'] = pd.Categorical(df_time['C'], categories=[2, 3, 4, 5, 10], ordered=True)
    df_time['C_order'] = df_time['C'].cat.codes

    g_values = df_time['G'].unique()
    fig, axes = plt.subplots(1, len(g_values), figsize=(8, 4), sharey=True)

    for i, g in enumerate(g_values):
        ax = axes[i]
        df_g = df_time[df_time['G'] == g]

        for idx, method in enumerate(method_order):
            df_method = df_g[df_g['method'] == method]
            ax.scatter(
                df_method['C_order'],
                df_method['time'],
                color=colors[idx],
                marker=markers[idx],
                label=method_names[idx],
                facecolors = 'none',
                s=20,
                alpha=0.8
            )

        ax.set_title(f'G = {g}')
        ax.set_xlabel('C')
        if i == 0:
            ax.set_ylabel('Mean Time [s]')
        if i == len(g_values) - 1:
            ax.legend(bbox_to_anchor=(1.15, 1))

        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:.5f}".rstrip('0').rstrip('.')))
        ax.set_xticks(range(5))
        ax.set_xticklabels(['2', '3', '4', '5', '10'])

    plt.tight_layout()
    os.makedirs(save_dir, exist_ok=True)
    plt.savefig(os.path.join(save_dir, save_name), bbox_inches="tight")
    plt.show()

# Main script execution
if __name__ == '__main__':
    save_dir = 'figures'      # Where to save the plot
    save_name = 'fig1-em-time.pdf'

    df = read_simulated_instances()
    plot_EM_time(df, save_dir=save_dir, save_name=save_name)
