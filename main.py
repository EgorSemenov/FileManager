# -*- coding: utf8 -*-

import datetime as dt
import random
import string
import re
import os
import sqlite3
import statistics
import time
from progress.bar import Bar


class FileGenerator:
    def __init__(self, amount_of_last_years, amount_of_symbols, randomizer):
        self.amount_of_last_years = amount_of_last_years  # случайная дата за последние amount_of_last_years лет
        self.amount_of_symbols = amount_of_symbols  # количество символов в русской и латинской последовательностях
        self.randomizer = randomizer  # сущность рандомного генератора, которой будет гениророваться вся необходимая информация
        self.path = 'D:\\документы\\4 курс\\test_exercise\\test_task\\files\\'  # пусть до директории с файлами

    def gen_files(self, name, number_of_first, amount, size):
        """
        следующие три метода - это генератор, использую, т.к. строк может быть очень много, записываем в файл по одной,
        сгенерировали - записали, чтобы всегда хватало памяти.
        :param name: имя файла
        :param number_of_first: первый номер файла, под которым файл будет создан или перезаписан
        :param amount:  количество файлов, к записи/перезаписи подряд от первого
        :param size: количество строк в файле
        :return:
        """
        print('Генерация файлов...')
        for i in range(number_of_first, number_of_first + amount):
            self.__gen_file(name + str(i) + '.txt', size)
        print('Генерация файлов завершена.')

    def __gen_file(self, name, size):
        file_name = self.path + name
        metafile_name = self.path + 'meta' + name
        mf = open(metafile_name, 'w')
        mf.write(str(size))
        mf.close()
        with open(file_name, 'w') as f:
            for i in self.__gen_strings(size):
                f.write(i)
        f.close()

    def __gen_strings(self, size):
        k = 0
        while k < size:
            yield self.__form_string()
            k += 1

    def __form_string(self):
        return self.randomizer.gen_date_between(
            self.amount_of_last_years) + '||' + self.randomizer.gen_letter_sequence(self.amount_of_symbols, 'eng') \
               + '||' + self.randomizer.gen_letter_sequence(self.amount_of_symbols, 'ru') + '||' \
               + str(self.randomizer.gen_int()) + '||' + str(self.randomizer.gen_float()) + '||' + '\n'

    def unite_files(self, name, name_of_merged, first, last, ind_for_delete='*'):
        """
        объединяет файлы в один, также использовал генератор, чтобы работать со строками по одной
        :param name: имя файл в который произойдет объединение
        :param name_of_merged: имя объединяемых
        :param first: первый индекс объединяемых
        :param last: последний индекс объединяемых
        :param ind_for_delete: набор символов, при наличии которого в строке, строки будут удаляться
        """
        print('Объединение файлов...')
        amount_of_deleted = 0
        counter = 0
        uf = open(self.path + name + '.txt', 'w')
        filenametemp = self.path + 'filetemp.txt'
        for i in range(first, last + 1):
            filename = self.path + name_of_merged + str(i) + '.txt'  # имя объединяемого файла
            f = open(filename, 'r')
            temp_f = open(filenametemp,
                          'w')  # этот файл заменяет объединяемые файлы, отличаясь от них отсутствием строк с заданным
            # сочетанием символов.(в него также строки вписываются по одной, чтобы не загружать в память все строки,
            # удалять несколько и затем записывать их в файл, без использования временного файла)
            temp_f_counter = 0
            for k in self.__get_strings(f, ind_for_delete):
                uf.write(
                    k)  # заполнение подходящими(без заданного сочетания символов) строками файла в который объединяются другие файлы
                temp_f.write(k)  # заполнение подходящими строками временного файла
                temp_f_counter += 1
                counter += 1
            temp_f.close()
            metafilename = self.path + 'meta' + name_of_merged + str(
                i) + '.txt'  # получение имени мета-файла, для каждого из объединяемых файлов
            mf = open(metafilename, 'r')
            amount_of_deleted = amount_of_deleted + int(
                mf.read()) - temp_f_counter  # прибавляем разницу между количеством строк которое было
            # и количеством строк которое записано в файл
            mf.close()
            mf = open(metafilename, 'w')
            mf.write(str(temp_f_counter))  # запись нового количества строк в объединяемом файле в мета-файл
            mf.close()
            f.close()
            temp_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                     filename)  # получение имены файла, который нужно заменить
            os.remove(temp_path)  # удаление файла, который нужно заменить
            os.rename(filenametemp, filename)  # переименование временного файла
        muf = open(self.path + 'meta' + name + '.txt',
                   'w')  # мета файл с новым количеством строк для файла в который объединялись
        muf.write(str(counter))
        muf.close()
        print('Объединение завершено, было удалено {} строк'.format(amount_of_deleted))

    def __get_strings(self, file, s):
        """
        # читает строки и возвращает их, если в них нет заданного сочетания символов
        """
        line = file.readline()
        while line:
            if s not in line:
                yield line
            line = file.readline()


