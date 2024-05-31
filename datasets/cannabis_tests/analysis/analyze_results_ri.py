
# === OLD ===

# data_dir = r'D:\data\public-records\Rhode Island\Rhode Island'
# data = []
# for root, dirs, files in os.walk(data_dir):
#     for file in files:
#         if 'no data' in file.lower():
#             continue
#         print('Reading:', file)
#         datafile = os.path.join(root, file)
#         if file.endswith('.csv'):
#             df = pd.read_csv(datafile, usecols=columns.keys(), encoding='latin1')  # Use 'latin1' encoding
#         elif file.endswith('.xlsx'):
#             df = pd.read_excel(datafile, usecols=columns.keys())  # Read .xlsx files correctly
#         df.rename(columns=columns, inplace=True)
#         data.append(df)
# data = pd.concat(data, ignore_index=True)
# print('Number of Rhode Island tests:', len(data))

# # Extract test_name, units, and product_type from test_type.
# data[['test_name', 'units', 'product_type']] = data['test_type'].str.extract(r'(.+?) \((.+?)\) (.+)')

# # Restrict to passed tests.
# data = data[data['status'] == True]

# # Pivot the data to get results for each sample.
# results = data.pivot_table(
#     index=['sample_id', 'producer_license_number', 'lab', 'label', 'date_tested', 'product_type'],
#     columns='test_name',
#     values='test_result',
#     aggfunc='first'
# ).reset_index()
# results['date_tested'] = pd.to_datetime(results['date_tested'], errors='coerce')
# results['month'] = results['date_tested'].dt.to_period('M')
# print('Number of Rhode Island samples:', len(results))

# # Calculate the total cannabinoids.
# ri_cannabinoids = [
#     'CBD',
#     'CBDA',
#     'Delta-9 THC',
#     'THCA',
# ]
# ri_terpenes = [
#     'Alpha-Bisabolol',
#     'Alpha-Humulene',
#     'Alpha-Pinene',
#     'Alpha-Terpinene',
#     'Beta-Caryophyllene',
#     'Beta-Myrcene',
#     'Beta-Pinene',
#     'Caryophyllene Oxide',
#     'Limonene',
#     'Linalool',
#     'Nerolidol',
# ]
# results['total_thc'] = results['Total THC']
# results['total_cbd'] = results['Total CBD']
# results['total_cannabinoids'] = results['total_thc'] + results['total_cbd']
# results['total_terpenes'] = results[ri_terpenes].sum(axis=1)

# # Calculate the total THC to total CBD ratio.
# results['thc_cbd_ratio'] = results['total_thc'] / results['total_cbd']

# # Calculate the total cannabinoids to total terpenes ratio.
# results['cannabinoids_terpenes_ratio'] = results['total_cannabinoids'] / results['total_terpenes']


# === Analyze Rhode Island lab results ===

# # Visualize market share by lab by month as a timeseries.
# market_share = results.groupby(['month', 'lab']).size().unstack().fillna(0)
# market_share = market_share.div(market_share.sum(axis=1), axis=0)
# market_share.plot.area(
#     title='Market Share by Lab by Month in Rhode Island',
#     figsize=(13, 8),
# )
# plt.xlabel('')
# plt.savefig(f'{assets_dir}/ri-market-share-by-lab-by-month.png', dpi=300, bbox_inches='tight', transparent=False)
# plt.show()

# # Visualize tests per capita by month.
# ri_population = {
#     2023: 1_095_962,
#     2022: 1_093_842,
#     2021: 1_097_092,
#     2020: 1_096_444,
#     2019: 1_058_158,
# }
# results['year'] = results['date_tested'].dt.year
# results['population'] = results['year'].map(ri_population)
# tests_per_capita = results.groupby('month').size() / (results.groupby('month')['population'].first() / 100_000)
# fig, ax = plt.subplots(figsize=(13, 8))
# tests_per_capita.plot(ax=ax, title='Cannabis Tests per 100,000 People by Month in Rhode Island')
# ax.set_ylabel('Tests per 100,000 People')
# plt.show()

# # Visualize average total THC by month over time.
# results['date_tested'] = pd.to_datetime(results['date_tested'])
# results['total_thc'] = results['total_thc'].astype(float)
# results['month'] = results['date_tested'].dt.to_period('M')
# average_total_thc = results.groupby('month')['total_thc'].mean()
# fig, ax = plt.subplots(figsize=(13, 8))
# average_total_thc.index = average_total_thc.index.to_timestamp()
# ax.plot(average_total_thc.index, average_total_thc.values, label='Monthly Average Total THC', color='royalblue', lw=5)
# ax.scatter(results['date_tested'], results['total_thc'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
# ax.set_xlabel('')
# ax.set_ylabel('Total THC (%)')
# ax.set_title('Average Total THC by Month in Rhode Island')
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
# ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
# plt.xticks(rotation=45)
# plt.ylim(5, 37.5)
# plt.savefig(f'{assets_dir}/ri-total-thc.png', dpi=300, bbox_inches='tight', transparent=False)
# plt.show()

# # Visualize average total CBD by month over time.
# results['total_cbd'] = results['total_cbd'].astype(float)
# sample = results.loc[results['total_cbd'] < 1]
# average_total_cbd = sample.groupby('month')['total_cbd'].mean()
# fig, ax = plt.subplots(figsize=(13, 8))
# average_total_cbd.index = average_total_cbd.index.to_timestamp()
# ax.plot(average_total_cbd.index, average_total_cbd.values, label='Monthly Average Total CBD', color='royalblue', lw=5)
# ax.scatter(sample['date_tested'], sample['total_cbd'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
# ax.set_xlabel('')
# ax.set_ylabel('Total CBD (%)')
# ax.set_title('Average Total CBD by Month in Rhode Island in Low CBD Samples (<1%)')
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
# ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
# plt.xticks(rotation=45)
# plt.ylim(0, 0.33)
# plt.savefig(f'{assets_dir}/ri-total-cbd.png', dpi=300, bbox_inches='tight', transparent=False)
# plt.show()