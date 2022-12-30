import csv
import os.path
import re
import datetime as DT
import itertools
import openpyxl
import openpyxl.styles.numbers
import matplotlib.pyplot as plt
import numpy as np
import pdfkit
import doctest
from jinja2 import Environment, PackageLoader, FileSystemLoader
from typing import List, Dict, Tuple, Any
from openpyxl.styles import NamedStyle, Border, Side, Font


class DataSet:
    """
    Класс для представления первичных данных всех вакансий.

    Attributes:
        file_name (str): Название файла исходных данных
        vacancies_objects (List[Vacancy]): Список вакансий типа Vacancy
    """

    def __init__(self, file_name: str):
        """
        Инициализирует объект DataSet, выполняет преобразование файла в список вакансий.

        :param file_name: Название файла исходных данных

        Tests
        -----
        >>>type(DataSet('vaca.csv')).__name__
        'DataSet'
        >>>len(DataSet('vaca.csv').vacancies_objects)
        2
        >>>DataSet('vaca.csv').vacancies_objects[0].name
        'Специалист'
        >>>DataSet('vaca.csv').vacancies_objects[1].name
        'Менеджер'
        >>>DataSet('vaca.csv').vacancies_objects[0].area_name
        'Санктg-Петербург'
        """
        self.file_name = file_name
        self.vacancies_objects = [Vacancy(vacancy) for vacancy in self.csv_filer(*self.csv_reader(file_name))]

    @staticmethod
    def __clean_html(raw_html: str) -> str:
        """
        Выполняет чистку строки от HTML-тегов и лишних специальных символов.

        :param raw_html: Исходная строка данных
        :return: Возвращает универсальную строку для обработки
        """
        clean_text = re.sub('<.*?>', '', raw_html).replace('\r\n', ' ').replace(u'\xa0', ' ').replace(u'\u2002',
                                                                                                      ' ').strip()
        return re.sub(' +', ' ', clean_text)

    @staticmethod
    def csv_reader(file_name: str) -> Tuple[List[str], List[List[str]]]:
        """
        Выполняет чтение файла и построчное извлечение данных из файла.

        :param file_name: Название файла исходных данных
        :return: Возвращает заголовки файла и список вакансий в виде строк
        """
        reader = csv.reader(open(file_name, encoding='utf-8-sig'))
        vacancies = [line for line in reader]
        if len(vacancies) == 0:
            custom_exit('Пустой файл')
        return vacancies[0], vacancies[1:]

    def csv_filer(self, list_naming: List[str], reader: List[List[str]]) -> List[Dict]:
        """
        Формирует список словарей, соответствующие вакансиям.

        :param list_naming: Заголовки файла
        :param reader: Список вакансий в виде строк
        :return: Возвращает список словарей по каждой вакансии
        """
        for i in range(len(reader) - 1, -1, -1):
            if reader[i].__contains__(''):
                reader[i] = ['']
            if len(reader[i]) < len(list_naming):
                reader.pop(i)
        for i in range(0, len(reader)):
            for j in range(0, len(reader[i])):
                reader[i][j] = self.__clean_html(reader[i][j])
        return [dict(zip(list_naming, value)) for value in reader]


