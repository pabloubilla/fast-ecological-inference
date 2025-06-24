import numpy as np
import pickle
import matplotlib.pyplot as plt
import os
import json
import pandas as pd

results_folder = "results/"

I_list = [100] # personas
B_list = [50] # mesas
G_list = [2,3,4] # grupos
C_list = [2,3,4] # candidatos
# G=2 y C=5 también 
lambda_list = [0.5]
# cv_list = [1000, 10000]
cv_list = [1000]
seed_list = [i+1 for i in range(20)]
# seed_list = [i+1 for i in range(20)]

instances = []
n_instances = len(I_list)*len(B_list)*len(G_list)*len(C_list)*len(seed_list)
EM_method_names = ["exact"]

df_differences = []

# read instances
for I in I_list:
    for M in B_list:
        for G in G_list:
            for C in C_list:
                for lambda_ in lambda_list:
                    for cv in cv_list:
                        for seed1 in seed_list:
                            for seed2 in seed_list[seed1:]:
                                # results/I100_B50_G2_C3_lambda50/exact/1_pinit1.json
                                json_path_1 = f'I{I}_B{M}_G{G}_C{C}_lambda{int(100*lambda_)}/exact/1_pinit{seed1}.json'
                                file_path_1 = os.path.join(results_folder, json_path_1)
                                if os.path.exists(file_path_1):
                                    # read json
                                    with open(file_path_1, 'r') as f:
                                        instance1 = json.load(f)
                                    p_est1 = np.array(instance1['prob'])

                                else:
                                    print("File not found:", file_path_1)
                                # same for seed2
                                json_path_2 = f'I{I}_B{M}_G{G}_C{C}_lambda{int(100*lambda_)}/exact/1_pinit{seed2}.json'
                                file_path_2 = os.path.join(results_folder, json_path_2)
                                if os.path.exists(file_path_2):
                                    # read json
                                    with open(file_path_2, 'r') as f:
                                        instance2 = json.load(f)
                                    # print(instance)
                                    p_est2 = np.array(instance2['prob'])

                                # dif_instance = np.max(np.abs(p_est1 - p_est2))
                                dif_instance = np.mean(np.abs(p_est1 - p_est2))
                                # frobenius norm
                                # dif_instance = np.linalg.norm(p_est1 - p_est2)
                                # print(seed1, seed2, dif_instance)
                                # append the dif
                                df_differences.append([I,M,G,C,lambda_,cv,seed1,seed2,dif_instance])
                                # else:
                                #     print("File not found:", file_path)
                                #     print("File path:", file_path)
                                #     print("")

df_differences = pd.DataFrame(df_differences, columns=['I','M','G','C','lambda','cv','seed1','seed2','dif_instance'])


# pasar a latex la tabla
df_differences_latex = df_differences[df_differences['cv'] == 1000]
df_differences_latex = df_differences[['G', 'C', 'dif_instance']]
# round to 4 decimals latex
print(df_differences_latex.groupby(['G','C']).agg(
    ['mean', 'std', 'max'])[['dif_instance']].round(4).to_latex(
        float_format="{:0.4f}".format))