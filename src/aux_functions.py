import warnings
import json
import os
import pandas as pd
import numpy as np

# auxiliary functions

warnings.filterwarnings("ignore", category=RuntimeWarning)

# function to read simulated_instances into a dataframe
def read_simulated_instances(
    output_dir='output/simulated_instances',
    I_list=[100],
    B_list=[50],
    G_list=[2, 3, 4],
    C_list=[2, 3, 4, 5, 10],
    lambda_list=[0.5],
    seed_list=list(range(1, 21)),
    methods=['exact', 'mcmc_100', 'mcmc_1000', 'mvn_cdf', 'mvn_pdf', 'mult']
):
    df_rows = []

    for I in I_list:
        for B in B_list:
            for G in G_list:
                for C in C_list:
                    for lambda_ in lambda_list:
                        for method in methods:
                            for seed in seed_list:
                                path = os.path.join(
                                    output_dir,
                                    f'I{I}_B{B}_G{G}_C{C}_lambda{int(100 * lambda_)}',
                                    method,
                                    f'{seed}.json'
                                )
                                try:
                                    with open(path, 'r') as f:
                                        data = json.load(f)

                                    p_real = np.array(data['real_prob'])
                                    p_est = np.array(data['prob'])

                                    mean_error = np.mean(np.abs(p_real - p_est))
                                    max_error = np.max(np.abs(p_real - p_est))
                                    time = data['time']
                                    simulate_time = 0 if 'simulate' in method else np.nan
                                    iterations = data['iterations']
                                    status = data['status']

                                    df_rows.append([
                                        I, B, G, C, lambda_, method, seed,
                                        time, simulate_time, iterations, status,
                                        mean_error, max_error
                                    ])
                                except Exception as e:
                                    # uncomment for debugging
                                    # print(f"[!] Error reading {path}: {e}")
                                    continue

    columns = ['I', 'B', 'G', 'C', 'lambda', 'method', 'seed',
               'time', 'simulate_time', 'iterations', 'status',
               'mean_error', 'max_error']
    
    return pd.DataFrame(df_rows, columns=columns)


def read_district(district_name, last_name="", folder=""):
    """
    Read the JSON file for a given district.

    Parameters:
        district_name (str): Name of the district.
        last_name (str): Optional last name to append to the file name.
        folder (str): Optional folder path to look for the file.

    Returns:
        dict: Parsed JSON content of the district results.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
    """
    filename = f"{district_name}{last_name}.json"
    district_file = os.path.join(folder, filename)

    if not os.path.exists(district_file):
        raise FileNotFoundError(f"District {district_name} not found at '{district_file}'.")

    with open(district_file, "r", encoding="utf-8") as f:
        return json.load(f)

def load_pvalue_df():
    """
    Load all election data from all disrtricts with p-value information

    Returns:
        pd.DataFrame: Combined DataFrame with p-values and ballotbox info.
    """
    RESULT_PATH = os.path.join("output","results_districts")
    COLUMN_DISTRICT = "District"
    COLUMN_BALLOTBOX = "Ballot-box ID"
    COLUMN_PVALUE = "P-Value"
    COLUMN_NUM_BALLOTBOXES = "Number of Ballot-boxes"

    if not os.path.exists(RESULT_PATH):
        print("No results folder found. Please ensure JSONs are in ", RESULT_PATH)
        return pd.DataFrame()

    # Extract district names from .json files
    districts = [
        f.split(".")[0] for f in os.listdir(RESULT_PATH) if f.endswith(".json")
    ]

    df_pais = pd.DataFrame(
        columns=[
            COLUMN_DISTRICT,
            COLUMN_BALLOTBOX,
            COLUMN_PVALUE,
            COLUMN_NUM_BALLOTBOXES,
        ]
    )
    
    for dist in districts:
        data = read_district(dist, folder=RESULT_PATH)

        ballots = data.get("ballotbox_id", [])
        pvals = data.get("p_values", [])
        
        # check that ballots is not a list
        if not isinstance(ballots, list):
            ballots = [ballots]
        
        df_dist = pd.DataFrame(
            {
                COLUMN_DISTRICT: dist,
                COLUMN_BALLOTBOX: ballots,
                COLUMN_PVALUE: pvals,
                COLUMN_NUM_BALLOTBOXES: len(pvals),
            }
        )

        df_pais = pd.concat([df_pais, df_dist], ignore_index=True)

    return df_pais

# Function that converts an age range string like "18-29" to index values (e.g., (0, 1))
def age2index(age, return_str=False):
    # age : string in the format "18-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80+", or similar
    age_ranges_from = ["18", "20", "30", "40", "50", "60", "70", "80"]
    age_ranges_to = ["-19", "-29", "-39", "-49", "-59", "-69", "-79", "+"]
    
    # Find the index corresponding to the starting value of the age range
    for i, age_from in enumerate(age_ranges_from):
        if age_from in age:
            indice_from = i
            break
    
    # Find the index corresponding to the ending value of the age range
    for i, age_to in enumerate(age_ranges_to):
        if age_to in age:
            indice_to = i + 1
            break
    
    # Return either a tuple of indices or a formatted string
    if return_str:
        return f"{indice_from}-{indice_to}"
    else:
        return indice_from, indice_to

# Function that maps a list of age range strings to corresponding index strings separated by "|"
def list_age2index(list_age):
    # list_age : list of strings with format like "18-19", "20-29", ..., "80+"
    return "|".join([str(age2index(age, return_str=True)) for age in list_age])

# Function to convert index ranges into age range strings
def macro_group_notation(index_from, index_to):
    # index_from and index_to are integers from 0 to 7
    # Representing predefined age ranges
    age_ranges_from = ["18", "20", "30", "40", "50", "60", "70", "80"]
    age_ranges_to = ["-19", "-29", "-39", "-49", "-59", "-69", "-79", "+"]
    return f"{age_ranges_from[index_from]}{age_ranges_to[index_to]}"

# Function that transforms a group aggregation (group_agg) from R notation 
# to macro-group notation (e.g., [3, 7, 8] → ["18-39", "40-79", "80+"])
def group_agg_to_macro_group(group_agg):
    # Input: group_agg is a list of integers between 1 and 8 (inclusive)
    # Output: macro_group is a list of age group strings like "18-39"
    macro_group = []
    index_from = 0  # Start of the current macro-group
    for i in range(len(group_agg)):
        index_to = group_agg[i] - 1  # End index for current macro-group
        #print(f"index_from: {index_from}, index_to: {index_to}")
        macro_group.append(macro_group_notation(index_from, index_to))
        index_from = index_to + 1  # Next macro-group starts after this one
    return macro_group


