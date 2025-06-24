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



def compute_avg_ages(output_folder,
                              result_folder,
                              data_folder_fig6,
                              data_folder_fig7):
    """
    Computes the average voter age for each candidate in each district
    """



    # Age midpoint per age group
    avg_age_groups = [19, 25, 35, 45, 55, 65, 75, 85]

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

    # Directory with .json district results output/results_districts
    results_dir = Path(os.path.join(output_folder,result_folder))
    dist_files = list(results_dir.rglob("*.json"))


    data = []
    for dist_path in dist_files:
        with open(dist_path, 'r') as file:
            dist = json.load(file)

        X = np.array(dist['X'])
        W = np.array(dist['W'])
        W_agg = np.array(dist['W_agg'])
        prob = np.array(dist['prob'])
        group_agg = dist.get('group_agg', [])
        if isinstance(group_agg, int):
            group_agg = [group_agg]
        group_agg = np.array(group_agg)

        if len(group_agg) < 3:
            continue  # skip if not enough groups

        # Compute average age per group
        voters_per_age_group = W.sum(axis=0)
        avg_age_agg = []
        g_start = 0
        for g_cut in group_agg:
            age_weights = voters_per_age_group[g_start:g_cut]
            ages = avg_age_groups[g_start:g_cut]
            avg = np.sum(age_weights * ages) / age_weights.sum()
            avg_age_agg.append(avg)
            g_start = g_cut
        avg_age_agg = np.array(avg_age_agg)

        # Compute candidate-wise average age and probabilities
        avg_age_per_cand = prob.T @ avg_age_agg / prob.sum(axis=0)
        prob_per_cand = X.sum(axis=0) / X.sum()

        for i, cand in enumerate(CANDIDATOS):
            data.append({
                'Candidate': cand,
                'AvgAge': avg_age_per_cand[i],
                'VoteProb': prob_per_cand[i],
                'Color': age_color_map[i % len(age_color_map)]
            })

    # Build DataFrame
    df = pd.DataFrame(data)

    # define and create paths for figure 
    path_fig6 = os.path.join(output_folder,data_folder_fig6)
    path_fig7 = os.path.join(output_folder,data_folder_fig7)
    os.makedirs(path_fig6, exist_ok = True)
    os.makedirs(path_fig7, exist_ok = True) 

    df.to_csv(os.path.join(path_fig6, 'average_age_district.csv'))

    # Save average age per candidate (for figure 7)
    df.groupby('Candidate')['AvgAge'].mean().to_csv(os.path.join(path_fig7, 'average_age_total.csv'))



# Entry point for script
def main():
    output_folder = 'output'
    result_folder = 'results_districts'
    data_folder_fig6 = 'figure6'
    data_folder_fig7 = 'figure7'


    compute_avg_ages(output_folder, result_folder, data_folder_fig6, data_folder_fig7)

if __name__ == "__main__":
    main()