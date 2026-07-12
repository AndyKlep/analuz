import pandas as pd

df = pd.read_csv('animal.csv')

df.fillna(value=0, inplace=True)
group = df.groupby('Пища')['Средняя продолжительность жизни'].mean()
print(group)
df.to_csv('output.csv', index=False)