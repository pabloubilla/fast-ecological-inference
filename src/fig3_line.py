import numpy as np
import matplotlib.pyplot as plt
import os
from aux_functions import read_district, group_agg_to_macro_group

FOLDER = os.path.join("output", "figure3")

def plot_probabilities(district_list, group_combinations_list):
    """"
    Plot the probabilities of candidates in different districts and types.
    This function reads data from JSON files for two districts and two types of voting (individual and aggregate),
    and generates a figure with subplots for each district. Each subplot contains two axes, one for each type of voting.
    The probabilities for three candidates are plotted with different markers and line styles.
    The figure is saved as a PDF file.
    """

    district_list = ["EL GOLF", "SALTOS DEL LAJA"]
    
    candidate_label = ['Gabriel Boric', 'José A. Kast', "Franco Parisi"]
    markers = ['o', 'v', 's']
    linestyles = ['-', '--', '-.']
    candidates_used = [0, 1, 6]
    
    fig = plt.figure(constrained_layout=True, figsize=(12, 7))
    subfigs = fig.subfigures(nrows=3, ncols=1, height_ratios=[3, 3, 1])

    for idx_district, district in enumerate(district_list):
        for idx_group_combinations, group_combination in enumerate(group_combinations_list):
            # load data for the district
            last_name = "_"+"_".join(map(str, group_combination))
            district_data = read_district(district, last_name=last_name, folder=FOLDER)
            p_est = np.array(district_data['prob'])
            X = np.array(district_data['X'])

            if idx_group_combinations == 0:
                B = len(X)
                subfigs[idx_district].suptitle(f'\n {district} (B = {B})', )
                axs = subfigs[idx_district].subplots(nrows=1, ncols=2, sharey=True)
            group_names = group_agg_to_macro_group(group_combination)
            for c_ix, c in enumerate(candidates_used):
                axs[idx_group_combinations].plot(p_est[:, c], label=candidate_label[c_ix], marker=markers[c_ix], linestyle=linestyles[c_ix])

            axs[idx_group_combinations].set_xticks(range(len(group_names)), group_names)
            axs[0].set_ylim([-0.02, 1.02])
            if idx_group_combinations == 0:
                axs[idx_group_combinations].set_ylabel('Probability')

    axs_label = subfigs[2].subplots(nrows=1, ncols=1)
    for c_ix, c in enumerate(candidates_used):
        axs_label.plot([0, 0], [0, 0], label=candidate_label[c_ix], marker=markers[c_ix], linestyle=linestyles[c_ix])
    axs_label.set_frame_on(False)
    axs_label.xaxis.set_visible(False)
    axs_label.yaxis.set_visible(False)
    axs_label.legend(loc='center', ncol=3)

    # create folder if it does not exist
    os.makedirs("figures", exist_ok=True)
    plt.savefig("figures/fig3-line.pdf", bbox_inches='tight')
    plt.show()

def main():
    # Plot estimated probabilities for different group aggregations
    district_list = ["EL GOLF", "SALTOS DEL LAJA"]
    group_combinations_list = [[1,2,3,4,5,6,7,8],[2,6,8]]
    plot_probabilities(district_list, group_combinations_list)

if __name__ == '__main__':
    main()
