import itertools
import multiprocessing
import pandas as pd
import os
import cProfile
from collections import ChainMap
from typing import List, Dict


def print_multiprocess_result(file_name: str, profession_name: str, queue: multiprocessing.Queue) -> None:
    """
    Формирует данные аналитики по годам в режиме многопроцессорности

    :param file_name: Название csv-файла
    :param profession_name: Название профессии
    :param queue: Передаваемая очередь класса Queue из библиотеки multiprocessing
    """
    df = pd.read_csv(file_name)
    df['salary'] = df[['salary_from', 'salary_to']].mean(axis=1)
    df['published_at'] = df['published_at'].apply(lambda x: int(x[:4]))
    vacancy_df = df[df['name'].str.contains(profession_name)]
    vacancy_years = df['published_at'].unique()
    year_salary = {year: [] for year in vacancy_years}
    count_salary = {year: 0 for year in vacancy_years}
    job_year_salary = {year: [] for year in vacancy_years}
    job_count_salary = {year: 0 for year in vacancy_years}

    for year in vacancy_years:
        year_salary[year] = int(df[df['published_at'] == year]['salary'].mean())
        count_salary[year] = len(df[df['published_at'] == year])
        job_year_salary[year] = int(vacancy_df[vacancy_df['published_at'] == year]['salary'].mean())
        job_count_salary[year] = len(vacancy_df[vacancy_df['published_at'] == year].index)

    queue.put([year_salary, count_salary, job_year_salary, job_count_salary])

def print_singleprocess_result(file_name: str) -> List[Dict]:
    """
    Формирует данные аналитики по городам в режиме однопроцессорности

    :param file_name: Название csv-файла
    :return: Возвращает словари с информацией об уровне зарплат и доле вакансий по городам
    """
    df = pd.read_csv(file_name)
    df['salary'] = df[['salary_from', 'salary_to']].mean(axis=1)
    df['published_at'] = df['published_at'].apply(lambda x: int(x[:4]))
    df['count'] = df.groupby('area_name')['area_name'].transform('count')
    sample_df = df[df['count'] > 0.01 * len(df)]
    city_salary = {}
    city_count = {}
    for city in list(sample_df['area_name'].unique()):
        salary_df = sample_df[sample_df['area_name'] == city]
        city_salary[city] = int(salary_df['salary'].mean())
        city_count[city] = round(len(salary_df) / len(df), 4)
    return [city_salary, city_count]


def start_multiprocess_analytics(directory_name: str, profession_name: str) -> None:
    """
    Запускает обработку и формирование аналитики по вакансиям в режиме многопроцессорности

    :param directory_name: Название директории csv-файлов
    :param profession_name: Название профессии
    """
    data = []
    queue = multiprocessing.Queue()
    processes = []
    for file_name in os.listdir(directory_name):
        file_csv_name = os.path.join(directory_name, file_name)
        process = multiprocessing.Process(target=print_multiprocess_result, args=(file_csv_name, profession_name, queue))
        processes.append(process)
        process.start()

    for process in processes:
        data.append(queue.get())
        process.join()

    city_data = print_singleprocess_result(r'..\csv\vacancies_by_year.csv')
    years_data = list(zip(*data))
    print(f'Динамика уровня зарплат по годам: '
          f'{dict(sorted(dict(ChainMap(*years_data[0])).items(), key=lambda x: x[0]))}')
    print(f'Динамика количества вакансий по годам: '
          f'{dict(sorted(dict(ChainMap(*years_data[1])).items(), key=lambda x: x[0]))}')
    print(f'Динамика уровня зарплат по годам для выбранной профессии: '
          f'{dict(sorted(dict(ChainMap(*years_data[2])).items(), key=lambda x: x[0]))}')
    print(f'Динамика количества вакансий по годам для выбранной профессии: '
          f'{dict(sorted(dict(ChainMap(*years_data[3])).items(), key=lambda x: x[0]))}')
    print(f'Уровень зарплат по городам (в порядке убывания): '
          f'{dict(itertools.islice(sorted(city_data[0].items(), key=lambda x: x[1], reverse=True), 10))}')
    print(f'Доля вакансий по городам (в порядке убывания): '
          f'{dict(itertools.islice(sorted(city_data[1].items(), key=lambda x: x[1], reverse=True), 10))}')


class UserInput:
    """
    Класс для предоставления вводных данных по параметрам

    Attributes:
        directory_name (str): Название файла исходных данных
        profession_name (str): Название профессии
    """

    def __init__(self):
        """
        Инициализирует объект UserInput, выполняет сохранение пользовательских вводов
        """
        inputs = [
            'Введите название директории файлов csv',
            'Введите название профессии',
        ]
        values = [input(f'{inputs[i]}: ') for i in range(len(inputs))]
        self.directory_name = values[0]
        self.profession_name = values[1]
        self.error_checker()

    def error_checker(self):
        if not os.path.exists(self.directory_name):
            custom_exit('Каталог не найден')


def custom_exit(message: str) -> None:
    """
    Выполняет выход из программы с пользовательским выводом.

    :param message: Сообщение для вывода
    """
    print(message)
    exit()


if __name__ == '__main__':
    p = cProfile.Profile()
    p.enable()

    inputs = UserInput()
    start_multiprocess_analytics(directory_name=inputs.directory_name, profession_name=inputs.profession_name)


    p.disable()
    p.print_stats(sort='cumtime')
