import pandas as pd
import requests
import concurrent.futures
from typing import List, Dict, Any


class HeadHunterCSV:
    """
    Класс для представления функций по получению вакансий в .csv файле через API HeadHunter.ru

    Attributes:
        url (str): URL-адрес API HeadHunter.ru
    """
    def __init__(self, url):
        """
        Инициализирует класс HeadHunterCSV

        :param url: URL-адрес API HeadHunter.ru
        """
        self.url = url

    def get_json_data(self, param_sets: List[Dict[str, Any]]) -> (List[Dict[str, str]] or List[Dict[Dict[str, str]]]):
        """
        Выполняет запрос к API hh.ru для получения JSON-файла с данными о вакансиях

        :param param_sets: Словарь с выборкой параметров, по которым будет идти поиск вакансий (заранее поделен на
        временные интервалы для обхода ограничений в 2000 вакансий на запрос)
        :return: Возвращает данные о вакансиях в формате JSON
        """
        return requests.get(self.url, param_sets).json()["items"]

    @staticmethod
    def get_vacancies_data(vacancies: List[Dict[str, str]] or List[Dict[Dict[str, str]]]) -> (List[List[str]]):
        """
        Формирует список данных о вакансиях, полученных из JSON.
        Требуемые поля:
        Название, Город, Нижняя граница оклада, Верхняя граница оклада, Идентификатор валюты, Дата публикации

        :param vacancies: Список вакансий, представленных в формате JSON
        :return: Возвращает список с вакансиями с нужными полями
        """
        return [[vacancy["name"],
                 vacancy["salary"]["from"],
                 vacancy["salary"]["to"],
                 vacancy["salary"]["currency"],
                 vacancy["area"]["name"],
                 vacancy["published_at"]] for vacancy in vacancies if vacancy["salary"]]


if __name__ == "__main__":
    pages = 20
    param_set1 = [dict(specialization=1,
                       date_from="2022-12-29T00:00:00",
                       date_to="2022-12-29T06:00:00",
                       per_page=100,
                       page=page) for page in range(pages)]

    param_set2 = [dict(specialization=1,
                       date_from="2022-12-29T06:00:00",
                       date_to="2022-12-29T12:00:00",
                       per_page=100,
                       page=page) for page in range(pages)]

    param_set3 = [dict(specialization=1,
                       date_from="2022-12-29T12:00:00",
                       date_to="2022-12-29T18:00:00",
                       per_page=100,
                       page=page) for page in range(pages)]

    param_set4 = [dict(specialization=1,
                       date_from="2022-12-29T18:00:00",
                       date_to="2022-12-30T00:00:00",
                       per_page=100,
                       page=page) for page in range(pages)]

    api_parser = HeadHunterCSV('https://api.hh.ru/vacancies')

    executor = concurrent.futures.ProcessPoolExecutor()
    result_data = list(executor.map(api_parser.get_json_data, param_set1 + param_set2 + param_set3 + param_set4))
    response = list(executor.map(api_parser.get_vacancies_data, result_data))
    result_data = pd.concat([pd.DataFrame(row,
                                          columns=['name',
                                                   'salary_from',
                                                   'salary_to',
                                                   'salary_currency',
                                                   'area_name',
                                                   'published_at'])
                             for row in response])
    result_data.to_csv("HeadHunter_csv.csv", index=False)