import sqlite3
import logging
#from config import LOGS, DB_FILE

LOGS = '1.txt' #elfkbnm cnhjre? rjulf ,eltn dc` zcyj c rjyabujv`
DB_FILE = 'узнайте в confige.'


logging.basicConfig(filename=LOGS,
                    level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s",
                    filemode="w")

path_to_db = DB_FILE

def create_database():
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plan_systems (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                system TEXT)
            ''')
            logging.info("DATABASE: База данных существует")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None
    

def change_plan_system(user_id, plan_system_new):
    con = sqlite3.connect(path_to_db)
    cur = con.cursor()
    sql_query = f"UPDATE plan_systems SET system = ? WHERE user_id = ?;"
    cur.execute(sql_query, (plan_system_new, user_id))
    con.commit() 
    con.close() 
    logging.info(f"DATABASE: сп изменена на {plan_system_new}")


def insert_database(user_id, plan_system):
    try:
        con = sqlite3.connect(path_to_db)
        cur = con.cursor()
        query = f'''INSERT INTO plan_systems (user_id, plan_system) VALUES (?, ?);'''
        cur.execute(query, (user_id, plan_system))
        con.commit()
    except sqlite3.Error as e:
        logging.ERROR("Ошибка при работе с SQLite:", e)
    finally:
        con.close()


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
                task TEXT,
                mini_task TEXT)
            ''')
            logging.info("DATABASE: База данных GTD существует")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None
    




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
                will do TEXT)
            ''')
            logging.info("DATABASE: База данных Канбан существует")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None
    

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
                unimp_nonurg TEXT)
            ''')
            logging.info("DATABASE: База данных МАТРИЦА ЭЙЗЕНХАУЭРА существует")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None
    

def create_db_pomodoro():
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pomodoro (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                send_time INT,
                work_time INT,
                rest_time INT)
            ''')
            logging.info("DATABASE: База данных Помодоро существует")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None