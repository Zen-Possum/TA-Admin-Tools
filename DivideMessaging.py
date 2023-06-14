import pandas as pd
import numpy as np

file_name = 'FilteredMembersUSA.csv'
admins = ['Louise', 'Bruce', 'Mick', 'Ray', 'Aidan', 'TPD']
filtered_members = pd.read_csv(file_name)
n_rows, n_cols = filtered_members.shape
n_folds = len(admins)

filtered_members['link'] = filtered_members['username'].map(lambda x: f'https://www.chess.com/member/{x}')
# shuffled = filtered_members.sample(frac=1)
filtered_members = filtered_members.loc[range(900)]
for i in range(n_folds):
    fold = np.array_split(filtered_members, n_folds)[i] # _shuffled
    #fold = fold_shuffled.sort_values('rating', ascending=False)
    fold.to_csv(f'{admins[i]}.csv', index=False)
