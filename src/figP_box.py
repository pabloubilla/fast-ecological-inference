import pandas as pd
import numpy as np
import os
import seaborn as sns 
import matplotlib.pyplot as plt
from aux_functions import read_district

B_threshold = 50
#candidates = ['GABRIEL BORIC', 'JOSE ANTONIO KAST', 'YASNA PROVOSTE', 'SEBASTIAN SICHEL', 'EDUARDO ARTES', 'MARCO ENRIQUEZ-OMINAMI', 'FRANCO PARISI', 'NULO BLANCO']
candidates = ['G.B.', 'J.K.', 'Y.P.', 'S.S.', 'E.A.', 'M.E.', 'F.P.', 'N.B.']

# get the estimated probabilities with age below and above 40 years old
def read_all_district_age():

    path = 'output/results_districts_age40'

    # Define empty DataFrame with specified columns
    df = pd.DataFrame(columns=["District", "Candidate", "X18.39", "X40.", "Number Ballots"])
    
    # iterate over all .json files of the directory
    for file in os.listdir(path):
        #file = os.listdir(path)[0]
        # check if file is a .json file
        if not file.endswith('.json'):
            continue
        # read the json file
        district_name = file.split('.')[0]  # remove the .json extension
        # read the district results
        data = read_district(district_name, folder=path)
        # get the estimated probabilities
        est_probs = data['prob']
        # create a DataFrame for the current district
        df_partial = pd.DataFrame(np.array(est_probs).transpose(), columns=["X18.39","X40."])
        df_partial['Candidate'] = candidates
        df_partial['District'] = district_name
        df_partial['Number Ballots'] = len(data['X'])
        # append the district DataFrame to the main DataFrame
        df = pd.concat([df, df_partial], ignore_index=True)
    
    df['Abs_diff'] = np.abs(df['X18.39'] - df['X40.'])
    # drop columns 'X18.39' and 'X40.'
    df.drop(columns=['X18.39', 'X40.'], inplace=True)    
    return df

# get the estimated probabilities with males and females
def read_all_district_sex():

    path = 'output/results_districts_sex'

    # Define empty DataFrame with specified columns
    df = pd.DataFrame(columns=["District", "Candidate", "M", "F", "Number Ballots"])
    
    # iterate over all .json files of the directory
    for file in os.listdir(path):
        #file = os.listdir(path)[0]
        # check if file is a .json file
        if not file.endswith('.json'):
            continue
        # read the json file
        district_name = file.split('.')[0]  # remove the .json extension
        # read the district results
        data = read_district(district_name, folder=path)
        # get the estimated probabilities
        est_probs = data['prob']
        # create a DataFrame for the current district
        df_partial = pd.DataFrame(np.array(est_probs).transpose(), columns=["M","F"])
        df_partial['Candidate'] = candidates
        df_partial['District'] = district_name
        df_partial['Number Ballots'] = len(data['X'])
        # append the district DataFrame to the main DataFrame
        df = pd.concat([df, df_partial], ignore_index=True)
    
    df['Abs_diff'] = np.abs(df['M'] - df['F'])
    # drop columns 'M' and 'F'
    df.drop(columns=['M', 'F'], inplace=True)
    return df

# function that performs the box plot of the absolute difference of voting probabilities
def do_plot():
    # extract the estimated probabilities for age and sex
    df_age = read_all_district_age()
    df_sex = read_all_district_sex()

    # adda  column indicating the case
    df_age['Case'] = 'Age: <40, ≥40'
    df_sex['Case'] = 'Sex: Men, Women'

    # Combine the two DataFrames
    df = pd.concat([df_age, df_sex], ignore_index=True)

    # Filter for districts with more than B_threshold ballot boxes
    df = df[df['Number Ballots'] > B_threshold]

    sns.boxplot(x = df['Candidate'], 
                y = df['Abs_diff'], 
                hue = df['Case'],
                flierprops=dict(marker='D', markerfacecolor='black', markersize=3, linestyle='none')  # diamante negro
                )

    plt.xlabel("Candidate", fontsize=12)
    plt.ylabel("Absolute Difference of Voting Probability", fontsize=12)
    leg = plt.legend(title="Groups:", title_fontsize='10', fontsize='10')  # Customize the legend title and labels
    leg._legend_box.align = "left"

    plt.savefig(f'figures/figP-boxplot.pdf', bbox_inches='tight')
    plt.show()

# main
if __name__ == "__main__":
    do_plot()
    
