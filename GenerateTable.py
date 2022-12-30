import csv
import re
import datetime as DT
from enum import Enum
from prettytable import PrettyTable
from typing import List, Dict, Tuple, Any


class FieldsTranslator(Enum):
    name = 'Название'
    description = 'Описание'
    key_skills = 'Навыки'
    experience_id = 'Опыт работы'
    premium = 'Премиум-вакансия'
    employer_name = 'Компания'
    salary_from = 'Оклад'
    salary_to = 'Верхняя граница вилки оклада'
    salary_gross = 'Оклад указан до вычета налогов'
    salary_currency = 'Идентификатор валюты оклада'
    area_name = 'Название региона'
    published_at = 'Дата публикации вакансии'


class ValuteTranslator(Enum):
    AZN = "Манаты"
    BYR = "Белорусские рубли"
    EUR = "Евро"
    GEL = "Грузинский лари"
    KGS = "Киргизский сом"
    KZT = "Тенге"
    RUR = "Рубли"
    UAH = "Гривны"
    USD = "Доллары"
    UZS = "Узбекский сум"


class ExperienceTranslator(Enum):
    noExperience = "Нет опыта"
    between1And3 = "От 1 года до 3 лет"
    between3And6 = "От 3 до 6 лет"
    moreThan6 = "Более 6 лет"


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
    Класс для представления данных вакансии

    Attributes:
        name (str): Название вакансии
        description (str): Описание вакансии
        key_skills (str): Навыки
        experience_id (str): Опыт работы
        premium (str): Премиум-вакансия
        employer_name (str): Название компании
        salary (Salary): Оклад
        area_name (str): Город вакансии
        published_at (str): Дата публикации вакансии
    """
    def __init__(self, vacancy: Dict):
        self.name = vacancy['name']
        self.description = vacancy['description']
        self.key_skills = vacancy['key_skills']
        self.experience_id = vacancy['experience_id']
        self.premium = vacancy['premium']
        self.employer_name = vacancy['employer_name']
        self.salary = Salary(salary_from=vacancy['salary_from'],
                             salary_to=vacancy['salary_to'],
                             salary_gross=vacancy['salary_gross'],
                             salary_currency=vacancy['salary_currency'])
        self.area_name = vacancy['area_name']
        self.published_at = vacancy['published_at']


class Salary:
    """
    Класс для представления данных зарплаты

    Attributes:
        salary_from (str): Нижняя граница оклада
        salary_to (str): Верхняя граница оклада
        salary_gross (str): Вычет налогов
        salary_currency (str): Идентификатор валюты оклада
    """
    def __init__(self, salary_from: str, salary_to: str, salary_gross: str, salary_currency: str):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency

    def rub_convert(self) -> Tuple[float, float]:
        currency_to_rub = {
            "AZN": 35.68,
            "BYR": 23.91,
            "EUR": 59.90,
            "GEL": 21.74,
            "KGS": 0.76,
            "KZT": 0.13,
            "RUR": 1,
            "UAH": 1.64,
            "USD": 60.66,
            "UZS": 0.0055,
        }
        return float(self.salary_from) * currency_to_rub[self.salary_currency], \
               float(self.salary_to) * currency_to_rub[self.salary_currency]


def filter_premium(vacancies: List[Vacancy], value: str) -> List[Vacancy]:
    """
    Производит фильтрацию списка вакансий по параметру "Премиум-вакансия"

    :param vacancies: Список вакансий
    :param value: Значение параметра "Премиум-вакансия"
    :return: Возвращает отфильтрованный по параметру "Премиум-вакансия" список вакансий
    """
    dict_translator = {
        'Да': 'True',
        'Нет': 'False'
    }
    return [vacancy for vacancy in vacancies if vacancy.premium == dict_translator[value]]


filter_dict = {
    'Название': lambda vacancies, value: [vacancy for vacancy in vacancies if vacancy.name == value],
    'Описание': lambda vacancies, value: [vacancy for vacancy in vacancies if vacancy.description == value],
    'Навыки': lambda vacancies, value: [vacancy for vacancy in vacancies
                                        if set(value.split(', ')).issubset(vacancy.key_skills.split('\n'))],
    'Опыт работы': lambda vacancies, value: [vacancy for vacancy in vacancies
                                             if ExperienceTranslator[vacancy.experience_id].value == value],
    'Премиум-вакансия': filter_premium,
    'Оклад': lambda vacancies, value: [vacancy for vacancy in vacancies
                                       if int(vacancy.salary.salary_from) <= int(value) <= int(vacancy.salary.salary_to)],
    'Идентификатор валюты оклада': lambda vacancies, value: [vacancy for vacancy in vacancies
                                                             if ValuteTranslator[
                                                                 vacancy.salary.salary_currency].value == value],
    'Название региона': lambda vacancies, value: [vacancy for vacancy in vacancies if vacancy.area_name == value],
    'Дата публикации вакансии': lambda vacancies, value: [vacancy for vacancy in vacancies
                                                          if vacancy.published_at[0:10] ==
                                                          DT.datetime.strptime(value.replace('.', '-'), '%d-%m-%Y')
                                                              .date().strftime('%Y-%m-%d')],
    'Компания': lambda vacancies, value: [vacancy for vacancy in vacancies if vacancy.employer_name == value]
}


def exp_sort(x):
    """
    Сортировка по опыту работы

    :param x: Параметр опыта работы
    :return: Возвращает значимость параметра опыта работы
    """
    exp_dict = {
        'noExperience': 0,
        'between1And3': 1,
        'between3And6': 2,
        'moreThan6': 3
    }
    return exp_dict[x]


sort_dict = {
    'Название': lambda vacancies, order: sorted(vacancies, key=lambda s: s.name, reverse=order),
    'Описание': lambda vacancies, order: sorted(vacancies, key=lambda s: s.description, reverse=order),
    'Навыки': lambda vacancies, order: sorted(vacancies, key=lambda s: len(s.key_skills.split('\n')), reverse=order),
    'Опыт работы': lambda vacancies, order: sorted(vacancies, key=lambda s: exp_sort(s.experience_id),
                                                   reverse=order),
    'Премиум-вакансия': lambda vacancies, order: sorted(vacancies, key=lambda s: s.premium, reverse=order),
    'Оклад': lambda vacancies, order: sorted(vacancies,
                                             key=lambda s: int(int(s.salary.rub_convert()[0] +
                                                                   s.salary.rub_convert()[1]) / 2),
                                             reverse=order),
    'Идентификатор валюты оклада': lambda vacancies, order: sorted(vacancies, key=lambda s: s.salary.salary_currency,
                                                                   reverse=order),
    'Название региона': lambda vacancies, order: sorted(vacancies, key=lambda s: s.area_name, reverse=order),
    'Дата публикации вакансии': lambda vacancies, order: sorted(vacancies, key=lambda s: s.published_at,
                                                                reverse=order),
    'Компания': lambda vacancies, order: sorted(vacancies, key=lambda s: s.employer_name, reverse=order)
}


class InputConnect:
    """
    Класс для представления методов для работы со списком вакансий
    """
    @staticmethod
    def formatter(vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Производит форматирование списка вакансий

        :param vacancies: Список вакансий
        :return: Возвращает отформатированный список вакансий
        """
        for vacancy in vacancies:
            if vacancy.premium == 'False':
                vacancy.premium = 'Нет'
            else:
                vacancy.premium = 'Да'
            if vacancy.salary.salary_gross == 'False':
                vacancy.salary.salary_gross = 'Нет'
            else:
                vacancy.salary.salary_gross = 'Да'
            vacancy.salary.salary_currency = ValuteTranslator[vacancy.salary.salary_currency].value
            vacancy.experience_id = ExperienceTranslator[vacancy.experience_id].value
            datetime = DT.datetime.strptime(vacancy.published_at[0:10].replace('-', ''), '%Y%m%d').date()
            vacancy.published_at = datetime.strftime('%d.%m.%Y')
            if vacancy.salary.salary_gross == 'Да':
                vacancy.salary.salary_gross = 'Без вычета налогов'
            else:
                vacancy.salary.salary_gross = 'С вычетом налогов'
            vacancy.salary = f"{'{0:,}'.format(int(float(vacancy.salary.salary_from))).replace(',', ' ')} - " \
                             f"{'{0:,}'.format(int(float(vacancy.salary.salary_to))).replace(',', ' ')} " \
                             f"({vacancy.salary.salary_currency}) ({vacancy.salary.salary_gross})"
        return vacancies

    @staticmethod
    def filtrate(string: str, vacancies: List[Vacancy]) -> List[Vacancy]:
        """
        Производит фильтрацию по указанным параметрам

        :param string: Параметр фильтрации
        :param vacancies: Список вакансий
        :return: Возвращает отфильтрованный список вакансий
        """
        if string == '':
            return vacancies
        header, value = string.split(': ')
        results = filter_dict[header](vacancies, value)
        if len(results) == 0:
            custom_exit('Ничего не найдено')
        return results

    @staticmethod
    def sorting(string: str, vacancies: List[Vacancy], order: str) -> List[Vacancy]:
        """
        Производит сортировку по указанным параметрам

        :param string: Параметр сортировки
        :param vacancies: Список вакансий
        :param order: Параметр порядка сортировки
        :return: Возвращает отсортированный список вакансий
        """
        sort_order = False
        if order == 'Да':
            sort_order = True
        if string == '':
            return vacancies
        return sort_dict[string](vacancies, sort_order)


