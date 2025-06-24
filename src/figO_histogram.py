#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


IMAGES_DIR = "figures/"
COLUMN_DISTRICT = 'Circunscripción electoral'


def plot_ballotbox_histogram(df_election, image_path=IMAGES_DIR, truncate=500):
    """
    Plot histogram of the number of ballot boxes (mesas) per district
    and save it as a PDF file.

    Parameters:
        df_election (pd.DataFrame): The dataset containing ballot box info.
        image_path (str): Output path to save the plot.
        truncate (int): Maximum value for ballot boxes to truncate (for better visualization).
    """
    # Count number of ballot boxes per district
    df_ballotbox = (
        df_election.groupby(COLUMN_DISTRICT)['Mesa'].nunique()
        .reset_index()
        .rename(columns={'Mesa': 'n_ballotbox'})
    )

    # Cap large values for visualization
    if truncate is not None:
        df_ballotbox.loc[df_ballotbox["n_ballotbox"] > truncate, "n_ballotbox"] = (
            truncate + 10
        )

    # Histogram settings
    bins = np.arange(0, truncate + 30, 25)
    plt.figure(figsize=(8, 5))
    plt.hist(
        df_ballotbox["n_ballotbox"], bins=bins, edgecolor="k", alpha=1.0, color="skyblue"
    )

    # Axis formatting
    plt.xlabel("Number of Ballot-Boxes")
    plt.ylabel("Number of Districts")
    plt.xticks(
        ticks=np.arange(0, truncate + 100, 100),
        labels=[str(i) for i in np.arange(0, truncate, 100)] + [f"{truncate}+"],
    )

    plt.grid(False)
    plt.tight_layout()

    # Save and display
    plt.savefig(image_path, bbox_inches="tight")
    plt.show()
    plt.close()




def main():

    os.makedirs(IMAGES_DIR, exist_ok=True)

    df_election = pd.read_excel('data/2021_11_Presidencial.xlsx', skiprows=6, sheet_name='Votantes efectivos en Chile')

    plot_ballotbox_histogram(
        df_election, image_path=os.path.join(IMAGES_DIR, "figO-histogram-ballotbox.pdf")
    )


if __name__ == "__main__":
    main()

