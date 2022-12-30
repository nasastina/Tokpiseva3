import pandas as pd
import sqlite3
from statistics import mean

class ValuteConverter:
    """
    Класс для представления функций по конвертации валют в вакансиях и создании .csv файла

    Attributes:
        df (DataFrame): Исходный фрейм данных вакансий
        currency_db (Connection): Подключенная БД с данными о курсах валют
        currencies (List[str]): Допустимые к обработке валюты
    """
    def __init__(self, df: pd.DataFrame):
        """
        Инициализирует класс ValuteConverter, формирует список допустимых к обработке валют

        :param df: Исходный фрейм данных вакансий, полученный после формирования файла курса валют
        """
        self.df = df
        self.currency_db = sqlite3.connect('db.sqlite')
        self.currencies = list(pd.read_sql("SELECT * from 'db.sqlite'", self.currency_db).keys()[1:])


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
            # multiplier = self.currency_df[self.currency_df['date'] == str(row[3])[:7]][salary_currency].iat[0]
            multiplier = pd.read_sql(f"SELECT {salary_currency} from 'db.sqlite' WHERE date='{str(row[3])[:7]}'",
                                     self.currency_db)[f'{salary_currency}'][0]
            if multiplier is not None:
                salary *= multiplier
            else:
                return 'nan'
        return salary

    def csv_to_vacancy_sql(self, db_name: str) -> None:
        """
        Преобразует .csv файл с данными о вакансиях в базу данных sqlite

        :param db_name: Имя файла БД
        """
        self.csv_create()
        connect = sqlite3.connect(db_name)
        cursor = connect.cursor()
        self.df.to_sql(name=db_name, con=connect, if_exists='replace', index=False)
        connect.commit()


ValuteConverter(pd.read_csv('vacancies_dif_currencies.csv')).csv_to_vacancy_sql('vacancy_db.sqlite')
