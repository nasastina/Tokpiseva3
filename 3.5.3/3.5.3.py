import pandas as pd
import sqlite3

vacancy_name = input()

db = sqlite3.connect('python_proj.db')
c = db.cursor()
salary_by_year = pd.read_sql("SELECT strftime('%Y', published_at) as Year, ROUND(AVG(salary)) as avg_salary FROM vacancies WHERE salary is not null GROUP BY strftime('%Y', published_at)", db)
print('Динамика уровня зарплат по годам:')
print(salary_by_year.to_string(index=False))

count_by_year = pd.read_sql("SELECT strftime('%Y', published_at) as Year, COUNT(name) as count_vacancies FROM vacancies GROUP BY strftime('%Y', published_at)", db)
print('Динамика количества вакансий по годам:')
print(count_by_year.to_string(index=False))

selected_salary_by_year = pd.read_sql(f"SELECT strftime('%Y', published_at) as Year, ROUND(AVG(salary)) as avg_salary_for_selected FROM vacancies WHERE salary is not null AND LOWER(name) LIKE '%{vacancy_name.lower()}%' GROUP BY strftime('%Y', published_at)", db)
print('Динамика уровня зарплат по годам для выбранной профессии:')
print(selected_salary_by_year.to_string(index=False))

selected_count_by_year = pd.read_sql(f"SELECT strftime('%Y', published_at) as Year, COUNT(name) as count_vacancies_for_selected FROM vacancies WHERE LOWER(name) LIKE '%{vacancy_name.lower()}%' GROUP BY strftime('%Y', published_at)", db)
print('Динамика количества вакансий по годам для выбранной профессии:')
print(selected_count_by_year.to_string(index=False))

len_table = int(c.execute("SELECT COUNT(*) FROM vacancies WHERE salary is not null ").fetchall()[0][0])

salary_by_area = pd.read_sql(f"SELECT area_name, ROUND(AVG(salary)) as avg_salary FROM vacancies WHERE salary is not null GROUP BY area_name HAVING COUNT(name) >= {len_table // 100} ORDER BY avg_salary DESC LIMIT 10", db)
print('Уровень зарплат по городам:')
print(salary_by_area.to_string(index=False))

fraction_by_area = pd.read_sql(f"SELECT area_name, ROUND(COUNT(salary) / {len_table}.0, 3) as fraction_vacancies FROM vacancies GROUP BY area_name HAVING COUNT(name) >= {len_table // 100} ORDER BY fraction_vacancies DESC LIMIT 10", db)
print('Доля вакансий по городам:')
print(fraction_by_area.to_string(index=False))