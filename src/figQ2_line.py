# Code that analyzes the heterogeneity of demographic groups across ballot boxes
# using the chi-square test on contingency tables between demographic groups and ballot boxes
# It generates a cumulative histogram plot of districts based on p-values

import pandas as pd
from scipy.stats import chi2_contingency  # chi-square test on contingency matrix
import matplotlib.pyplot as plt

COLUMN_DISTRICT = 'Circunscripción electoral'

# Custom function that receives a 2D array and computes the chi-square p-value
def test_xi_square(df_matrix):
    # remove columns with all-zero values
    if min(df_matrix.sum(axis=0)) == 0:
        df_matrix = df_matrix.drop(df_matrix.columns[df_matrix.sum(axis=0) == 0], axis=1)
    # convert dataframe to numpy array
    arr = df_matrix.to_numpy()
    # compute chi-square test
    chi2_stat, p_val, dof, expected = chi2_contingency(arr)
    return p_val

# Performs chi-square test on contingency matrix for each district
def test_xi_square_per_district():
    # read Excel file
    voters = pd.read_excel('data/2021_11_Presidencial.xlsx', skiprows=6, sheet_name='Votantes efectivos en Chile')

    # aggregate number of voters for each district-ballot box-age range
    voters = voters.groupby([COLUMN_DISTRICT, 'Mesa', 'Rango etario']).sum('Votantes').reset_index()

    # get age range labels
    age_ranges = voters['Rango etario'].unique()
    
    # pivot the table to have age ranges as columns
    voters = voters.pivot_table(index=[COLUMN_DISTRICT, 'Mesa'], columns='Rango etario', values='Votantes', fill_value=0).reset_index()

    # apply chi-square test for each district
    df_pvalues = voters.groupby(COLUMN_DISTRICT)[age_ranges].apply(test_xi_square).reset_index(name='pvalue')

    return df_pvalues

# Plot cumulative histogram of p-values for all electoral districts
def plot_chi_square_pvalues(df_p_val):
    x = [1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1]
    y = [100 * df_p_val['pvalue'].apply(lambda x: x < cut).mean() for cut in x]
    
    # create a dataframe for plotting
    df = pd.DataFrame({'x': x, 'y': y})
    print(df)

    # create the plot
    plt.figure(figsize=(8, 4))
    plt.plot(x, y, marker='o', label='Line 1')
    plt.ylim(80, 100)  # Set y-axis limits from 80% to 100%
    plt.xscale('log')
    plt.xlabel('p-values')
    plt.ylabel('Cumulative Histogram of Districts [%]')
    plt.gca().set_yticklabels(['{:.0f}%'.format(x) for x in plt.gca().get_yticks()])  # format y-axis labels as percentages
    plt.xticks(x)
    # save the plot to disk as PDF
    plt.savefig("figures/figQ2-line.pdf")
    plt.show()
    
if __name__ == '__main__':
    df_p_val = test_xi_square_per_district()
    plot_chi_square_pvalues(df_p_val)