class Table:
    """
    Класс для представления данных таблицы PrettyTable

    Attributes:
        table (PrettyTable): Объект таблицы PrettyTable
    """
    def __init__(self):
        """
        Инициализирует объект Table, задает стандартные стили таблицы
        """
        self.table = PrettyTable(['Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия', 'Компания',
                                  'Оклад', 'Название региона', 'Дата публикации вакансии'])
        self.table.hrules = 1
        self.table.align = 'l'
        self.table.max_width = 20

    def __make_table(self, data_vacancies: List[Vacancy]) -> None:
        """
        Создает таблицу

        :param data_vacancies: Список всех вакансий
        """
        if len(data_vacancies) == 0:
            custom_exit('Нет данных')
        for vacancy in InputConnect.formatter(data_vacancies):
            row = []
            for value in vacancy.__dict__.values():
                row.append(value[:100] + '...') if len(value) > 100 else row.append(value)
            self.table.add_row(row)
        self.table.add_autoindex('№')

    def print_table(self, output_range: str, table_rows: str, sorting_param: str,
                    filter_param: str, reverse_sort_param: str, file_name: str) -> None:
        """
        Печатает таблицу в консоль

        :param output_range: Диапазон выводимых строк
        :param table_rows: Выводимые столбцы таблицы
        :param sorting_param: Параметр сортировки
        :param filter_param: Параметр фильтрации
        :param reverse_sort_param: Параметр обратной сортировки
        :param file_name: Имя файла исходных данных
        """
        self.__make_table(InputConnect.sorting(sorting_param,
                                               InputConnect.filtrate(filter_param,
                                                                     DataSet(file_name).vacancies_objects),
                                               reverse_sort_param))
        distances = [1, len(self.table.rows) + 1] if len(output_range) == 0 else output_range.split(' ')
        table_rows = self.table.field_names if len(table_rows) == 0 else ['№'] + table_rows.split(', ')
        if len(distances) == 1:
            distances.append(len(self.table.rows) + 1)
        print(self.table.get_string(start=int(distances[0]) - 1, end=int(distances[1]) - 1, fields=table_rows))


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
        file_name (str): Имя файла исходных данных
        filter_param (str): Параметр фильтрации
        sorting_param (str): Параметр сортировки
        reverse_sort_param (str): Параметр обратной сортировки
        output_range (str): Диапазон выводимых строк
        table_rows (str): Выводимые столбцы таблицы

    """
    def __init__(self):
        """
        Инициализирует объект UserInput
        """
        inputs = [
            'Введите название файла',
            'Введите параметр фильтрации',
            'Введите параметр сортировки',
            'Обратный порядок сортировки (Да / Нет)',
            'Введите диапазон вывода',
            'Введите требуемые столбцы'
        ]
        values = [input(f'{inputs[i]}: ') for i in range(len(inputs))]
        self.file_name = values[0]
        self.filter_param = values[1]
        self.sorting_param = values[2]
        self.reverse_sort_param = values[3]
        self.output_range = values[4]
        self.table_rows = values[5]
        self.__error_checker()

    def __error_checker(self) -> None:
        """
        Проверяет вводимые данные на корректность
        """
        try:
            headers = next(csv.reader(open(self.file_name, 'r', encoding='utf-8-sig')))
        except:
            custom_exit('Пустой файл')
        if self.reverse_sort_param not in ['Да', 'Нет', '']:
            custom_exit('Порядок сортировки задан некорректно')
        if self.sorting_param not in [FieldsTranslator[header].value for header in headers] + ['']:
            custom_exit('Параметр сортировки некорректен')
        if self.filter_param == '':
            return
        try:
            header, value = self.filter_param.split(': ')
        except:
            custom_exit('Формат ввода некорректен')
        if header not in [FieldsTranslator[header].value for header in headers] + ['']:
            custom_exit('Параметр поиска некорректен')


def generate_table():
    """
    Запускает генерацию таблицы и ее печать
    """
    inputs = UserInput()
    Table().print_table(file_name=inputs.file_name,
                        filter_param=inputs.filter_param,
                        sorting_param=inputs.sorting_param,
                        reverse_sort_param=inputs.reverse_sort_param,
                        output_range=inputs.output_range,
                        table_rows=inputs.table_rows)
