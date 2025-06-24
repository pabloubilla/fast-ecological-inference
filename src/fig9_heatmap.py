import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import colors
from aux_functions import read_district, load_pvalue_df, group_agg_to_macro_group

CANDIDATE_LABELS = [
    "G.B",
    "J.K",
    "Y.P",
    "S.S",
    "E.A",
    "M.E",
    "F.P",
    "N.B",
]
IMAGES_DIR = "figures/"
FOLDER_DISTRICT_RESULTS = os.path.join("output", "results_districts")

COLUMN_DISTRICT = "District"
COLUMN_BALLOTBOX = "Ballot-box ID"
COLUMN_PVALUE = "P-Value"
COLUMN_NUM_BALLOTBOXES = "Number of Ballot-boxes"

def plot_district_heatmap(df_pais, image_dir, max_pval=8, seed=42):
    """Generate and save heatmap for selected districts based on voting data and p-values."""
    np.random.seed(seed)

    # Select potential districts with very low p-values
    low_p = (
        df_pais[COLUMN_DISTRICT][df_pais[COLUMN_PVALUE] <= 10 ** (-max_pval)]
        .drop_duplicates()
        .to_numpy()
    )

    original_rc_params = plt.rcParams.copy()
    plt.rcParams.update({"font.size": 8})
    for circ in low_p:
        # plot only for district: "PUDAHUEL"
        if circ != "PUDAHUEL":
            continue
        try:
            district_result = read_district(district_name = circ, folder=FOLDER_DISTRICT_RESULTS)

            C = np.array(district_result["X"]).shape[1]
            
            map_dif = sns.diverging_palette(
                -50, 130, s=100, l=75, sep=25, center="light", as_cmap=True
            )
            
            df_circ = df_pais[df_pais[COLUMN_DISTRICT] == circ].copy()

            matrizX = np.array(district_result["X"])
            for i in range(C):
                df_circ[CANDIDATE_LABELS[i]] = matrizX[:, i]

            expected_votes = np.einsum(
                "bg,gc->bc",
                np.array(district_result["W_agg"]),
                np.array(district_result["prob"]),
            )
            expected_votes = (
                expected_votes
                * np.array(district_result["X"]).sum(axis=1, keepdims=True)
                / np.array(district_result["W_agg"]).sum(axis=1, keepdims=True)
            )

            for i, c in enumerate(CANDIDATE_LABELS):
                df_circ[f"DIF_{c}"] = df_circ[c] - expected_votes[:, i]
            dif_CANDIDATES = np.array([f"DIF_{c}" for c in CANDIDATE_LABELS])

            groups = group_agg_to_macro_group(district_result["group_agg"])
            
            for i, g in enumerate(groups):
                df_circ[g] = np.array(district_result["W_agg"])[:, i]
            
            df_circ[COLUMN_PVALUE] = district_result["p_values"]

            min_index = df_circ[COLUMN_PVALUE].idxmin()
            P_VALUE_SAMPLING_THRESHOLD = 0.01
            eligible_for_sampling_indexes = df_circ[
                df_circ[COLUMN_PVALUE] >= P_VALUE_SAMPLING_THRESHOLD
            ].index
            other_indexes = eligible_for_sampling_indexes.difference([min_index])

            try:
                sampled_indexes = np.random.choice(other_indexes, size=9, replace=False)
            except ValueError:
                print(f"Not enough tables in {circ} to sample 9 additional ones.")
                continue

            sampled_indexes = np.append(sampled_indexes, min_index)
            sampled_indexes = list(sampled_indexes)
            last_idx = sampled_indexes[-1]
            insert_pos = np.random.randint(0, len(sampled_indexes) - 1)
            sampled_indexes = sampled_indexes[:-1]
            sampled_indexes.insert(insert_pos, last_idx)

            df_heatmap = df_circ.loc[sampled_indexes].copy()
            df_heatmap = df_heatmap.set_index(COLUMN_BALLOTBOX)

            df_heatmap_for_coloring = df_heatmap[[COLUMN_PVALUE]].copy()
            df_heatmap_for_coloring.loc[
                df_heatmap_for_coloring[COLUMN_PVALUE] <= 10 ** (-max_pval), COLUMN_PVALUE
            ] = 10 ** (-max_pval)

            annotations = np.empty_like(df_heatmap[[COLUMN_PVALUE]].values, dtype=object)

            for i, p_val in enumerate(df_heatmap[COLUMN_PVALUE].values):
                if p_val == 0 or p_val < 10 ** (-max_pval):
                    annotations[i, 0] = r"<$10^{-8}$"
                else:
                    annotations[i, 0] = f"{p_val:.2f}"

            w_1, w_2 = 0.4, 0.3
            fig, ax = plt.subplots(
                1,
                4,
                sharey=True,
                figsize=(
                    w_1 * (2 * C + len(groups) + 2),
                    w_2 * (2 + len(df_heatmap)),
                ),
                width_ratios=[C, C, len(groups), 2],
            )
            plt.subplots_adjust(top=len(df_heatmap) / (2 + len(df_heatmap)), wspace=0.1)

            ax[0].set_title("Votes", fontsize=8)
            sns.heatmap(
                df_heatmap[CANDIDATE_LABELS].astype(int),
                cmap="Reds",
                cbar=False,
                fmt="g",
                annot=True,
                annot_kws={"fontsize": 8},
                ax=ax[0],
                xticklabels=CANDIDATE_LABELS,
            )
            ax[0].tick_params(axis="y", rotation=0, labelsize=8)
            ax[0].tick_params(axis="x", labelsize=8)
            ax[0].set_ylabel("Ballot-box id", fontsize=8)
            ax[0].set_xlabel("Candidate", fontsize=8)

            ax[1].set_title("Votes minus Expected Votes", fontsize=8)
            sns.heatmap(
                df_heatmap[dif_CANDIDATES].astype(int),
                cmap="PiYG",
                cbar=False,
                fmt="g",
                annot=True,
                annot_kws={"fontsize": 8},
                ax=ax[1],
                center=0,
                xticklabels=CANDIDATE_LABELS,
            )
            ax[1].set_xlabel("Candidate", fontsize=8)
            ax[1].tick_params(axis="x", labelsize=8)

            ax[2].set_title("Voters", fontsize=8)
            sns.heatmap(
                df_heatmap[groups].astype(int),
                cmap="Blues",
                cbar=False,
                fmt="g",
                annot=True,
                annot_kws={"fontsize": 8},
                ax=ax[2],
            )
            ax[2].set_xlabel("Age Range", fontsize=8)
            ax[2].tick_params(axis="x", labelsize=8)

            ax[3].set_title("p-value", fontsize=8)
            sns.heatmap(
                df_heatmap_for_coloring,
                cmap="Purples_r",
                cbar=False,
                annot=annotations,
                fmt="",
                annot_kws={"fontsize": 8},
                ax=ax[3],
                xticklabels=False,
                norm=colors.LogNorm(vmin=10 ** (-max_pval), vmax=1),
            )

            for i, text in enumerate(ax[3].texts):
                original_p_value = df_heatmap[COLUMN_PVALUE].iloc[i]
                p_value_for_coloring = df_heatmap_for_coloring[COLUMN_PVALUE].iloc[i]

                if original_p_value == 0 or original_p_value < 10 ** (-max_pval):
                    text.set_color("white")
                else:
                    log10_val = np.log10(p_value_for_coloring)
                    log10_vmin = np.log10(10 ** (-max_pval))
                    log10_vmax = np.log10(1)
                    if log10_val < (log10_vmin + log10_vmax) / 2:
                        text.set_color("white")
                    else:
                        text.set_color("black")

            for ix in range(1, 4):
                ax[ix].tick_params(left=False)
                ax[ix].set_ylabel("")

            plt.savefig(
                os.path.join(image_dir, f"fig9-heatmap.pdf"), bbox_inches="tight"
            )
            plt.show()
        except:
            print(f"Could not process district {circ}")

    plt.rcParams.update(original_rc_params)


def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    df_pais = load_pvalue_df()
    plot_district_heatmap(df_pais, IMAGES_DIR, max_pval=8, seed=46)


if __name__ == "__main__":
    main()
