import pandas as pd


df_feed = pd.read_json('https://domoplaner.ru/feeds-export/deals/full/312/y5RudLy1s0QMsu1w2FhIOMoa51YfjBfWx4IKVoTmfUevO0rBoyHjx1WEFqJksxNQ/U4aRJsydEBOIUAMZO2lskb7jX4nYNrdA/', orient='records')
df_feed = df_feed['data']
# df_feed = df_feed.set_index('ID')
df_feed = pd.json_normalize(df_feed)
df_feed.to_csv('feed.csv')


flats_DP = pd.read_json("https://domoplaner.ru/feeds-export/flats/full/312/y5RudLy1s0QMsu1w2FhIOMoa51YfjBfWx4IKVoTmfUevO0rBoyHjx1WEFqJksxNQ/U4aRJsydEBOIUAMZO2lskb7jX4nYNrdA/", orient='records')
flats_DP = pd.json_normalize(flats_DP['data'])
flats_DP = flats_DP.set_index('ID')
flats_DP.to_csv('flats_DP.csv')

# print(df_feed)
# print(flats_DP)