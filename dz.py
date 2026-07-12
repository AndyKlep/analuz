import pandas as pd

df1 = pd.read_csv('anime.csv')
print(
    df1.head(),
    df1.info(),
    df1.describe()
    )


df2 = pd.read_csv('dz.csv')
group2 = df2.groupby('City')['Salary'].mean()
print(group2)