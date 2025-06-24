# Code that analyzes the optimal grouping in terms of the resulting macro-groups
# Displays a heatmap showing the frequency with which each group combination appears in the final solution

import pandas as pd
import matplotlib.pyplot as plt
import os

from aux_functions import read_district, group_agg_to_macro_group, list_age2index

# Print the loaded JSON data
verbose = True # print outputs

FOLDER = os.path.join("output", "results_districts")

# Function that gets all group aggregations for all electoral districts
# Reads from the .JSON output files generated in R
def get_all_group_aggregations():
    # get all folder names in the output directory
    all_group_aggregations = []
    mesas = []
    # iterate over all .json files of the directory
    for file in os.listdir(FOLDER):
        # check if file is a .json file
        if not file.endswith('.json'):
            continue
        # read the json file
        district_name = file.split('.')[0]  # remove the .json extension
        # print(f"district_name = {district_name}")
        data = read_district(district_name, folder=FOLDER)
        # get the group aggregations
        group_agg = None
        if 'group_agg' in data:
            group_agg = data['group_agg'].copy() if isinstance(data['group_agg'], list) else [data['group_agg']]
            group_agg = group_agg_to_macro_group(group_agg)
        else:
            group_agg = ['18+']
        all_group_aggregations.append(group_agg)
        # get the number of mesas
        mesas.append(len(data['X']))
    return all_group_aggregations, mesas

# Function that creates a three-part figure:
# (1) visualizing macro-groups as age intervals,
# (2) showing their relative frequency across districts,
# (3) displaying summary statistics of the number of ballot boxes per macro-group

