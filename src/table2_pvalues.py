import os
import numpy as np
from aux_functions import load_pvalue_df

FOLDER_TABLES = "tables"
FOLDER_DISTRICT_RESULTS = os.path.join("output", "results_districts")

def calculate_pvalue_ranges(df_pais, image_path, write=True):
    """
    Generate a LaTeX table summarizing the number and percentage of ballot boxes
    with p-values below specified thresholds (10^0 to 10^-7).

    Parameters:
        df_pais (pd.DataFrame): Main dataset with "P-VALOR" column.
        image_path (str): File path to save the LaTeX table.
        write (bool): Whether to write the LaTeX code to file.
    """
    p_values = df_pais["P-Value"].values

    # Begin LaTeX table
    table = "\n\\begin{table}[H]\n"
    table += "\\centering\n"
    table += "\\small\n"
    table += "\\renewcommand{\\arraystretch}{1.2}\n"
    table += "\\begin{tabular}{lrr}\n"
    table += "\\toprule\n"
    table += "& \\multicolumn{2}{c}{Ballot boxes} \\\\\n"
    table += "\\cmidrule{2-3}\n"
    table += "p-value Range & \\multicolumn{1}{c}{Number} & \\multicolumn{1}{c}{Percentage} \\\\\n"
    table += "\\midrule\n"

    for i in range(0, -8, -1):
        p_val_range = f"$\\leq 10^{{{i}}}$"
        count = np.sum(p_values <= 10**i)
        percentage = count / len(p_values) * 100
        table += f"{p_val_range} & {count:,} & {percentage:.2f} \\\\\n"

    table += "\\midrule\n"
    table += "\\end{tabular}\n"
    table += "\\caption{p-value count in the 2021-GCE.}\n"
    table += "\\label{tab:p-val-pais}\n"
    table += "\\end{table}\n"

    print(table)

    if write:
        with open(os.path.join(image_path, "table2.txt"), "w", encoding="utf-8") as f:
            f.write(table)


def main():
    os.makedirs(FOLDER_TABLES, exist_ok=True)
    
    df_pais = load_pvalue_df()

    calculate_pvalue_ranges(
        df_pais,
        image_path=FOLDER_TABLES,
        write=True,
    )


if __name__ == "__main__":
    main()
