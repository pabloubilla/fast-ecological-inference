
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import textwrap
import pickle

IMAGES_DIR = "figures/"
COLUMN_DISTRICT = 'Circunscripción electoral'
COLUMN_SUB_DISTRICT = 'Local'
GROUPS = ['18-19', '20-29', '30-39', '40-49', '50-59','60-69', '70-79', '80+']


def group_heatmap(voters_district, sub_districts, cmap='Blues', trunc=0.7, img_path = 'fig.pdf'):
    fig, ax = plt.subplots(2, int(len(sub_districts)/2), figsize=(2*len(sub_districts), 5), sharey=True)
    cbar_ax = fig.add_axes([1.01, 0.3, 0.03, 0.4])

    for i, l in enumerate(sub_districts):
        index = i//int(len(sub_districts)/2), i%int(len(sub_districts)/2)
        group_data = voters_district[voters_district[COLUMN_SUB_DISTRICT] == l][GROUPS].T
        group_proportion = group_data / np.sum(group_data, axis=0)
        im = sns.heatmap(group_proportion, ax=ax[index], xticklabels=False, yticklabels=True,
                         cmap=cmap, cbar=True, cbar_ax=cbar_ax, vmin=0, vmax=trunc,
                         cbar_kws={"shrink": 0.3})
        if trunc < 1:
            n_trunc = int(trunc*10)
            cbar_ax.set_yticks([0.1*j for j in range(n_trunc+1)])
            cbar_ax.set_yticklabels([f'   {0.1*j:.1f}' for j in range(n_trunc)] + [f' > {0.1*n_trunc:.1f}'])
        cbar_ax.set_title('Proportion', fontsize=10, pad=10)

        if index[1] == 0:
            ax[index].set_yticklabels(GROUPS)
            ax[index].set_ylabel('Age Range')
            ax[index].tick_params(left=True)
        else:
            ax[index].tick_params(left=False)

        title = '\n'.join(textwrap.wrap(f'{l}', width=30))
        ax[index].text(0.5, 1.08, title, transform=ax[index].transAxes, va='center', ha='center')

    fig.subplots_adjust(wspace=0.15, right=0.95)


    fig.savefig(img_path, bbox_inches='tight')
    plt.show()



if __name__ == '__main__':

    img_path = 'figures/figQ1-heatmap.pdf'

    print('Loading Excel file, this can take a minute...')
    voters = pd.read_excel('data/2021_11_Presidencial.xlsx', skiprows=6, sheet_name='Votantes efectivos en Chile')
    
        # remove rows with empty age range or 0 voters

    voters = voters[~((voters['Rango etario'] == '') & (voters['Votantes'] == 0))]

    voters = voters.groupby([COLUMN_DISTRICT, COLUMN_SUB_DISTRICT, 'Mesa'] + ['Rango etario']).sum().reset_index() # group by GROUPS, there may be repeated rows (NACIONALIDAD)
    voters = voters.pivot(index = [COLUMN_DISTRICT, COLUMN_SUB_DISTRICT, 'Mesa'], columns = 'Rango etario', values='Votantes').reset_index() # long to wide
    district = 'PUENTE ALTO'
    voters_district = voters[voters[COLUMN_DISTRICT] == district]

    sub_districts = ['COLEGIO PARTICULAR PADRE JOSE KENTENICH', 'COLEGIO NUEVA ERA SIGLO XXI SEDE PUENTE ALTO ',
                'LICEO INDUSTRIAL MUNICIPALIZADO A 116 LOCAL: 1', 'COLEGIO MAIPO LOCAL: 2',
                'COLEGIO COMPAÑIA DE MARIA PUENTE ALTO LOCAL: 2', 'ESCUELA LOS ANDES LOCAL: 1']
    group_heatmap(voters_district, sub_districts, cmap='Blues', img_path=img_path)



