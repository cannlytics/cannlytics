
# External imports:
import pandas as pd

# TODO: Read curated Nevada lab result data.
stats_dir = 'D://data/nevada/results/datasets'
datafile = f'{stats_dir}/nv-results-latest.csv'
results = pd.read_csv(datafile)

# # Restrict to flower.
# flower_types = ['Marijuana Flowers/Buds', 'Small/Popcorn Buds']
# nv_flower = results[results['product_type'].isin(flower_types)]
# print('Number of Nevada flower samples:', len(nv_flower))

# # # TODO: Combine the test type columns.
# # def combine_columns(df, base_col):
# #     unit_cols = [col for col in df.columns if col.startswith(base_col + ' (')]
# #     df[base_col] = df[unit_cols].bfill(axis=1).iloc[:, 0]
# #     df.drop(unit_cols, axis=1, inplace=True)
# # base_columns = [col.split(' (')[0] for col in nv_flower.columns if ' (' in col]
# # base_columns = list(set(base_columns))
# # for base_col in base_columns:
# #     combine_columns(nv_flower, base_col)

# # Drop columns containing 'Raw Plant Material' or 'Whole Wet Plant'
# columns_to_drop = [col for col in nv_flower.columns if 'Raw Plant Material' in col or 'Whole Wet Plant' in col or '(' in col]
# nv_flower.drop(columns=columns_to_drop, inplace=True)
