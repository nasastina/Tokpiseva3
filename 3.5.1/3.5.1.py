import pandas as pd
import sqlite3


def convert_csv_to_sql(file_name: str, db_name: str) -> None:
    """
    Создает базу данных на основе .csv файла

    :param file_name: Имя исходного .csv файла
    :param db_name: Имя базы данных sqlite
    """
    df = pd.read_csv(file_name)
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    df.to_sql(name=db_name, con=connect, if_exists='replace', index=False)
    connect.commit()


if __name__ == '__main__':
    convert_csv_to_sql('currency.csv', 'db.sqlite')