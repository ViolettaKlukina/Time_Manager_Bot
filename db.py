import sqlite3
import logging
from config import LOGS, DB_FILE




logging.basicConfig(filename=LOGS,
                    level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s",
                    filemode="w")

path_to_db = DB_FILE


def execute_query(query, data=None):
    try:
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        connection.commit()
        return cursor
    
    except sqlite3.Error as e:
        print("Ошибка при выполнении запроса:", e)

    finally:
        connection.close()


# Функция для выполнения любого sql-запроса для получения данных (возвращает значение)
def execute_selection_query(sql_query, data=None):
    try:
        logging.info(f"DATABASE: Execute query: {sql_query}")
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()
        if data:
            cursor.execute(sql_query, data)
        else:
            cursor.execute(sql_query)
        rows = cursor.fetchall()
        connection.close()
        return rows

    except sqlite3.Error as e:
        logging.error(f"DATABASE: Ошибка при запросе: {e}")
        print("Ошибка при выполнении запроса:", e)


def is_value_in_table(table_name, column_name, value):
    sql_query = f'SELECT {column_name} FROM {table_name} WHERE {column_name} = ? order by date desc'
    rows = execute_selection_query(sql_query, [value])
    return rows


def create_database():
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plan_system (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                system TEXT);
            ''')
            logging.info("DATABASE: База данных существует")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None
    

def insert_database(values):
    columns = '(user_id, system)'
    sql_query = f"INSERT INTO plan_system {columns} VALUES (?, ?)"
    execute_query(sql_query, values)


def change_plan_system(user_id, plan_system_new):
    con = sqlite3.connect(path_to_db)
    cur = con.cursor()
    sql_query = f"UPDATE plan_system SET system = ? WHERE user_id = ?;"
    cur.execute(sql_query, (plan_system_new, user_id))
    con.commit() 
    con.close() 
    logging.info(f"DATABASE: сп изменена на {plan_system_new}")


# GTD
def create_db_gtd():
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gtd (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                main_task TEXT,
                task TEXT);
            ''')
            logging.info("DATABASE: База данных GTD существует")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None


def insert_gtd(values):
    columns = '(user_id, main_task, task)'
    sql_query = f"INSERT INTO gtd {columns} VALUES (?, ?, ?)"
    execute_query(sql_query, values)


def update_row_value_gtd(user_id, column_name, new_value):
    if is_value_in_table('gtd', 'user_id', user_id):
        sql_query = f'UPDATE gtd SET {column_name} = ? WHERE user_id = {user_id}'
        execute_query(sql_query, [new_value])
    else:
        logging.info(f"DATABASE: Пользователь с id = {user_id} не найден")
        print("Такого пользователя нет :(")

    
def select_gtd(user_id):
    columns = '(main_task, task)'
    row = execute_selection_query(f"SELECT {columns} FROM gtd WHERE VALUES user_id = {user_id}")
    print(row)
    return row


#KANBAN
def create_db_kanban():
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kanban (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                done TEXT,
                doing TEXT,
                will do TEXT);
            ''')
            logging.info("DATABASE: База данных Канбан существует")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None
    

def insert_kanban(values):
    columns = '(user_id, done, doing, will do)'
    sql_query = f"INSERT INTO kanban {columns} VALUES (?, ?, ?, ?)"
    execute_query(sql_query, values)


def update_row_value_kanban(user_id, column_name, new_value):
    if is_value_in_table('kanban', 'user_id', user_id):
        sql_query = f'UPDATE kanban SET {column_name} = ? WHERE user_id = {user_id}'
        execute_query(sql_query, [new_value])
    else:
        logging.info(f"DATABASE: Пользователь с id = {user_id} не найден")
        print("Такого пользователя нет :(")


def select_kanban(user_id):
    columns = '(done, doing, will do)'
    row = execute_selection_query(f"SELECT {columns} FROM kanban WHERE VALUES user_id = {user_id}")
    return row


#MATRIX
def create_db_matrix():
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matrix (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                imp_urg TEXT,
                imp_nonur TEXT,
                unimp_urg TEXT,
                unimp_nonurg TEXT);
            ''')
            logging.info("DATABASE: База данных МАТРИЦА ЭЙЗЕНХАУЭРА существует")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None
    

def insert_matrix(values):
    columns = '(user_id, imp_urg, imp_nonur, unimp_urg, unimp_nonurg)'
    sql_query = f"INSERT INTO matrix {columns} VALUES (?, ?, ?, ?, ?)"
    execute_query(sql_query, values)


def update_row_value_matrix(user_id, column_name, new_value):
    if is_value_in_table('matrix', 'user_id', user_id):
        sql_query = f'UPDATE matrix SET {column_name} = ? WHERE user_id = {user_id}'
        execute_query(sql_query, [new_value])
    else:
        logging.info(f"DATABASE: Пользователь с id = {user_id} не найден")
        print("Такого пользователя нет :(")


def select_matrix(user_id):
    columns = '(imp_urg, imp_nonur, unimp_urg, unimp_nonurg)'
    row = execute_selection_query(f"SELECT {columns} FROM matrix WHERE VALUES user_id = {user_id}")
    return row


#REMINDER
def create_db_reminder():
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminder (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                send_time INT,
                text_mes TEXT);
            ''')
            logging.info("DATABASE: База данных напоминаний существует")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None


def insert_reminder(values):
    columns = '(user_id, send_time, text_mes)'
    sql_query = f"INSERT INTO reminder {columns} VALUES (?, ?, ?)"
    execute_query(sql_query, values)


def select_reminder(user_id):
    columns = '(send_time, text_mes)'
    row = execute_selection_query(f"SELECT {columns} FROM reminder WHERE VALUES user_id = {user_id}")
    return row