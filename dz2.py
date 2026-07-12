import random
import pandas as pd

data = {
    'student_name': [
        'Иван', 'Мария', 'Алексей', 'Ольга', 'Дмитрий',
        'Елена', 'Сергей', 'Анна', 'Никита', 'Татьяна'
    ],
    'math': [],
    'physics': [],
    'informatics': [],
    'history': [],
    'literature': []
}

subjects = ['math', 'physics', 'informatics', 'history', 'literature']

for name in data['student_name']:
    for subj in subjects:
        data[subj].append(random.randint(2, 5))

df = pd.DataFrame(data)
print(df.head())

for i in df:
    if i == 'student_name':
        pass
    else:
        print(f'Средняя оценка по {i}: {df[i].mean()}')
        print(f'Средняя оценка по {i}: {df[i].median()}')
        q1 = df[i].quantile(0.25)
        q3 = df[i].quantile(0.75)
        IQR = q3 - q1
        print(f'Mежквартальный размах {i}: {IQR}')
        print(f'Стандартное отклоение по {i}: {df[i].std()}')