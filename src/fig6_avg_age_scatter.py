#!/usr/bin/env python
# coding: utf-8

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import matplotlib.gridspec as gridspec

# Fixed candidate list for 2021 Chilean presidential election
CANDIDATOS = np.array([
    "GABRIEL BORIC",
    "JOSE ANTONIO KAST",
    "YASNA PROVOSTE",
    "SEBASTIAN SICHEL",
    "EDUARDO ARTES",
    "MARCO ENRIQUEZ-OMINAMI",
    "FRANCO ALDO PARISI",
    "NULO BLANCO"
])


def plot_scatter_districts_v2(output_folder, image_dir):
    """
    Generate a scatter plot with boxplots to visualize the relationship between
    average voter age and voting probabilities per candidate, across districts.
    """


    # Color mapping and candidate order (for plot consistency)
    age_color_map = ['#A9A9A9', '#8B4513', '#228B22', '#1E90FF', '#9370DB', '#FFA500', '#FF69B4', '#FF0000']
    order_candidatos = [7, 4, 5, 0, 2, 6, 3, 1]

    # Optional label shortening
    candidate_short_names = {
        "YASNA PROVOSTE": "Yasna Provoste",
        "GABRIEL BORIC": "Gabriel Boric",
        "FRANCO ALDO PARISI": "Franco Parisi",
        "JOSE ANTONIO KAST": "José A. Kast",
        "EDUARDO ARTES": "Eduardo Artés",
        "MARCO ENRIQUEZ-OMINAMI": "M. Enríquez-Ominami",
        "SEBASTIAN SICHEL": "Sebastián Sichel",
        "NULO BLANCO": "Null/Blank"
    }

  
    # read dataframe
    df_plot = pd.read_csv(output_folder)

    color_map = {cand: age_color_map[i] for i, cand in enumerate(CANDIDATOS[order_candidatos])}
    df_plot['Color'] = df_plot['Candidate'].map(color_map)

    # Layout setup
    fig = plt.figure(figsize=(14, 12))
    gs = gridspec.GridSpec(2, 2, width_ratios=[2.5, 1], height_ratios=[1, 2.5], wspace=0.1, hspace=0.1)
    ax_box_x = fig.add_subplot(gs[0, 0])
    ax_scatter = fig.add_subplot(gs[1, 0])
    ax_box_y = fig.add_subplot(gs[1, 1])
    ax_legend = fig.add_subplot(gs[0, 1])

    # Main scatter plot
    ax_scatter.scatter(df_plot['AvgAge'], df_plot['VoteProb'], color=df_plot['Color'], alpha=0.6, s=15)
    for i, cand in enumerate(CANDIDATOS[order_candidatos]):
        ax_legend.scatter([], [], color=age_color_map[i], alpha=1, s=20, label=candidate_short_names[cand])

    ax_scatter.set_xlabel("Average Age of Voters")
    ax_scatter.set_ylabel("Voting Probability")
    # ax_scatter.set_yticks(np.arange(0, 0.7, 0.1))
    ax_scatter.spines[['right', 'top']].set_visible(False)

    ax_legend.legend(loc="center", title='Candidate')
    ax_legend.axis('off')
    ax_legend.set_facecolor('white')
    ax_legend.get_legend().get_frame().set_edgecolor('black')

    # Boxplot: Age distribution per candidate
    sns.boxplot(data=df_plot, x='AvgAge', y='Candidate',
                ax=ax_box_x, palette=age_color_map[:len(CANDIDATOS)], orient='h',
                order=CANDIDATOS[order_candidatos])
    ax_box_x.set_yticklabels([])
    # ax_box_x.set_xticklabels([])
    ax_box_x.set_ylabel("")
    ax_box_x.set_xlabel("")
    ax_box_x.tick_params(axis='y', left=False)
    ax_box_x.tick_params(axis='x', which='both', bottom=True)
    ax_box_x.tick_params(labelbottom=True)
    ax_box_x.spines[['right', 'top', 'left']].set_visible(False)

    # Boxplot: Vote probability per candidate
    sns.boxplot(data=df_plot, y='VoteProb', x='Candidate',
                ax=ax_box_y, palette=age_color_map[:len(CANDIDATOS)][::-1],
                order=CANDIDATOS[order_candidatos][::-1])
    ax_box_y.invert_xaxis()
    ax_box_y.set_xticklabels([])
    # ax_box_y.set_yticklabels([])
    ax_box_y.set_ylabel("")
    ax_box_y.set_xlabel("")
    ax_box_y.tick_params(axis='x', bottom=False)
    ax_box_y.tick_params(axis='y', which='both', left=True)
    ax_box_y.tick_params(labelleft=True)
    ax_box_y.spines[['right', 'top', 'bottom']].set_visible(False)

    for ax in [ax_scatter, ax_box_x, ax_box_y]:
        ax.grid(False)
        for spine in ax.spines.values():
            spine.set_edgecolor('black')
            spine.set_linewidth(1)

    
    # Force limits to match
    xlim = ax_scatter.get_xlim()
    ylim = ax_scatter.get_ylim()
    ax_box_x.set_xlim(xlim)
    ax_box_y.set_ylim(ylim)


    # Save output
    os.makedirs(image_dir, exist_ok=True)
    save_path = os.path.join(image_dir, 'scatter_districts.pdf')
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.show()
    plt.close()



# Entry point for script
def main():
    output_folder = 'output/figure6/average_age_district.csv'
    image_dir = 'figures'

    plot_scatter_districts_v2(output_folder, image_dir)

if __name__ == "__main__":
    main()
