import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

file_name1 = input()
file_name2 = input()
data_mvs = pd.read_csv(file_name1, delimiter = ",", header = None)
data_profile = pd.read_csv(file_name2, delimiter = ",", header = None)

### Проверка на то, что входные файлы типа txt
if not file_name1[-4:] == '.txt':
    print('ERROR MVS FILE TYPE')
if not file_name2[-4:] == '.txt':
    print('ERROR PROFILE FILE TYPE')
	
### Проверка на то, что входные данные морской съемки имеют нужный тип данных
if not data_profile[0].dtypes == object and data_profile[1].dtypes == object and data_profile[2].dtypes == np.float64 and data_profile[3].dtypes == np.int64 and data_profile[4].dtypes == np.int64:
    print('ERROR PROFILE DATA TYPE')
	
### Проверка на то, что входные данные МВС имеют нужный тип данных
if not data_mvs[0].dtypes == object and data_mvs[1].dtypes == object and data_mvs[2].dtypes == np.float64:
    print('ERROR MVS DATA TYPE')
	
### Проверка на то, что в файлах содержатся только цифры и разделители целой и дробной части
flag = 1
for i in range(len(data_mvs)):
    for s in data_mvs[0][i]:
        if not ('0' <= s <= '9' or s == '.'):
            flag = 0
    for s in data_mvs[1][i]:
        if not ('0' <= s <= '9' or s == ':'):
            flag = 0
    if flag == 0:
        print('ERROR MVS DATA RECORDING')
        break

flag = 1
for i in range(len(data_profile)):
    for s in data_profile[0][i]:
        if not ('0' <= s <= '9' or s == '.'):
            flag = 0
    for s in data_profile[1][i]:
        if not ('0' <= s <= '9' or s == ':'):
            flag = 0
    if flag == 0:
        print('ERROR PROFILE DATA RECORDING')
        break

### Проверка на то, что временной диапазон МВС полностью покрывает морскую съемку
if not (data_mvs[1][0] <= data_profile[1][0] and data_mvs[1][len(data_mvs) - 1] >= data_profile[1][len(data_profile) - 1]):
    print('ERROR TIME INTERVALS')

### Проверка на то, что дата в обоих файлах одинаковая и единственная
if not len(np.unique(data_mvs[0])) == 1 and np.unique(data_mvs[0]) == np.unique(data_profile[0]):
    print('DATE MATCHING ERROR')

### Строится график данных морской съемки
### Ось ОХ - время
### Ось OY - напряженность магнитного поля
plt.figure(figsize = (20,10))
plt.plot(data_profile[2])
plt.xticks(np.arange(0, len(data_profile[1]), 20), data_profile[1][::20])
plt.xlabel('Время', fontsize = 15)
plt.ylabel('нТл', fontsize = 15)
plt.grid()
plt.title('График данных морской съемки', fontsize = 21)
plt.savefig('Marine_data_plot.png')
os.system('Marine_data_plot.png')

### Строится график данных МВС
### Ось ОХ - время
### Ось OY - напряженность магнитного поля
plt.figure(figsize = (20,10))
plt.plot(data_mvs[2])
plt.xticks(np.arange(0, len(data_mvs[1]), 30), data_mvs[1][::30])
plt.xlabel('Время', fontsize = 15)
plt.ylabel('нТл', fontsize = 15)
plt.grid()
plt.title('График данных МВС', fontsize = 21)
plt.savefig('MVS_data_plot.png')
os.system('MVS_data_plot.png')

### Функция, которая преобразует строку формата 'hh:mm:ss' в число.
### Это нужно, чтобы удобно проинтерполировать
def get_time(time_in_string):
    h, m, s = map(int, time_in_string.split(':'))
    return h * 3600 + m * 60 + s

### x - точки в которых мы хотим получить интерполированные значения функции
### xp - координаты времени значений
### fp - значения функции в xp
x = np.arange(get_time(data_mvs[1][0]), get_time(data_mvs[1][len(data_mvs) - 1]))
xp = list(map(get_time, data_mvs[1]))
fp = data_mvs[2]
### Функция интерполирования
interpolate_data = np.interp(x, xp, fp)

### Считаем поправку для интерполированных значений
med = np.median(data_mvs[2])
popravka = med - interpolate_data

### Выбираем нужный диапазон: время, когда считались данные морской съемки
### Прибавляем к данным морской съемки поправку за вариации МП
start_idx = get_time(data_profile[1][0]) - get_time(data_mvs[1][0])
finish_idx = start_idx + len(data_profile[1])
data_with_popravka = data_profile[2] + popravka[start_idx:finish_idx]

### Строим 2 графика для сравнения данных морской съемки без поправки и с ней
plt.figure(figsize = (20,10))
plt.plot(data_profile[2], label = 'исходные данные')
plt.plot(data_with_popravka, label = 'данные с учетом поправки')
plt.xticks(np.arange(0, len(data_profile[1]), 20), data_profile[1][::20])
plt.xlabel('Время', fontsize = 15)
plt.ylabel('нТл', fontsize = 15)
plt.grid()
plt.title('График морских данных с поправкой', fontsize = 21)
plt.legend(fontsize = 15)
plt.savefig('Marine_data_with_modification_plot.png')
os.system('Marine_data_with_modification_plot.png')

### Создаем массив данных морской съемки с учтенной поправкой
res_data = data_profile
res_data[2] = data_with_popravka
### Создаем выходной файл, куда сохраняем данные с введенной поправкой
res_file = open('res_marine_profile_data.txt', 'w')
res_file.write(res_data.to_string())
res_file.close()