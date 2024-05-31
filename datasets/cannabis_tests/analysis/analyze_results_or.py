


# === Analyze Oregon lab results ===

# # Visualize market share by lab by month as a timeseries.
# market_share = results.groupby(['month', 'lab_id']).size().unstack().fillna(0)
# market_share = market_share.div(market_share.sum(axis=1), axis=0)
# market_share.plot.area(
#     title='Market Share by Lab by Month in Oregon',
#     figsize=(13, 8),
#     legend=None,
# )
# plt.xlabel('')
# plt.savefig(f'{assets_dir}/or-market-share-by-lab-by-month.png', dpi=300, bbox_inches='tight', transparent=False)
# plt.show()

# # Visualize tests per capita by month.
# or_population = {
#     2023: 4_233_358,
#     2022: 4_239_379,
#     2021: 4_256_465,
#     2020: 4_245_044,
#     2019: 4_216_116,
# }
# results['year'] = results['date'].dt.year
# results['population'] = results['year'].map(or_population)
# fig, ax = plt.subplots(figsize=(13, 8))
# or_tests_per_capita = results.groupby('month').size() / (results.groupby('month')['population'].first() / 100_000)
# or_tests_per_capita.plot(ax=ax, title='Cannabis Tests per 100,000 People by Month in Oregon')
# ax.set_ylabel('Tests per 100,000 People')
# plt.show()

# # Visualize average total THC by month over time.
# results['total_thc'] = results['total_thc'].astype(float)
# average_total_thc = results.groupby('month')['total_thc'].mean()
# fig, ax = plt.subplots(figsize=(13, 8))
# average_total_thc.index = average_total_thc.index.to_timestamp()
# ax.plot(average_total_thc.index, average_total_thc.values, label='Monthly Average Total THC', color='royalblue', lw=5)
# ax.scatter(results['date'], results['total_thc'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
# ax.set_xlabel('')
# ax.set_ylabel('Total THC (%)')
# ax.set_title('Average Total THC by Month in Oregon')
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
# ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
# plt.xticks(rotation=45)
# plt.ylim(0, 45)
# plt.savefig(f'{assets_dir}/or-total-thc.png', dpi=300, bbox_inches='tight', transparent=False)
# plt.show()

# # Visualize average total CBD by month over time.
# results['total_cbd'] = results['total_cbd'].astype(float)
# sample = results.loc[results['total_cbd'] < 1]
# average_total_cbd = sample.groupby('month')['total_cbd'].mean()
# fig, ax = plt.subplots(figsize=(13, 8))
# average_total_cbd.index = average_total_cbd.index.to_timestamp()
# ax.plot(average_total_cbd.index, average_total_cbd.values, label='Monthly Average Total CBD', color='royalblue', lw=5)
# ax.scatter(sample['date'], sample['total_cbd'], color='royalblue', s=10, alpha=0.5, label='Daily Individual Results')
# ax.set_xlabel('')
# ax.set_ylabel('Total CBD (%)')
# ax.set_title('Average Total CBD by Month in Oregon in Low CBD Samples (<1%)')
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
# ax.xaxis.set_major_locator(mdates.MonthLocator((1,4,7,10)))
# plt.xticks(rotation=45)
# plt.ylim(0, 0.75)
# plt.savefig(f'{assets_dir}/or-total-cbd.png', dpi=300, bbox_inches='tight', transparent=False)
# plt.show()