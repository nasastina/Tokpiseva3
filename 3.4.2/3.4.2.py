import os
from typing import Dict, List, Any, Tuple

import pdfkit
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from jinja2 import Environment, FileSystemLoader
from concurrent import futures
from statistics import mean


currency = pd.read_csv('currency.csv')

class ValuteConverter:
    """
    Класс для представления функций по конвертации валют в вакансиях и создании .csv файла

    Attributes:
        df (DataFrame): Исходный фрейм данных вакансий
        currency_df (DataFrame): Фрейм с курсами валют на даты, встречающиеся в вакансиях
        currencies (List[str]): Допустимые к обработке валюты
    """
    def __init__(self, df: pd.DataFrame, currency_df: pd.DataFrame):
        """
        Инициализирует класс ValuteConverter, формирует список допустимых к обработке валют

        :param df: Исходный фрейм данных вакансий, полученный после формирования файла курса валют
        :param currency_df: Фрейм с курсами валют на даты, встречающиеся в вакансиях
        """
        self.df = df
        self.currency_df = currency_df
        self.currencies = list(self.currency_df.keys()[2:])

    def csv_create(self, date):
        """
        Создает .csv файл с обработанными вакансиями, у которых зарплата переведена по курсу валют
        """
        self.df.insert(1, 'salary', None)
        self.df['salary'] = self.df[['salary_from', 'salary_to', 'salary_currency', 'published_at']]\
                                                        .apply(self.get_salary, axis=1)
        self.df.drop(labels=['salary_to', 'salary_from', 'salary_currency'], axis=1, inplace=True)
        self.df = self.df.loc[self.df['salary'] != 'nan']
        self.df.to_csv(f'csv\\part_{date}.csv', index=False)
        return self.df

    def get_salary(self, row) -> (str or float):
        """
        Возвращает значение зарплаты по вакансии, переведенное в рубли по курсу валют. В случае недопустимых значений,
        возвращает 'nan' и останавливает функцию.

        :param row: Строка из DataFrame - рассматриваемая вакансия (ее строка)
        :return: Возвращает значение зарплаты или 'nan' при несоблюдении условий конвертации и обработки вакансии
        """
        salary_currency = str(row[2])
        salary_list = list(filter(lambda x: str(x) != 'nan', row[:2]))
        if salary_currency == 'nan':
            return 'nan'

        if len(salary_list) != 0:
            salary = mean(salary_list)
        else:
            return 'nan'

        if salary_currency != 'RUR' and salary_currency in self.currencies:
            multiplier = self.currency_df[self.currency_df['date'] == str(row[3])[:7]][salary_currency].iat[0]
            salary *= multiplier
        return salary

class SeparateCSV:
    """
    Класс для деления общего .csv файла с вакансиями на несколько по годам в формате part_[year].csv

    Attributes:
        file_name (str): Имя исходного .csv файла
    """
    def __init__(self, file_name: str):
        """
        Инициализирует класс SeparateCSV, производит деление большого .csv файла на несколько малых по годам

        :param file_name: Имя исходного .csv файла
        """
        self.df = pd.read_csv(file_name)
        self.df["years"] = self.df["published_at"].apply(lambda year: int(".".join(year[:4].split("-"))))
        self.years = list(self.df["years"].unique())

        for year in self.years:
            if not os.path.exists('csv'):
                os.mkdir('csv')

            data = self.df[self.df["years"] == year]
            data[["name",
                  "salary_from",
                  "salary_to",
                  "salary_currency",
                  "area_name",
                  "published_at"]].to_csv(f"csv\\part_{year}.csv", index=False)

class UserInput:
    """
    Класс для пользовательских вводов данных
    """
    def __init__(self):
        """
        Инициализирует класс UserInput, в поля сохраняет пользовательские исходные данные
        """
        self.file_name = input("Введите название файла: ")
        self.profession_name = input("Введите название профессии: ")