class Vacancy:
    """
    Класс для представления данных вакансии.

    Attributes:
        __currency_to_rub (dict): Словарь перевода с валюты на рубли.
        name (str): Название вакансии.
        salary (int): Величина средней зарплаты по вакансии.
        area_name (str): Город вакансии.
        published_at (int): Год публикации вакансии.
    """

    def __init__(self, vacancy: Dict):
        """
        Инициализирует объект Vacancy, выполняет преобразования полей.

        :param vacancy: Словарь вакансии со всеми полями вакансии.

        Tests
        -----
        >>>vacancies = {'name': 'Программист',
        ...'salary_from': '40000.0',
        ...'salary_to': '55000.0',
        ...'salary_currency': 'RUR',
        ...'area_name': 'Москва','published_at': '2012-04-09T13:49:00+0400',}
        >>>type(Vacancy(vacancies)).__name__
        'Vacancy'
        >>>Vacancy(vacancies).name
        'Программист'
        >>>Vacancy(vacancies).salary
        47500
        >>>Vacancy(vacancies).area_name
        'Москва'
        >>>Vacancy(vacancies).published_at
        2012
        """
        self.__currency_to_rub = {
            "AZN": 35.68,
            "BYR": 23.91,
            "EUR": 59.90,
            "GEL": 21.74,
            "KGS": 0.76,
            "KZT": 0.13,
            "RUR": 1,
            "UAH": 1.64,
            "USD": 60.66,
            "UZS": 0.0055
        }
        self.name = vacancy['name']
        self.salary = int((float(vacancy['salary_from']) + float(vacancy['salary_to'])) / 2 * self.__currency_to_rub[
            vacancy['salary_currency']])
        self.area_name = vacancy['area_name']
        self.published_at = datetime_first_test(vacancy['published_at'])


