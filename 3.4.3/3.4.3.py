import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdfkit
from statistics import mean
from typing import Dict, Any, List
from matplotlib import cm
from jinja2 import Environment, FileSystemLoader

def sort_dict_area(unsorted_dict: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Метод для сортировки словаря по городам вакансии

    :param unsorted_dict: Исходный словарь
    :return: Возвращает отсортированный словарь
    """
    sorted_tuples = sorted(unsorted_dict.items(), key=lambda item: item[1], reverse=True)[:10]
    sorted_dict = {key: value for key, value in sorted_tuples}
    return sorted_dict


def sort_dict(unsorted_dict: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Метод для сортировки словаря

    :param unsorted_dict: Исходный словарь
    :return: Возвращает отсортированный словарь
    """
    sorted_dict = {}
    for key in sorted(unsorted_dict):
        sorted_dict[key] = unsorted_dict[key]
    return sorted_dict


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

    def csv_create(self):
        """
        Создает .csv файл с обработанными вакансиями, у которых зарплата переведена по курсу валют
        """
        self.df.insert(1, 'salary', None)
        self.df['salary'] = self.df[['salary_from', 'salary_to', 'salary_currency', 'published_at']]\
                                                        .apply(self.get_salary, axis=1)
        self.df.drop(labels=['salary_to', 'salary_from', 'salary_currency'], axis=1, inplace=True)
        self.df = self.df.loc[self.df['salary'] != 'nan']
        self.df.to_csv(f'converted_vacancies.csv', index=False)
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
        self.area_name = input("Введите название региона: ")


class Report:
    """
    Класс для генерации .png графиков и .pdf отчета по аналитике вакансий
    """
    def __init__(self, profession_name: str, area_name: str, area_dicts: List[Dict], year_dicts: List[Dict]):
        """
        Инициализирует класс Report, начинает генерацию графиков и отчета

        :param profession_name: Название профессии
        :param area_name: Название региона
        :param area_dicts: Словари с городами
        :param year_dicts: Словари с годами
        """
        self.generate_image(profession_name, area_name, area_dicts, year_dicts)
        self.generate_pdf(profession_name, area_name, area_dicts, year_dicts)

    @staticmethod
    def generate_pdf(profession_name: str,
                     area_name: str,
                     area_dicts: List[Dict[Any, Any]],
                     year_dicts: List[Dict[Any, Any]]) -> None:
        """
        Метод для генерации .pdf отчета

        :param profession_name: Название профессии
        :param area_name: Название региона
        :param area_dicts: Список словарей по городам
        :param year_dicts: Список словарей по годам
        """
        env = Environment(loader=FileSystemLoader('./'))
        template = env.get_template("template.html")
        pdf_template = template.render(
            {'profession_name': profession_name,
             'area_name': area_name,
             'area_dict': area_dicts,
             'year_dict': year_dicts,
             'keys_0_area': list(area_dicts[0].keys()),
             'values_0_area': list(area_dicts[0].values()),
             'keys_1_area': list(area_dicts[1].keys()),
             'values_1_area': list(area_dicts[1].values()),
             'graph': 'graph.png'})

        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options={'enable-local-file-access': ''})

    @staticmethod
    def generate_image(profession_name: str,
                       area_name: str,
                       area_dicts: List[Dict[Any, Any]],
                       year_dicts: List[Dict[Any, Any]]) -> None:
        """
        Метод для генерации .png графиков с аналитикой по городам

        :param profession_name: Название профессии
        :param area_name: Название региона
        :param area_dicts: Список словарей по городам
        :param year_dicts: Список словарей по годам
        """
        graph = plt.figure()
        width = 0.4
        x_axis = np.arange(len(year_dicts[0].keys()))

        first_graph = graph.add_subplot(221)
        first_graph.set_title("Уровень зарплат по годам")
        first_graph.bar(x_axis, year_dicts[0].values(), width, label=f"з/п {profession_name.lower()} {area_name.lower()}")
        first_graph.set_xticks(x_axis, year_dicts[0].keys(), rotation="vertical")
        first_graph.tick_params(axis="both", labelsize=8)
        first_graph.legend(fontsize=8)
        first_graph.grid(True, axis="y")

        second_graph = graph.add_subplot(222)
        second_graph.set_title("Количество вакансий по годам")
        second_graph.bar(x_axis,
                         year_dicts[1].values(),
                         width,
                         label=f"Количество вакансий \n{profession_name.lower()} {area_name.lower()}")
        second_graph.set_xticks(x_axis, year_dicts[1].keys(), rotation="vertical")
        second_graph.tick_params(axis="both", labelsize=8)
        second_graph.legend(fontsize=8)
        second_graph.grid(True, axis="y")

        y_cities = np.arange(len(area_dicts[0].keys()))
        third_graph = graph.add_subplot(223)
        third_graph.set_title("Уровень зарплат по городам")
        third_graph.barh(y_cities, area_dicts[0].values(), 0.8, align="center")
        third_graph.set_yticks(y_cities,
                               labels=[key.replace('-', '-\n').replace(' ', '\n') for key in area_dicts[0].keys()],
                               horizontalalignment="right",
                               verticalalignment="center")
        third_graph.tick_params(axis="x", labelsize=8)
        third_graph.tick_params(axis="y", labelsize=6)
        third_graph.invert_yaxis()
        third_graph.grid(True, axis="x")

        fourth_graph = graph.add_subplot(224)
        fourth_graph.set_title("Доля вакансий по городам")
        area_dicts[1] = {'Другие': 1 - sum(area_dicts[1].values()), **area_dicts[1]}
        fourth_graph.pie(area_dicts[1].values(),
                         labels=area_dicts[1].keys(),
                         startangle=0,
                         textprops={'fontsize': 6},
                         colors=cm.Set3(np.arange(11)))
        fourth_graph.axis('equal')

        plt.tight_layout()
        plt.savefig("graph.png")


