import pandas as pd
import requests
from statistics import mean
from typing import List
from xml.etree import ElementTree
from datetime import datetime
from dateutil.relativedelta import relativedelta


class DataSet:
    """
    Класс для представления DataSet - объекта, хранящего в себе данные о вакансиях

    Attributes:
        df (DataFrame): Фрейм данных вакансий
        currency_dict (dict): Словарь частотности валют в вакансиях
        start_date (date): Начальная дата (самая старая вакансия в выборке)
        end_date (date): Конечная дата (самая новая вакансия в выборке)
    """
    def __init__(self, file_name: str):
        """
        Инициализирует класс DataSet, производит подсчет частности встречающихся валют в вакансиях

        :param file_name: Имя файла исходных данных в .csv формате
        """
        self.df = pd.read_csv(file_name).sort_values(by='published_at').reset_index(drop=True)
        self.currency_dict = {}
        self.get_currency_count()
        self.start_date = self.get_date(range(len(self.df)))
        self.end_date = self.get_date(range(len(self.df) - 1, -1, -1))

    def get_currency_count(self) -> None:
        """
        Производит подсчет частотности встречающихся валют в вакансиях
        """
        for i in range(len(self.df)):
            key = self.df['salary_currency'][i]
            if str(key) == 'nan' or str(key) == 'RUR':
                continue
            if key not in self.currency_dict:
                self.currency_dict[key] = 0
            self.currency_dict[key] += 1
        print(self.currency_dict)
        self.currency_dict = dict([x for x in self.currency_dict.items() if x[1] > 5000])
        self.currency_dict = dict(sorted(self.currency_dict.items(), key=lambda x: x[0]))

    def get_date(self, date_range) -> datetime.date:
        """
        Производит перебор по началу и концу списка вакансий в поисках самой старой и новой вакансии соответственно

        :param date_range: Задает промежуток вакансий, который нужно рассмотреть
        :return: Возвращает дату вакансии в формате (date)
        """
        for i in date_range:
            if self.df['salary_currency'][i] in self.currency_dict or self.df['salary_currency'][i] == 'RUR':
                return datetime.strptime(self.df['published_at'][i], '%Y-%m-%dT%H:%M:%S%z').date()


class CurrencyData:
    """
    Класс для представления данных о курсах валют

    Attributes:
        df (DataFrame): Фрейм данных вакансий
    """
    def __init__(self, df):
        """
        Инициализирует класс CurrencyData

        :param df: Фрейм данных вакансий из класса DataSet
        """
        self.df = df

    @staticmethod
    def get_year_range(start: datetime.date, end: datetime.date) -> List[str]:
        """
        Определяет нужные даты в формате месяц/год для дальнейшего использования в запросах

        :param start: Начальная дата выборки
        :param end: Конечная дата выборки
        :return: Возвращает список дат для текущей выборки
        """
        result = []
        start = start + relativedelta(day=1)
        end = end + relativedelta(day=28)
        while start < end:
            result.append(start.strftime('%m/%Y'))
            start = start + relativedelta(months=1)
        return result

    def get_currency_csv(self, currency_list: List[str], start_date: datetime.date, end_date: datetime.date) -> pd.DataFrame:
        """
        Формирует .csv файл с курсами валют в зависимости от даты

        :param currency_list: Список рассматриваемых валют
        :param start_date: Начальная дата выборки
        :param end_date: Конечная дата выборки
        :return: Возвращает фрейм с курсами валют в разные годы
        """
        currency_df = pd.DataFrame(columns=['date'] + currency_list)
        dates = self.get_year_range(start_date, end_date)
        for date in dates:
            response = requests.get(f'http://www.cbr.ru/scripts/XML_daily.asp?date_req=28/{date}d=1')
            response = ElementTree.fromstring(response.content.decode("WINDOWS-1251"))
            currency_dict = {x: None for x in currency_list}
            for valute in response.findall('./Valute'):
                if valute.find('./CharCode').text in currency_list:
                    currency_dict[valute.find('./CharCode').text] = \
                        round(float(valute.find('./Value').text.replace(',', '.')) /
                              int(valute.find('./Nominal').text), 4)
                    if all(currency_dict.values()):
                        break
            currency_dict = sorted(currency_dict.items(), key=lambda x: x[0])
            currency = [x[1] for x in currency_dict]
            currency_df.loc[len(currency_df.index)] = [datetime.strptime(date, '%m/%Y').strftime('%Y-%m')] + currency
        currency_df.to_csv('currency.csv', index=False)
        return currency_df

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

    def csv_create(self) -> None:
        """
        Создает .csv файл с обработанными вакансиями, у которых зарплата переведена по курсу валют
        """
        self.df.insert(1, 'salary', None)
        self.df['salary'] = self.df[['salary_from', 'salary_to', 'salary_currency', 'published_at']]\
                                                        .apply(self.get_salary, axis=1)
        self.df.drop(labels=['salary_to', 'salary_from', 'salary_currency'], axis=1, inplace=True)
        self.df = self.df.loc[self.df['salary'] != 'nan']
        self.df.to_csv('csv_result.csv', index=False)

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

data = DataSet('vacancies_dif_currencies.csv')
currency_data = CurrencyData(data.df)
currency_csv = currency_data.get_currency_csv(list(data.currency_dict.keys()), data.start_date, data.end_date)
converted_csv = ValuteConverter(data.df, currency_csv)
converted_csv.csv_create()