def datetime_first_test(test):
    return int(DT.datetime.strptime(test, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y'))


def datetime_second_test(test):
    return int(test[:4])


def datetime_third_test(test):
    return int(test.split('-')[0])


def custom_exit(message: str) -> None:
    """
    Выполняет выход из программы с пользовательским выводом.

    :param message: Сообщение для вывода
    """
    print(message)
    exit()


class UserInput:
    """
    Класс для предоставления вводных данных по параметрам

    Attributes:
        file_name (str): Название файла исходных данных
        profession_name (str): Название профессии
    """

    def __init__(self):
        """
        Инициализирует объект UserInput, выполняет сохранение пользовательских вводов
        """
        inputs = [
            'Введите название файла',
            'Введите название профессии',
        ]
        values = [input(f'{inputs[i]}: ') for i in range(len(inputs))]
        self.file_name = values[0]
        self.profession_name = values[1]


class VacancyCountDict:
    """
    Класс для представления словаря - {вакансия : количество}

    Attributes:
        length (int): Длина словаря
        count_dict (dict): Пользовательский словарь
    """

    def __init__(self):
        """
        Инициализирует объект VacancyCountDict
        """
        self.length = 0
        self.count_dict = {}

    def add(self, key: str or int):
        """
        Добавляет или обновляет ключ и его значение в словаре
        :param key: Ключ словаря
        :return: Возвращает объект VacancyCountDict
        """
        if self.count_dict.get(key) is None:
            self.count_dict[key] = 0
        self.count_dict[key] += 1
        self.length += 1
        return self

    def add_not_contains(self, key: str or int):
        """
        Добавляет ключ при его отсутствии в словаре
        :param key: Ключ словаря
        :return: Возвращает объект VacancyCountDict
        """
        if self.count_dict.get(key) is None:
            self.count_dict[key] = 0
        return self

    def percent_add(self) -> None:
        """
        Выполняет выборку словаря по проценту от длины словаря
        """
        keys = []
        for key, value in self.count_dict.items():
            if value >= int(self.length * 0.01):
                self.count_dict[key] = round((value / self.length), 4)
            else:
                keys.append(key)
        for key in keys:
            del self.count_dict[key]


class VacancySalaryDict:
    """
    Класс для представления словаря - {вакансия : оклад}

    Attributes:
        length (int): Длина словаря
        year_salary_dict (dict): Словарь в виде {год: оклад}
        year_count_dict (dict): Словарь в виде {год: количество}
        area_salary_dict (dict): Словарь в виде {город: оклад}
    """

    def __init__(self):
        """
        Инициализиует объект VacancySalaryDict

        Tests
        -----
        >>>salary_dict = VacancySalaryDict()
        >>>type(salary_dict).__name__
        'VacancySalaryDict'
        >>>salary_dict.add(200, 2022)
        >>>salary_dict.length
        1
        >>>salary_dict.year_salary_dict
        {2022: 200}
        >>>salary_dict.year_count_dict
        {2022: 1}
        >>>salary_dict.add(100, 2021)
        >>>salary_dict.length
        2
        >>>salary_dict.year_salary_dict
        {2022: 200, 2021: 100}
        >>>salary_dict.year_count_dict
        {2022: 1, 2021: 1}
        >>>salary_dict.add(100, 2022)
        >>>salary_dict.length
        3
        >>>salary_dict.year_salary_dict
        {2022: 300, 2021: 100}
        >>>salary_dict.year_count_dict
        {2022: 2, 2021: 1}
        """
        self.length = 0
        self.year_salary_dict = {}
        self.year_count_dict = {}
        self.area_salary_dict = {}

    def add(self, salary: int, year: int):
        """
        Добавляет или обновляет ключ и его значение в словаре
        :param salary: Оклад вакансии
        :param year: Год публикации вакансии
        :return: Возвращает объект VacancySalaryDict
        """
        if self.year_salary_dict.get(year) is None:
            self.year_salary_dict[year] = 0
        if self.year_count_dict.get(year) is None:
            self.year_count_dict[year] = 0
        self.year_salary_dict[year] += salary
        self.year_count_dict[year] += 1
        self.length += 1
        return self

    def add_not_contains(self, year: int):
        """
        Добавляет ключ при его отсутствии в словаре
        :param year: Год публикации вакансии
        :return: Возвращает объект VacancySalaryDict
        """
        if self.year_salary_dict.get(year) is None:
            self.year_salary_dict[year] = 0
        return self

    def add_area(self, salary: int, area: str):
        """
        Добавляет или обновляет город и оклад в словаре
        :param salary: Оклад вакансии
        :param area: Город вакансии
        :return: Возвращает объект VacancySalaryDict
        """
        if self.area_salary_dict.get(area) is None:
            self.area_salary_dict[area] = 0
            self.year_count_dict[area] = 0
        self.area_salary_dict[area] += salary
        self.year_count_dict[area] += 1
        self.length += 1
        return self

    def get_average_salary(self) -> None:
        """
        Выполняет расчет среднего оклада по годам
        """
        if self.length > 0:
            for key, value in self.year_salary_dict.items():
                try:
                    self.year_salary_dict[key] = int(self.year_salary_dict[key] / self.year_count_dict[key])
                except:
                    self.year_salary_dict[key] = 0

    def percent_add(self) -> None:
        """
        Выполняет выборку словаря по проценту от длины словаря
        """
        keys = []
        for key, value in self.year_count_dict.items():
            if value >= int(self.length * 0.01):
                pass
            else:
                keys.append(key)
        for key in keys:
            del self.year_salary_dict[key]


class AnalysisResult:
    """
    Класс для представления данных по анализу вакансий

    Attributes:
        dataset (DataSet): Набор данных по вакансиям
        profession_name (str): Название профессии
        year_salary (VacancySalaryDict): Словарь в виде {год: оклад}
        count_salary (VacancyCountDict): Словарь в виде {количество: оклад}
        job_year_salary (VacancySalaryDict): Словарь в виде {год: оклад} по указанной профессии
        job_count_salary (VacancyCountDict): Словарь в виде {количество: оклад} по указанной профессии
        city_salary (VacancySalaryDict): Словарь в виде {город: оклад}
        city_count (VacancyCountDict): Словарь в виде {город: количество}
    """

    def __init__(self, dataset: DataSet, profession_name: str):
        """
        Инициализирует объект AnalisysResult

        :param dataset: Набор данных по вакансиям
        :param profession_name: Название профессии
        """
        self.dataset = dataset
        self.profession_name = profession_name
        self.year_salary = VacancySalaryDict()
        self.count_salary = VacancyCountDict()
        self.job_year_salary = VacancySalaryDict()
        self.job_count_salary = VacancyCountDict()
        self.city_salary = VacancySalaryDict()
        self.city_count = VacancyCountDict()

    def get_results(self):
        """
        Получает результаты анализа по вакансиям

        :return: Возвращает объект AnalysisResult
        """
        for vacancy in self.dataset.vacancies_objects:
            self.year_salary.add(salary=vacancy.salary, year=vacancy.published_at)
            self.count_salary.add(key=vacancy.published_at)
            self.city_count.add(key=vacancy.area_name)
            self.city_salary.add(salary=vacancy.salary, year=vacancy.area_name)
            if vacancy.name.__contains__(self.profession_name):
                self.job_count_salary.add(key=vacancy.published_at)
                self.job_year_salary.add(salary=vacancy.salary, year=vacancy.published_at)
            else:
                self.job_count_salary.add_not_contains(key=vacancy.published_at)
                self.job_year_salary.add_not_contains(year=vacancy.published_at)

        self.city_count.percent_add()
        self.year_salary.get_average_salary()
        self.job_year_salary.get_average_salary()
        self.city_salary.get_average_salary()
        self.city_salary.percent_add()
        return self

    def print_result(self):
        """
        Выполняет печать словарей

        :return: Возвращает данные в виде объекта Report для дальнейшей конвертации в нужный формат представления данных
        """
        year_salary = dict(sorted(self.year_salary.year_salary_dict.items(), key=lambda x: x[0]))
        count_salary = dict(sorted(self.count_salary.count_dict.items(), key=lambda x: x[0]))
        job_year_salary = dict(sorted(self.job_year_salary.year_salary_dict.items(), key=lambda x: x[0]))
        job_count_salary = dict(sorted(self.job_count_salary.count_dict.items(), key=lambda x: x[0]))
        city_salary = dict(
            itertools.islice(sorted(self.city_salary.year_salary_dict.items(), key=lambda x: x[1], reverse=True), 10))
        city_count = tuple(
            itertools.islice(sorted(self.city_count.count_dict.items(), key=lambda x: x[1], reverse=True), 10))
        print(f'Динамика уровня зарплат по годам: {year_salary}')
        print(f'Динамика количества вакансий по годам: {count_salary}')
        print(f'Динамика уровня зарплат по годам для выбранной профессии: {job_year_salary}')
        print(f'Динамика количества вакансий по годам для выбранной профессии: {job_count_salary}')
        print(f'Уровень зарплат по городам (в порядке убывания): {city_salary}')
        print(f'Доля вакансий по городам (в порядке убывания): {dict(city_count)}')
        return Report(profession_name=self.profession_name,
                      year_salary=year_salary,
                      count_salary=count_salary,
                      job_year_salary=job_year_salary,
                      job_count_salary=job_count_salary,
                      city_salary=city_salary,
                      city_count=city_count)


class Report:
    """
    Класс для представления данных отчета по анализу вакансий

    Attributes:
        profession_name (str): Название профессии
        year_salary (Dict[str, str]): Словарь в виде {год: оклад}
        count_salary (Dict[str, str]): Словарь в виде {количество: оклад}
        job_year_salary (Dict[str, str]): Словарь в виде {год: оклад} по указанной профессии
        job_count_salary (Dict[str, str]): Словарь в виде {количество: оклад} по указанной профессии
        city_salary (Dict[str, str]): Словарь в виде {город: оклад}
        city_count (Dict[str, str]): Словарь в виде {город: количество}

    """

    def __init__(self,
                 profession_name: str,
                 year_salary: Dict[str, str],
                 count_salary: Dict[str, str],
                 job_year_salary: Dict[str, str],
                 job_count_salary: Dict[str, str],
                 city_salary: Dict[str, str],
                 city_count: Tuple[Any]):
        """
        Инициализирует объект Report

        :param profession_name: Название профессии
        :param year_salary: Словарь в виде {год: оклад}
        :param count_salary: Словарь в виде {количество: оклад}
        :param job_year_salary: Словарь в виде {год: оклад} по указанной профессии
        :param job_count_salary: Словарь в виде {количество: оклад} по указанной профессии
        :param city_salary: Словарь в виде {город: оклад}
        :param city_count: Словарь в виде {город: количество}
        """
        self.profession_name = profession_name
        self.year_salary = year_salary
        self.count_salary = count_salary
        self.job_year_salary = job_year_salary
        self.job_count_salary = job_count_salary
        self.city_salary = city_salary
        self.city_count = city_count

    @staticmethod
    def __error_checker(file_name: str, file_type: str):
        """
        Проверяет вводимые данные на корректность

        :param file_name: Название файла
        :param file_type: Расширение файла
        """
        if isinstance(file_name, type(str)):
            raise TypeError('Указанное название файла имеет неправильный тип')
        if not file_name.endswith(file_type):
            raise KeyError('Указанный файл имеет неправильное расширение')

    def generate_excel(self, file_name: str) -> None:
        """
        Генерирует Excel-таблицу с анализом данных по вакансиям

        :param file_name: Название файла Excel-таблицы
        """
        self.__error_checker(file_name, '.xlsx')
        wb = openpyxl.Workbook()
        header_style = NamedStyle(name='headers')
        header_style.font = Font(bold=True)
        border = Side(style='thin', color='000000')
        header_style.border = Border(left=border, top=border, right=border, bottom=border)

        border_style = NamedStyle(name='cells')
        border_style.border = Border(left=border, top=border, right=border, bottom=border)
        wb.add_named_style(header_style)
        wb.add_named_style(border_style)
        wb.active.title = 'Статистика по годам'
        wb.create_sheet('Статистика по городам')

        sheet_stat_year = wb['Статистика по годам']
        first = self.__generate_years_table()
        for row in first:
            sheet_stat_year.append(row)

        sheet_stat_city = wb['Статистика по городам']
        second = list(self.__generate_city_table())
        for row in zip(second[0], second[1]):
            sheet_stat_city.append([*row[0], '', *row[1]])

        self.__styling_excel(sheet_stat_year)
        self.__styling_excel(sheet_stat_city)
        wb.save(file_name)

    @staticmethod
    def __styling_excel(sheet: openpyxl) -> None:
        """
        Выполняет стилизацию Excel-таблицы

        :param sheet: Лист Excel-таблицы
        """
        dimensions = {}
        for row in sheet.rows:
            for cell in row:
                if cell.value != '':
                    dimensions[cell.column_letter] = max((dimensions.get(cell.column_letter, 0), len(str(cell.value))))
                    cell.style = 'cells'
                else:
                    dimensions[cell.column_letter] = 0
                if sheet.title == 'Статистика по городам' and cell.column_letter == 'E':
                    cell.number_format = openpyxl.styles.numbers.FORMAT_PERCENTAGE_00
        for column, value in dimensions.items():
            if value > 0:
                sheet[f'{column}1'].style = 'headers'
            sheet.column_dimensions[column].width = value + 2

    def generate_image(self, file_name: str) -> None:
        """
        Генерирует изображение с визуальными данными по анализу вакансий

        :param file_name: Название файла изображения
        """
        self.__error_checker(file_name, '.png')
        graph = plt.figure()
        width = 0.4
        x_axis = np.arange(len(self.year_salary.keys()))

        first_graph = graph.add_subplot(221)
        first_graph.set_title('Уровень зарплат по годам')
        first_graph.bar(x_axis - width / 2, self.year_salary.values(), width, label='средняя з/п')
        first_graph.bar(x_axis + width / 2, self.job_year_salary.values(), width, label=f'з/п {self.profession_name}')
        first_graph.set_xticks(x_axis, self.year_salary.keys(), rotation='vertical')
        first_graph.tick_params(axis='both', labelsize=8)
        first_graph.legend(fontsize=8)
        first_graph.grid(True, axis='y')

        second_graph = graph.add_subplot(222)
        second_graph.set_title('Количество вакансий по годам')
        second_graph.bar(x_axis - width / 2, self.count_salary.values(), width, label='Количество вакансий')
        second_graph.bar(x_axis + width / 2, self.job_count_salary.values(), width,
                         label=f'Количество вакансий \n{self.profession_name}')
        second_graph.set_xticks(x_axis, self.count_salary.keys(), rotation='vertical')
        second_graph.tick_params(axis='both', labelsize=8)
        second_graph.legend(fontsize=8)
        second_graph.grid(True, axis='y')

        y_cities = np.arange(len(self.city_salary.keys()))
        third_graph = graph.add_subplot(223)
        third_graph.set_title('Уровень зарплат по годам')
        third_graph.barh(y_cities, self.city_salary.values(), 0.8, align='center')
        third_graph.set_yticks(y_cities, [key.replace('-', '-\n').replace(' ', '\n')
                                          for key in self.city_salary.keys()])
        third_graph.tick_params(axis='y', labelsize=6)
        third_graph.tick_params(axis='x', labelsize=8)
        third_graph.invert_yaxis()
        third_graph.grid(True, axis='x')

        fourth_graph = graph.add_subplot(224)
        fourth_graph.set_title('Доля вакансий по городам')
        city_stat = {'Другие': 1 - sum(dict(self.city_count).values()), **dict(self.city_count)}
        fourth_graph.pie(city_stat.values(),
                         labels=city_stat.keys(),
                         startangle=0,
                         textprops={'fontsize': 6},
                         radius=1.15)

        plt.tight_layout()
        plt.savefig(file_name)

    def generate_pdf(self, file_name: str) -> None:
        """
        Генерирует PDF-файл с данными по анализу вакансий

        :param file_name: Название PDF-файла
        """
        self.__error_checker(file_name, '.pdf')
        env = Environment(loader=FileSystemLoader('./'))
        template = env.get_template('template.html')

        first_table_data = self.__generate_years_table()
        second_table_data, third_table_data = self.__generate_city_table()
        pdf_template = template.render({
            'graph': 'graph.png',
            'first_table': first_table_data[1:],
            'second_table': second_table_data[1:],
            'third_table': list(
                map(lambda val: (val[0], '{:.2f}%'.format(val[1] * 100).replace('.', ',')), third_table_data[1:])),
            'first_table_header': first_table_data[0],
            'second_table_header': second_table_data[0],
            'third_table_header': third_table_data[0],
            'profession_name': self.profession_name
        })

        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, file_name, configuration=config, options={"enable-local-file-access": ""})

    def __generate_years_table(self) -> List[List[str]]:
        """
        Составляет список с данными по годам для Excel-таблицы
        :return: Возвращает список с данными для таблицы
        """
        headers = ['Год',
                   'Средняя зарплата',
                   f'Средняя зарплата - {self.profession_name}',
                   'Количество вакансий',
                   f'Количество вакансий - {self.profession_name}']
        rows = [[year, value, self.job_year_salary[year], self.count_salary[year], self.job_count_salary[year]]
                for year, value in self.year_salary.items()]
        return [headers, *rows]

    def __generate_city_table(self) -> (List[List[str]], List[List[str]]):
        """
        Составляет список с данными по городам для Excel-таблицы
        :return: Возвращает список с данными для таблицы
        """
        salary_city = [['Город', 'Уровень зарплат']]
        count_city = [['Город', 'Доля вакансий']]
        iterable_city_count = iter(self.city_count)
        for city, value in self.city_salary.items():
            city_count, value_count = next(iterable_city_count)
            salary_city.append([city, value])
            count_city.append([city_count, value_count])
        return salary_city, count_city


def generate_pdf():
    """
    Запускает генерацию PDF-файла
    """
    inputs = UserInput()
    AnalysisResult(DataSet(inputs.file_name), inputs.profession_name).get_results().print_result() \
        .generate_pdf(input('Введите название сохраняемого файла: '))

if __name__ == '__main__':
    generate_pdf()
