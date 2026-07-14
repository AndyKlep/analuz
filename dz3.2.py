import numpy as np
import matplotlib.pyplot as plt

random_array1 = np.random.rand(25)
random_array2 = np.random.rand(25)
print(random_array1, random_array2)
plt.scatter(random_array1, random_array2)

plt.xlabel("ось Х")
plt.ylabel("ось Y")
plt.title("Тестовая диаграмма рассеяния")

plt.show()