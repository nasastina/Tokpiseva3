import csv
import os


def custom_exit(message: str) -> None:
    """
    Выполняет выход из программы с пользовательским выводом.

    :param message: Сообщение для вывода
    """
    print(message)
    exit()


def separate_csv(file_name: str) -> None:
    """
    Выполняет разделение исходного csv-файла на отдельные csv-файлы по годам.
    Сохраняет новые csv-файлы в папку vacancies

    :param file_name: Название исходного файла
    """
    separated_vacancies = {}
    vacancies = [line for line in csv.reader(open(file_name, encoding='utf-8-sig'))]
    if len(vacancies) == 0:
        custom_exit('Пустой файл')
    for vacancy in [dict(zip(vacancies[0], value)) for value in vacancies[1:]]:
        if separated_vacancies.get(vacancy['published_at'][:4]) is None:
            separated_vacancies[vacancy['published_at'][:4]] = [vacancy]
        else:
            separated_vacancies[vacancy['published_at'][:4]].append(vacancy)

    os.mkdir('../3.2.2-3.2.3/vacancies')
    for year in separated_vacancies.keys():
        with open(f'../3.2.2-3.2.3/vacancies/{year}.csv', mode="w", encoding='utf-8-sig') as write_file:
            file_writer = csv.DictWriter(write_file,
                                         delimiter=",",
                                         lineterminator="\r",
                                         fieldnames=vacancies[0])
            file_writer.writeheader()
            file_writer.writerows(separated_vacancies[year])

separate_csv(r'..\csv\vacancies_by_year.csv')