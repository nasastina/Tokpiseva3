import GeneratePDF
import GenerateTable


def main():
    """
    Точка входа в программу. Начинает анализ данных по вакансиям и вывод отчета в формате таблицы или PDF-файла
    """
    report = input("Введите команду (Вакансии или Статистика): ")
    if report == "Вакансии":
        GenerateTable.generate_table()
    elif report == "Статистика":
        GeneratePDF.generate_pdf()
    else:
        raise NameError('Неизвестная команда')

# second
main()
