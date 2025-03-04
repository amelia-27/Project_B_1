from pandas_datareader import wb

df = wb.get_indicators()[['id','name']]
df = df[df.name == 'Oil rents (% of GDP)']
print(df)