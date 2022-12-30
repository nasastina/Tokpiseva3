from unittest import TestCase

from GeneratePDF import Vacancy
from GeneratePDF import VacancySalaryDict
from GeneratePDF import DataSet


class VacancyTests(TestCase):
    vacancies = {
        'name': 'Программист',
        'salary_from': '40000.0',
        'salary_to': '55000.0',
        'salary_currency': 'RUR',
        'area_name': 'Москва',
        'published_at': '2012-04-09T13:49:00+0400',
    }

    def test_vacancy_type(self):
        self.assertEqual(type(Vacancy(self.vacancies)).__name__, 'Vacancy')

    def test_vacancy_name(self):
        self.assertEqual(Vacancy(self.vacancies).name, 'Программист')

    def test_vacancy_salary(self):
        self.assertEqual(Vacancy(self.vacancies).salary, 47500)

    def test_vacancy_area(self):
        self.assertEqual(Vacancy(self.vacancies).area_name, 'Москва')

    def test_vacancy_published(self):
        self.assertEqual(Vacancy(self.vacancies).published_at, 2012)


class VacancySalaryDictTests(TestCase):
    salary_dict = VacancySalaryDict()

    def test_salary_dict_type(self):
        self.assertEqual(type(self.salary_dict).__name__, 'VacancySalaryDict')

    def test_salary_dict_add(self):
        self.salary_dict.add(200, 2022)
        self.assertEqual(self.salary_dict.length, 1)
        self.assertEqual(self.salary_dict.year_salary_dict, {2022: 200})
        self.assertEqual(self.salary_dict.year_count_dict, {2022: 1})

        self.salary_dict.add(100, 2021)
        self.assertEqual(self.salary_dict.length, 2)
        self.assertEqual(self.salary_dict.year_salary_dict, {2022: 200, 2021: 100})
        self.assertEqual(self.salary_dict.year_count_dict, {2022: 1, 2021: 1})

        self.salary_dict.add(100, 2022)
        self.assertEqual(self.salary_dict.length, 3)
        self.assertEqual(self.salary_dict.year_salary_dict, {2022: 300, 2021: 100})
        self.assertEqual(self.salary_dict.year_count_dict, {2022: 2, 2021: 1})

    salary_dict_area = VacancySalaryDict()

    def test_salary_dict_add_area(self):
        self.salary_dict_area.add_area(200, 'Москва')
        self.assertEqual(self.salary_dict_area.length, 1)
        self.assertEqual(self.salary_dict_area.area_salary_dict, {'Москва': 200})
        self.assertEqual(self.salary_dict_area.year_count_dict, {'Москва': 1})

        self.salary_dict_area.add_area(100, 'Москва')
        self.assertEqual(self.salary_dict_area.length, 2)
        self.assertEqual(self.salary_dict_area.area_salary_dict, {'Москва': 300})
        self.assertEqual(self.salary_dict_area.year_count_dict, {'Москва': 2})

        self.salary_dict_area.add_area(100, 'Екатеринбург')
        self.assertEqual(self.salary_dict_area.length, 3)
        self.assertEqual(self.salary_dict_area.area_salary_dict, {'Москва': 300, 'Екатеринбург': 100})
        self.assertEqual(self.salary_dict_area.year_count_dict, {'Москва': 2, 'Екатеринбург': 1})

    def test_salary_dict_avg_salary(self):
        salary_dict = VacancySalaryDict()
        self.assertEqual(salary_dict.get_average_salary(), None)

        salary_dict.add(100, 2022)
        salary_dict.add(200, 2022)
        salary_dict.add(300, 2022)
        salary_dict.get_average_salary()
        self.assertEqual(salary_dict.year_salary_dict[2022], 200)

        salary_dict.add_not_contains(2023)
        salary_dict.get_average_salary()
        self.assertEqual(salary_dict.year_salary_dict[2023], 0)


class DataSetTests(TestCase):
    dataset = DataSet('vaca.csv')

    def test_dataset_type(self):
        self.assertEqual(type(self.dataset).__name__, 'DataSet')

    def test_dataset_objects(self):
        self.assertEqual(len(self.dataset.vacancies_objects), 2)
        self.assertEqual(type(self.dataset.vacancies_objects[0]).__name__, 'Vacancy')
        self.assertEqual(self.dataset.vacancies_objects[0].name, 'Специалист')
        self.assertEqual(self.dataset.vacancies_objects[1].name, 'Менеджер')
        self.assertEqual(self.dataset.vacancies_objects[0].area_name, 'Санктg-Петербург')
