import pandas as pd
import requests
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
        self.df = pd.read_csv(file_name).sort_values(by='published_at')
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
            if self.df['salary_currency'][i] in self.currency_dict:
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

    def get_currency_csv(self, currency_list: List[str], start_date: datetime.date, end_date: datetime.date) -> None:
        """
        Формирует .csv файл с курсами валют в зависимости от даты

        :param currency_list: Список рассматриваемых валют
        :param start_date: Начальная дата выборки
        :param end_date: Конечная дата выборки
        """
        currency_df = pd.DataFrame(columns=['date'] + currency_list)
        dates = self.get_year_range(start_date, end_date)
        for date in dates:
            response = requests.get(f'http://www.cbr.ru/scripts/XML_daily.asp?date_req=28/{date}d=1')
            response = ElementTree.fromstring(response.content.decode("WINDOWS-1251"))
            currency_dict = {x: '' for x in currency_list}
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


data = DataSet('vacancies_dif_currencies.csv')
b = CurrencyData(data.df)
b.get_currency_csv(list(data.currency_dict.keys()), data.start_date, data.end_date)