class RandomGenerator:
    def __init__(self):
        self.ru_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' + 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'.upper()  # пул русских символов, для составления случайной последовательности

    def gen_date_between(self,
                         amount_of_last_years):
        """
        генерация даты, начиная с заданного количества лет назад и до настоящего момента
        """
        end_date = dt.date.today()
        start_date = dt.date(end_date.year - amount_of_last_years, 1, 1)
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + dt.timedelta(days=random_number_of_days)
        return self.__add_zero_to_date(random_date.day) + '.' + self.__add_zero_to_date(random_date.month) + '.' + str(
            random_date.year)

    def __add_zero_to_date(self, date):
        """
        приводит месяца и дни к нужному виду
        """
        if date < 10:
            return '0' + str(date)
        else:
            return str(date)

    def gen_letter_sequence(self, amount_of_symbols, loc):
        """
        генерирует случайные последовательности в зависимости от локали
        """
        if loc == 'eng':
            return ''.join(random.choices(string.ascii_letters, k=amount_of_symbols))
        elif loc == 'ru':
            return ''.join(random.choices(self.ru_letters, k=amount_of_symbols))

    def gen_int(self):
        """
        генерирует случайное целое четное число от 1 до 100000000
        :return:
        """
        return random.randrange(2, 100000000, 2)

    def gen_float(self):
        """
        генерирует cлучайное положительное число с 8 знаками после запятой в диапазоне от 1 до 20
        :return:
        """
        return float('{:8f}'.format((random.uniform(1, 20))))


class DbInterface:
    """
    класс, который является интерфейсом между логикой и бд
    """
    def __init__(self, db_name):
        self.name = db_name
        self.names_of_tables = []
        self.path = 'D:\\документы\\4 курс\\test_exercise\\test_task\\files\\'

    def create_table(self, name_of_table):
        conn = sqlite3.connect(self.name)
        c = conn.cursor()
        c.execute(
            'CREATE TABLE IF NOT EXISTS ' + name_of_table + ' (Date TEXT, NameEng TEXT, NameRu TEXT, Number INTEGER, Float REAL);')
        conn.commit()
        conn.close()
        self.names_of_tables.append(name_of_table)

    def import_strings_to_db(self, name, name_of_table, number_of_rows_in_file=0):
        filename = self.path + name + '.txt'
        metafilename = self.path + 'meta' + name + '.txt'
        if self.__if_table(name_of_table):
            try:
                mf = open(metafilename, 'r')
                number_of_rows_in_file = int(mf.read())  # считывание количества строк в файле из меты
                mf.close()
                conn = sqlite3.connect(self.name)  # подключение к базе данных
                c = conn.cursor()
                with Bar('Загрузка строк в бд', fill='*', suffix='%(index)d|%(remaining)d',
                         max=number_of_rows_in_file) as bar:
                    for i in self.__get_strings(filename):  # строчки на запись в файл также приходят по одной
                        data = self.__get_data_from_string(i)
                        c.execute('INSERT INTO ' + name_of_table + ' VALUES (?,?,?,?,?)', data)
                        bar.next()
                bar.finish()
            except FileNotFoundError:
                print('не найден файл')
            else:
                conn.commit()
            finally:
                conn.close()  # при возникновении любой ошибки связь с бд должна быть прервана

    def __if_table(self, name_of_table):
        """
        проверка существования таблицы
        """
        if name_of_table not in self.names_of_tables:
            return False
        else:
            return True

    def __get_strings(self, filename):
        """
        достает и возвращает по одной строки из файла
        """
        f = open(filename, 'r')
        line = f.readline()
        while line:
            yield line
            line = f.readline()

    def __get_data_from_string(self, string):
        """
        парсит строчку, извлекая данные для записи в бд
        """
        data = []
        line = string.split('||')
        k = 0
        for i in line:
            if k == 3:
                data.append(int(i))
            elif k == 4:
                data.append(float(i))
            else:
                data.append(i)
            k += 1
        data.pop(-1)
        return data

    def get_summa_of_ints(self, name_of_table):
        if self.__if_table(name_of_table):
            conn = sqlite3.connect(self.name)
            c = conn.cursor()
            c.execute('SELECT SUM(Number) FROM ' + name_of_table + ';')  # запрос в бд
            sum = c.fetchone()[0]  # извлечение результата
            return sum

    def get_median_of_floats(self, name_of_table):
        if self.__if_table(name_of_table):
            conn = sqlite3.connect(self.name)
            c = conn.cursor()
            c.execute('SELECT Float FROM ' + name_of_table + ';')
            data = []
            for temp in c:
                data.append(temp[0])
            return statistics.median(data)


# 1
###################
# 1.1
r = RandomGenerator()  # создаем сущность рандомного генератора, чтобы передать ее в файловый генератор
fg = FileGenerator(4, 10, r)  # создаем файловый генератор, передаем за какое количество последних лет и размеры символьных наборов, рандомный генератор
fg.gen_files('file', 1, 10, 1)  # создаем файлы, задавая: имя, начиная с какого индекса, сколько, и какое количество строк
###################
# 1.2
fg.unite_files('ufile1', 'file', 1, 3, 'h')  # объединяем файлы в один, задавая: имя в который объединяем, имя объединяемых,
# индекс первого объединяемого и последнего, сочетанием символов - строки с которым будут удалены
###################
# 1.3
di = DbInterface('ey_2020.db')  # создаем бд
di.create_table('Requests')  # создаем таблицу
di.import_strings_to_db('ufile1', 'Requests')  # грузим файл в бд
####################
# 1.4
print()
print('Сумма всех целых чисел: ', di.get_summa_of_ints('Requests'))
print('Медиана всех дробных чисел: ', di.get_median_of_floats('Requests'))
####################
####################
# 2