if __name__ == '__main__':
    inputs = UserInput()
    file_name, profession_name, area_name = inputs.file_name, inputs.profession_name, inputs.area_name
    df = pd.read_csv(file_name)
    df_currency = pd.read_csv("currency.csv")

    df["years"] = df["published_at"].apply(lambda date: int(".".join(date[:4].split("-"))))
    years = list(df["years"].unique())
    salary_area, vacancy_area, profession_vacancy_salary, profession_vacancy_count = {}, {}, {}, {}

    df = ValuteConverter(df, df_currency).csv_create()

    vacancies_count = len(df)
    df["count"] = df.groupby("area_name")['area_name'].transform("count")
    df_splitted = df[df['count'] >= 0.01 * vacancies_count]
    for city in list(df_splitted["area_name"].unique()):
        df_salary = df_splitted[df_splitted['area_name'] == city]
        salary_area[city] = int(df_salary['salary'].mean())
        vacancy_area[city] = round(len(df_salary) / len(df), 4)

    df_vacancy = df[df["name"].str.contains(profession_name)]
    for year in years:
        df_vacancy_salary = df_vacancy[(df_vacancy['years'] == year) & (df_vacancy['area_name'] == area_name)]
        if not df_vacancy_salary.empty:
            profession_vacancy_salary[year] = int(df_vacancy_salary['salary'].mean())
            profession_vacancy_count[year] = len(df_vacancy_salary)

    print("Уровень зарплат по городам (в порядке убывания):", sort_dict_area(salary_area))
    print("Доля вакансий по городам (в порядке убывания):", sort_dict_area(vacancy_area))
    print("Динамика уровня зарплат по годам для выбранной профессии и региона:", sort_dict(profession_vacancy_salary))
    print("Динамика количества вакансий по годам для выбранной профессии и региона:", sort_dict(profession_vacancy_count))

    area_dicts = [sort_dict_area(salary_area), sort_dict_area(vacancy_area)]
    year_dicts = [sort_dict(profession_vacancy_salary), sort_dict(profession_vacancy_count)]

    report = Report(profession_name, area_name, area_dicts, year_dicts)