class Report:
    """
    Класс для генерации .png графиков и .pdf отчета по аналитике вакансий
    """
    def __init__(self, profession_name: str, year_analytics_dicts: List[Dict[str, int]]):
        """
        Инициализирует класс Report, начинает генерацию графиков и отчета

        :param profession_name: Название профессии
        :param year_analytics_dicts: Словари с аналитикой по годам для всех профессий и для выбранной профессии
        """
        self.generate_image(profession_name, year_analytics_dicts)
        self.generate_pdf(profession_name, year_analytics_dicts)

    @staticmethod
    def generate_pdf(profession_name: str, year_analytocs_dicts: List[Dict[str, int]]) -> None:
        """
        Метод для генерации .pdf отчета

        :param profession_name: Название профессии
        :param year_analytocs_dicts: Словари с аналитикой по годам для всех профессий и для выбранной профессии
        """
        env = Environment(loader=FileSystemLoader('./'))
        template = env.get_template("template.html")
        pdf_template = template.render(
            {'name': profession_name,
             'dicts': year_analytocs_dicts,
             'graph': 'graph.png'})
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options={"enable-local-file-access": ""})

    @staticmethod
    def generate_image(profession_name: str, year_analytics_dicts: List[Dict[str, int]]) -> None:
        """
        Метод для генерации .png графиков с аналитикой по годам

        :param profession_name: Название профессии
        :param year_analytics_dicts: Словари с аналитикой по годам для всех профессий и для выбранной профессии
        """
        graph = plt.figure()
        width = 0.4
        x_axis = np.arange(len(year_analytics_dicts[0].keys()))

        first_graph = graph.add_subplot(221)
        first_graph.set_title("Уровень зарплат по годам")
        first_graph.bar(x_axis - width / 2, year_analytics_dicts[0].values(), width, label="средняя з/п")
        first_graph.bar(x_axis + width / 2, year_analytics_dicts[1].values(), width,
                        label=f"з/п {profession_name.lower()}")
        first_graph.set_xticks(x_axis, year_analytics_dicts[0].keys(), rotation="vertical")
        first_graph.tick_params(axis="both", labelsize=8)
        first_graph.legend(fontsize=8)
        first_graph.grid(True, axis="y")

        second_graph = graph.add_subplot(222)
        second_graph.set_title("Количество вакансий по годам")
        second_graph.bar(x_axis - width / 2, year_analytics_dicts[2].values(), width, label="Количество вакансий")
        second_graph.bar(x_axis + width / 2, year_analytics_dicts[3].values(), width,
                         label=f"Количество вакансий \n{profession_name.lower()}")
        second_graph.set_xticks(x_axis, year_analytics_dicts[2].keys(), rotation="vertical")
        second_graph.tick_params(axis="both", labelsize=8)
        second_graph.legend(fontsize=8)
        second_graph.grid(True, axis="y")

        plt.tight_layout()
        plt.savefig("graph.png")

def sort_dict(unsorted_dict: Dict[Any]) -> Dict[Any]:
    """
    Метод для сортировки словаря

    :param unsorted_dict: Исходный словарь
    :return: Возвращает отсортированный словарь
    """
    sorted_dict = {}
    for key in sorted(unsorted_dict):
        sorted_dict[key] = unsorted_dict[key]
    return sorted_dict


def csv_process(proccess_args: Tuple[str, str]) -> List[Dict[Any]]:
    """
    Запускает процесс обработки данных за год и формирует словари с аналитикой

    :param proccess_args: Аргументы, передаваемые при запуске процесса
    :return: Возвращает словарь с аналитикой:
    - Динамина уровня зарплат по годам
    - Динамика количества вакансий по годам
    - Динамика уровня зарплат по годам для выбранной профессии
    - Динамика количества вакансий по годам для выбранной профессии
    """
    profession_name = proccess_args[0]
    current_year = proccess_args[1]
    year_df = pd.read_csv(f'csv\\part_{current_year}.csv')
    year_df = ValuteConverter(year_df, currency).csv_create(current_year)

    vacancy_year_df = year_df[year_df["name"].str.contains(profession_name)]

    salary_year = {current_year: []}
    vacancy_year = {current_year: 0}
    profession_salary_year = {current_year: []}
    profession_vacancy_year = {current_year: 0}

    salary_year[current_year] = int(year_df['salary'].mean())
    vacancy_year[current_year] = len(year_df)
    profession_salary_year[current_year] = int(vacancy_year_df['salary'].mean())
    profession_vacancy_year[current_year] = len(vacancy_year_df)

    analytics_dicts = [salary_year, vacancy_year, profession_salary_year, profession_vacancy_year]
    return analytics_dicts

if __name__ == '__main__':
    inputs = UserInput()
    file_name, profession_name = inputs.file_name, inputs.profession_name

    separate_csv = SeparateCSV(file_name)
    df = separate_csv.df
    years = separate_csv.years

    salary_year, vacancy_year, profession_salary_year, profession_vacancy_year = {}, {}, {}, {}

    executor = futures.ProcessPoolExecutor()
    for year in years:
        args = (profession_name, year)
        result = executor.submit(csv_process, args).result()
        salary_year.update(result[0])
        vacancy_year.update(result[1])
        profession_salary_year.update(result[2])
        profession_vacancy_year.update(result[3])

    print("Динамика уровня зарплат по годам:", sort_dict(salary_year))
    print("Динамика количества вакансий по годам:", sort_dict(vacancy_year))
    print("Динамика уровня зарплат по годам для выбранной профессии:", sort_dict(profession_salary_year))
    print("Динамика количества вакансий по годам для выбранной профессии:", sort_dict(profession_vacancy_year))

    analytics_list_dicts = [sort_dict(salary_year),
                            sort_dict(profession_salary_year),
                            sort_dict(vacancy_year),
                            sort_dict(profession_vacancy_year)]

    report = Report(profession_name, analytics_list_dicts)