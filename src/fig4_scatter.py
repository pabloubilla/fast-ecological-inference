import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from aux_functions import read_district, group_agg_to_macro_group

FOLDER = os.path.join("output", "figure4")

def plot_ll_vs_std(district_list, group_combinations_list):
    colors = ['green', 'orange', 'purple']
    size_list = [40, 90, 140, 200, 260]

    df_groups = []

    for district in district_list:
        print(f"district = {district}")
        for group_combination in group_combinations_list:
            print(f"group_combination = {group_combination}")
            # Load the district data
            last_name = "_"+"_".join(map(str, group_combination))
            district_data = read_district(district, last_name=last_name, folder=FOLDER)
            x = district_data['X']
            B = len(x)
            ll = district_data['logLik']
            sd_array = np.array(district_data['sd'], dtype=float)
            p_std = np.nanmax(sd_array)
            df_groups.append([district.title(), B, group_combination, ll, p_std, 0])    

    df_groups = pd.DataFrame(df_groups, columns = ['District', 'B', 'group_combinations', 'll', 'p_std', 'alphas'])

    # Some formatting for a nice plot
    df_groups['G'] = df_groups['group_combinations'].apply(len) # number of groups
    df_groups['ll-B'] = df_groups['ll'] / df_groups['B'] # average ll
    df_groups['District'] = df_groups['District'].astype(str) + ' (B = ' + df_groups['B'].astype(str) +')'
    df_groups['# Agg Groups'] = df_groups['G']
    age_ranges = [",".join(group_agg_to_macro_group(group_combination)) for group_combination in group_combinations_list]
    df_groups['Group aggregation'] = len(district_list)*age_ranges
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 5.5))

    # Plot scatter
    scatter = sns.scatterplot(
        data=df_groups, 
        x='ll-B', 
        y='p_std',
        hue='District', 
        size='Group aggregation', 
        sizes=size_list, 
        legend='brief',  # Enable legend generation
        palette=colors,
        alpha=1, 
        ax=ax
    )

    # Set axis labels
    ax.set_xlabel('Average Log-likelihood', fontsize=12)
    ax.set_ylabel('Maximum standard deviation', fontsize=12)

    # Set axis limits
    ax.set_ylim([-0.005, 0.45])
    ax.set_xlim([-22.0, -14.0])

    # Adjust tick parameters
    ax.tick_params(axis='both', which='major', labelsize=12)

    # Get handles and labels for the legend
    h,l = ax.get_legend_handles_labels()
    l1 = ax.legend(h[:len(district_list)+1],l[:len(district_list)+1], loc='upper left', fontsize = 12, bbox_to_anchor=(1.05, 0.9))
    l2 = ax.legend(h[len(district_list)+1:],l[len(district_list)+1:], loc='center left', fontsize = 12, bbox_to_anchor=(1.05, 0.4))
    ax.add_artist(l1) 
    plt.tight_layout()
    plt.subplots_adjust(right=0.55)
    
    # Show and save the plot
    plt.show()
    fig.savefig('figures/fig4-scatter.pdf', bbox_inches='tight')
    plt.close()

def main():
    # Plot ll vs std
    district_list = ['CANCURA', 'EL BELLOTO', 'PROVIDENCIA']
    group_combinations_list = [[8],
                               [4,8],
                               [2,4,6,8],
                               [2,3,4,5,6,8],
                               [1,2,3,4,5,6,7,8]]
    plot_ll_vs_std(district_list, group_combinations_list)

if __name__ == '__main__':
    main()
