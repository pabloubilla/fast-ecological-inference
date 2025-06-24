import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import itertools

def load_data(G_list, C_list, B, I, step_size, samples, seed_list, output_folder):
    """Loads data from pickle files for all combinations of G and I."""
    Z_dict = {}
    for G in G_list:
        for C in C_list:
            Z_dict[G, C] = []
            for s in seed_list:
                # Z_instances/C2G2v2/C2G2seed1.pkl
                # with open(f"{output_folder}/C{C}G{G}v2/C{C}G{G}seed{s}.pkl", "rb") as f:
                # # with open(f"Z_instances/Z_instance_G{G}_I{I}_M{M}_J{J}_step{step_size}_S{samples}_seed{s}_sequence.pickle", 'rb') as f:
                #     data = np.array(pickle.load(f))
                #     # Flatten the last two dimensions out of four dimensions
                #     data = data[:,:,:,:]
                #     data = data.reshape((data.shape[0], data.shape[1], data.shape[2] * data.shape[3]))

                data = pd.read_parquet(f'{output_folder}/C{C}_G{G}/C{C}G{G}seed{s}.parquet', engine='pyarrow').values
                data = data.reshape((B,samples,G*C))

                Z_dict[G, C].extend(data)
            Z_dict[G, C] = np.array(Z_dict[G, C])
    return Z_dict

def calculate_mean_correlation(Z_dict, G_list, C_list, S_lim):
    """Calculates the mean correlation for each step size."""
    proms = {}
    for G, C in itertools.product(G_list, C_list):
        print(f'Running G={G} C={C}')
        Z = Z_dict[G, C]
        proms[G, C] = np.zeros((S_lim, Z.shape[0]))
        for m, Z_s in enumerate(Z):
            for s in range(S_lim):
                proms[G, C][s, m] = np.mean([
                    np.abs(np.corrcoef(Z_s[:-(s+1), i], Z_s[(s+1):, i])[0, 1]) for i in range(Z_s.shape[1])
                ])
        proms[G, C] = np.nanmean(proms[G, C], axis=1)
    return proms

def plot_results(proms, G_list, C_list, S_lim, step_size, img_path):
    """Plots the results of the mean correlations."""
    line_styles = ['--', '-']
    marker_styles = ['^', '^', 'o', 'o']
    fill_styles = [None]
    markerface_colors = ['white', None]

    for idx, (G, I) in enumerate(itertools.product(G_list, C_list)):
        line_style = line_styles[idx % len(line_styles)]
        marker_style = marker_styles[idx % len(marker_styles)]
        fillstyle = fill_styles[idx % len(fill_styles)]
        markerfacecolor = markerface_colors[idx % len(markerface_colors)]

        plt.plot(step_size, np.log10(proms[G, I]), label=f'G = {G}, C = {I}', linestyle=line_style,
                 marker=marker_style, markersize=6, fillstyle=fillstyle, markevery=10, markerfacecolor=markerfacecolor)

    plt.legend()
    plt.xlabel('Step size')
    plt.ylabel('Correlation')

    # Customize y-axis ticks and labels
    values_to_show = [1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002]
    y_ticks = [np.log10(v) for v in values_to_show]
    y_ticklabels = [str(v) for v in values_to_show]
    plt.yticks(y_ticks, y_ticklabels)

    # Save and show the figure
    plt.savefig(img_path, bbox_inches='tight')
    plt.show()

def main():
    """Main function to load data, calculate correlations, and plot results."""
    G_list = [2, 4]
    C_list = [2, 10]
    B = 50
    I = 100
    step_size_value = 100
    samples = 10000
    seed_list = [i for i in range(1, 21)]
    S_lim = 100
    step_size = [i * step_size_value for i in range(1, S_lim + 1)]
    output_folder = 'output/figureH'
    img_path = 'figures/figH-z-correlation.pdf'

    # Load the data
    print('Loading Z instances')
    Z_dict = load_data(G_list, C_list, B, I, step_size_value, samples, seed_list, output_folder)

    # Calculate mean correlations
    print('Calculating correlations')
    proms = calculate_mean_correlation(Z_dict, G_list, C_list, S_lim)

    # Plot the results
    plot_results(proms, G_list, C_list, S_lim, step_size, img_path)
    print('Finished plotting')

if __name__ == "__main__":
    main()