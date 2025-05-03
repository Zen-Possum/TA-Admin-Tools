# ======================================================================================================================
# DivideMessaging.py takes a file and divides it into equal subsets for a list of admins. Written by ZenPossum :)
# ======================================================================================================================

import pandas as pd
import numpy as np

# Parameters
file_name = 'Data/FilteredMembersBulgaria.csv'
admins = ['Louise', 'Bruce', 'Steve', 'Jim', 'Aidan']

# Read file
filtered_members = pd.read_csv(file_name)
n_rows, n_cols = filtered_members.shape
n_folds = len(admins)

# Add link column and divide into folds
filtered_members['link'] = filtered_members['username'].map(lambda x: f'https://www.chess.com/member/{x}')
# shuffled = filtered_members.sample(frac=1)
for i in range(n_folds):
    fold = np.array_split(filtered_members, n_folds)[i]
    # fold = fold_shuffled.sort_values('rating', ascending=False)
    fold.to_csv(f'Data/Messaging{admins[i]}.csv', index=False)