def triple_plot_bw():
    # Get group aggregations and number of ballot boxes from all district files
    all_group_aggregations, mesas = get_all_group_aggregations()
    
    # Convert each macro-group (e.g. ["18-39", "40-79"]) to a string index format (e.g. "0-2|3-6")
    all_group_aggregations_indexes = []
    for group_agg in all_group_aggregations:
        all_group_aggregations_indexes.append(list_age2index(group_agg))

    # Create DataFrame with aggregation info and number of ballot boxes
    df = pd.DataFrame({"Grupos": all_group_aggregations_indexes, "Mesas": mesas})

    # Compute summary statistics: count, min, max, mean, median
    df_summary = df.groupby("Grupos")["Mesas"].agg(
        cuenta="count",
        mesas_min="min",
        mesas_max="max",
        mesas_mean="mean",
        mesas_median="median"
    ).reset_index()

    # Compute the percentage of each macro-group configuration
    df_summary["percentage"] = (df_summary["cuenta"] / df_summary["cuenta"].sum()) * 100

    # Count how many macro-groups are in each configuration
    df_summary["n_groups"] = df_summary["Grupos"].apply(lambda x: x.count("|") + 1)

    # Sort the summary by number of groups and group label
    df_summary = df_summary.sort_values(by=["n_groups", "Grupos"], ascending=[True, True]).reset_index(drop=True)
    df = df_summary.copy()

    # Create figure with 3 side-by-side subplots sharing the Y-axis
    fig, axes = plt.subplots(1, 3, figsize=(9, 6), gridspec_kw={'width_ratios': [1, 1, 1]}, sharey=True)

    # --------- Plot 1: Macro-group rectangles by age ranges ---------
    axes[0].grid(axis='x', linestyle='-', color='gray', alpha=0.4, zorder=0)
    for i, value in enumerate(df["Grupos"]):
        for age_range in value.split("|"):
            start, end = age_range.split("-")
            start = int(start)
            end = int(end)
            axes[0].add_patch(
                plt.Rectangle((start + 0.07, i - 0.3), end - start - 0.14, 0.6,
                              facecolor='white', edgecolor='black', linewidth=1.5, zorder=2)
            )

    axes[0].set_title("Group Aggregations", fontsize=10)
    axes[0].invert_yaxis()
    axes[0].set_xlim(-0.5, 8)
    axes[0].set_ylim(-1.0, len(df) - 0.2)
    axes[0].spines[['top', 'right', 'left']].set_visible(False)
    axes[0].spines['bottom'].set_visible(True)
    axes[0].set_xticks(range(8))
    axes[0].set_xticklabels(['18', '20', '30', '40', '50', '60', '70', '80'])
    
    # Draw grouping brackets and labels
    x_pos = -0.5
    arr_n = df["n_groups"].value_counts().sort_index().index
    arr_n_group_ac_f = df["n_groups"].value_counts().sort_index().cumsum().values - 0.7
    arr_n_group_ac_i = df["n_groups"].value_counts().sort_index().cumsum().values - df["n_groups"].value_counts().sort_index().values - 0.3
    tics = []
    for i in range(len(arr_n)):
        axes[0].plot([x_pos, x_pos], [arr_n_group_ac_i[i], arr_n_group_ac_f[i]], color='black', lw=1.0)
        axes[0].plot([x_pos, x_pos+0.2], [arr_n_group_ac_i[i], arr_n_group_ac_i[i]], color='black', lw=1.0)
        axes[0].plot([x_pos, x_pos+0.2], [arr_n_group_ac_f[i], arr_n_group_ac_f[i]], color='black', lw=1.0)
        tics.append((arr_n_group_ac_i[i] + arr_n_group_ac_f[i]) / 2)

    axes[0].set_yticks(tics)
    axes[0].set_yticklabels(arr_n)
    axes[0].tick_params(axis='y', which='both', length=0)
    axes[0].set_xlabel("Age", fontsize=10, labelpad=10)
    axes[0].set_ylabel("Number of macro groups in the group aggregation", fontsize=10, labelpad=10)

    # --------- Plot 2: Waterfall bar plot of group frequency ---------
    df_1 = df.groupby("n_groups")["percentage"].agg(cuenta="count", suma="sum").reset_index()
    df_1["pct_cum_sum"] = df_1["suma"].cumsum()
    df_1["pct_cum_sum_i"] = df_1["pct_cum_sum"] - df_1["suma"]
    df_1["n_cum_sum"] = df_1["cuenta"].cumsum()
    df_1["n_cum_sum_i"] = df_1["n_cum_sum"] - df_1["cuenta"]

    for i, value in enumerate(df["percentage"]):
        start = sum(df["percentage"][:i])
        axes[1].barh(i, value, left=start, height=0.99, color='red', align='center')

    for _, row in df_1.iterrows():
        axes[1].add_patch(plt.Rectangle(
            (row["pct_cum_sum_i"], row["n_cum_sum_i"] - 0.5), row["suma"], row["cuenta"],
            facecolor='red', alpha=0.2))

    axes[1].set_title("Market Share", fontsize=10)
    axes[1].tick_params(left=False)
    axes[1].set_xlim(0, 100)
    axes[1].set_ylim(-1.0, len(df) - 0.2)
    axes[1].set_xlabel("Percentage", fontsize=10, labelpad=10)

    # --------- Plot 3: Horizontal error bars for ballot boxes ---------
    for i, (start, end, mid) in enumerate(zip(df["mesas_min"], df["mesas_max"], df["mesas_mean"])):
        axes[2].hlines(i, start, end, color='black')
        axes[2].plot(start, i, 'o', markerfacecolor='white', markeredgecolor='black', markersize=4)
        axes[2].plot(end, i, 'o', markerfacecolor='white', markeredgecolor='black', markersize=4)
        axes[2].plot(mid, i, marker='D', color='red', markeredgecolor='black', markersize=4)

    axes[2].set_title("Ballot Boxes", fontsize=10)
    axes[2].invert_yaxis()
    axes[2].set_ylim(-1.0, len(df) - 0.2)
    axes[2].tick_params(left=False)
    axes[2].set_xlabel("Number of ballot boxes [min-avg-max]", fontsize=10, labelpad=10)

    # Final layout and export
    plt.tight_layout()
    plt.savefig("figures/fig5-cascade.pdf")
    plt.show()
    
if __name__ == '__main__':
    triple_plot_bw()
    