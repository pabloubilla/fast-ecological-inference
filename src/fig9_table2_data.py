# compute p-values

# the code computes the p-values for each ballot box in every district
# the estimated probabilities are the ones obtained with R using fastei
# it reas the .json files from results_district, computes the p-values
# for each ballot box and saves the results in a new .json file in results_pvalues

import json
import os
import numpy as np
from tqdm import tqdm
from p_val_mult import compute_thresholds, compute_p_value_m_mult_threshold
from aux_functions import read_district

FOLDER = os.path.join('output', 'results_districts')

# function that computes the voting probabilties of a district
def compute_voting_probabilities(district_results):
    W_agg = np.array(district_results['W_agg'])
    p_agg_est = np.array(district_results['prob'])
    total_voters = W_agg.sum(axis=1)
    probabilities = (W_agg @ p_agg_est) / total_voters[:, np.newaxis]
    print(f"B = {probabilities.shape[0]}")
    return probabilities

# function that analyze the ballot boxes of a district
def analyze_ballot_boxes(district_name, S_min=3, S_max=5, thresholds=None, lgac_n=None, 
                         seed=None, save_json=True, verbose = False):

    # Set default thresholds if not provided
    if thresholds is None:
        mu_power = 5
        alpha_power = 7
        thresholds = compute_thresholds(S_min, S_max, mu_power, alpha_power)
    # Set default lgac_n if not provided
    if lgac_n is None:
        lgac_n = np.array([sum([np.log(max(k, 1)) for k in range(j + 1)]) for j in range(1000 + 1)])
    # Set default seed if not provided
    if seed is not None:
        np.random.seed(42)  # Set seed for reproducibility in the main function
    
    # read the district results
    district_result = read_district(district_name, folder=FOLDER)
    # compute the voting probabilities
    probabilities = compute_voting_probabilities(district_result)
    X = np.array(district_result['X'])
    B, _ = X.shape

    # compute p-values
    p_values = []
    p_values_trials = []
    current_seed = seed
    if verbose:
        print(f"{'Disctrict':20.30s}\tp-value\ttrials")
    for b in range(B):
        x = X[b, :]
        r = probabilities[b, :]
        log_p = np.where(r > 0, np.log(r), 0)
        current_seed += 1
        pval, trials = compute_p_value_m_mult_threshold(x, r, S_min, S_max, thresholds, log_p = log_p, lgac_n = lgac_n, seed = current_seed)
        p_values.append(pval)
        p_values_trials.append(trials)
        if verbose:
            print(f'{district_name:20.30s}\t{pval}\t{trials}')
    # add the pvalues to the district result
    district_result['p_values'] = p_values
    district_result['p_values_trials'] = p_values_trials

    # save the .json
    if save_json:
        # save the results in a json file
        results_file = os.path.join(FOLDER, f'{district_name}.json')
        with open(results_file, 'w') as f:
            json.dump(district_result, f, ensure_ascii=False, indent=4)
    
# function that computes the p-values for all district
def compute_all_district_pvalues(load_bar = False, seed = None, save_json = False):

    # Calculate thresholds only once and pass them to inner functions
    S_min = 3
    S_max = 8
    mu_power = 5
    alpha_power = 7
    thresholds = compute_thresholds(S_min, S_max, mu_power, alpha_power)
    lgac_n = np.array([sum([np.log(max(k, 1)) for k in range(j + 1)]) for j in range(1000 + 1)])
        
    # iterate over all districts in the districts result folder
    districts_name = [f.split('.')[0] for f in os.listdir(FOLDER) if f.endswith('.json')]
    for district_name in tqdm(districts_name, 'Processing district p-values', disable = not load_bar):
        print(f"Processing district: {district_name}")
        analyze_ballot_boxes(district_name, S_min = S_min, S_max = S_max, thresholds = thresholds, lgac_n = lgac_n, 
                             seed = seed, save_json = save_json, verbose = False)

    
# main
if __name__ == "__main__":
    compute_all_district_pvalues(load_bar = True, seed = 42, save_json = True)
    
