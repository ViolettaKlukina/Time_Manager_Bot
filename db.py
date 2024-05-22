import sqlite3
import logging
#from config import LOGS, DB_FILE

LOGS = '1.txt' 
DB_FILE = 'dbtest.db'


logging.basicConfig(filename=LOGS,
                    level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s",
                    filemode="w")

path_to_db = DB_FILE

def execute_query(query:str, data=None):
    """
    Функция для выполнения запроса к базе данных.
    Принимает имя файла базы данных, SQL-запрос и опциональные данные для вставки.
    """
    try:
        logging.info(f"DATABASE: Execute query: {query}")
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


def execute_selection_query(sql_query:str, data=None):
    '''Функция для выполнения любого sql-запроса для получения данных (возвращает значение)'''
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


def is_value_in_table(table_name:str, column_name:str, value):
    ''' возвращает bool + row данных'''
    '''Функция для проверки, есть ли элемент в указанном столбце таблицы \n
    Создаёт запрос SELECT колонка FROM имя_таблицы WHERE колонка == значение LIMIT 1'''
    sql_query = f'SELECT {column_name} FROM {table_name} WHERE {column_name} = ? order by date desc;'
    rows = execute_selection_query(sql_query, [value])
    if rows == None:
        logging.error(f'значение {value} столбца {column_name} не существует в таблице {table_name}')
        return False
    return rows


def is_user_data_here(user_id: int):
    '''возвращает bool + row данных'''
    if is_value_in_table('plan_system', 'user_id', user_id):
        system = select_plan_system(user_id)
        row = is_value_in_table(system, 'user_id', user_id)
        if row:
            return True, row
        else:
            logging.error(f'данные пользователя {user_id} не существуют в таблице {system}')
            False
    else:
        logging.error(f'пользователь {user_id} не существует в таблице {system}')
        False


def clean_record(user_id:int, table_name:str, column_name:str, column_value):
    '''возвращает False'''
    try:
        if is_value_in_table(table_name, column_name, column_value):
            sql_query = f'DELETE FROM {table_name} WHERE {column_name} = {column_value} and user_id = {user_id};'
            execute_query(sql_query)
        else:
            logging.error(f'данные пользователя {user_id} не существуют в таблице {table_name}')
            return False
    except sqlite3.Error as e:
        logging.error(f'данные пользователя {user_id} не существуют в таблице {table_name}')
        print("Ошибка при удалении данных:", e)


def clean_user(user_id:int, table_name:str):
    '''возвращает False'''
    try:
        if is_value_in_table(table_name, 'user_id', user_id):
            sql_query = f'DELETE FROM {table_name} WHERE user_id = {user_id};'
            execute_query(sql_query)
        else:
            logging.error(f'удаление данных о пользователе {user_id} из таблицы {table_name} не удалось')
            return False
    except sqlite3.Error as e:
        logging.error(f'Ошибка при удалении данных пользователя {user_id} из таблицы {table_name}:', e)
        print("Ошибка при удалении данных:", e)



def clean_table(table_name: str):
    try:
        execute_query(f'DELETE FROM {table_name}')
    except sqlite3.Error as e:
        logging.error(f'Ошибка при удалении данных таблицы {table_name}:', e)
        print("Ошибка при удалении данных:", e)


def select_plan_system(user_id:int):
    '''возвращает row данных или None'''
    row = execute_selection_query(f"SELECT system FROM plan_system WHERE VALUES user_id = {user_id};")
    print(row)
    return row


def create_database():
    '''возвращает None'''
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
    '''values = (user_id:  int , system_name:  str )'''
    columns = '(user_id, system)'
    sql_query = f"INSERT INTO plan_system {columns} VALUES (?, ?);"
    execute_query(sql_query, values)


def change_plan_system(user_id:int, plan_system_new:str):
    try:
        con = sqlite3.connect(path_to_db)
        cur = con.cursor()
        sql_query = f"UPDATE plan_system SET system = ? WHERE user_id = ?;"
        cur.execute(sql_query, (plan_system_new, user_id))
        con.commit() 
        con.close() 
        logging.info(f"DATABASE: сп изменена на {plan_system_new}")
    except sqlite3.Error as e:
        logging.error(f"DATABASE: Ошибка при запросе изменений: {e}")
        print("Ошибка при выполнении запроса:", e)


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
    '''values = (user_id:  int , main_task:  str , task:  str )'''
    columns = '(user_id, main_task, task)'
    sql_query = f"INSERT INTO gtd {columns} VALUES (?, ?, ?);"
    execute_query(sql_query, values)


def update_row_value_gtd(user_id:int, column_name:str, new_value:str):
    if is_value_in_table('gtd', 'user_id', user_id):
        sql_query = f'UPDATE gtd SET {column_name} = ? WHERE user_id = {user_id};'
        execute_query(sql_query, [new_value])
    else:
        logging.info(f"DATABASE: Пользователь с id = {user_id} не найден")
        print("Такого пользователя нет :(")


def select_gtd(user_id:int):
    columns = '(main_task, task)'
    row = execute_selection_query(f"SELECT {columns} FROM gtd WHERE VALUES user_id = {user_id};")
    print(row)
    return row


def tasks_list(user_id: int):
    if is_value_in_table('gtd', 'user_id', user_id):
        sql_query = f'SELECT task FROM gtd WHERE user_id = {user_id};'
        row = execute_selection_query(sql_query)
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
    '''values = (user_id:  int , done:  str , doing:  str , will do:  str )'''
    columns = '(user_id, done, doing, will do)'
    sql_query = f"INSERT INTO kanban {columns} VALUES (?, ?, ?, ?);"
    execute_query(sql_query, values)


def update_row_value_kanban(user_id:int, column_name:str, new_value:str):
    if is_value_in_table('kanban', 'user_id', user_id):
        sql_query = f'UPDATE kanban SET {column_name} = ? WHERE user_id = {user_id};'
        execute_query(sql_query, [new_value])
    else:
        logging.info(f"DATABASE: Пользователь с id = {user_id} не найден")
        print("Такого пользователя нет :(")


def select_kanban(user_id:int):
    columns = '(done, doing, will do)'
    row = execute_selection_query(f"SELECT {columns} FROM kanban WHERE VALUES user_id = {user_id};")
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
    '''values = (user_id:  int , imp_urg:  str , imp_nonur:  str , unimp_urg:  str , unimp_nonurg:  str )'''
    columns = '(user_id, imp_urg, imp_nonur, unimp_urg, unimp_nonurg)'
    sql_query = f"INSERT INTO matrix {columns} VALUES (?, ?, ?, ?);"
    execute_query(sql_query, values)


def update_row_value_matrix(user_id:int, column_name:str, new_value:str):
    if is_value_in_table('matrix', 'user_id', user_id):
        sql_query = f'UPDATE matrix SET {column_name} = ? WHERE user_id = {user_id};'
        execute_query(sql_query, [new_value])
    else:
        logging.info(f"DATABASE: Пользователь с id = {user_id} не найден")
        print("Такого пользователя нет :(")


def select_matrix(user_id:int):
    columns = '(imp_urg, imp_nonur, unimp_urg, unimp_nonurg)'
    row = execute_selection_query(f"SELECT {columns} FROM matrix WHERE VALUES user_id = {user_id};")
    return row


#REMINDER + POMODORO
def create_db_reminder():
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminder (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                send_time TEXT,
                text_mes TEXT);
            ''')
            logging.info("DATABASE: База данных напоминаний существует")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None


def insert_reminder(values):
    '''values = (user_id:  int , send_time:  str , text_mes:  str )'''
    columns = '(user_id, send_time, text_mes)'
    sql_query = f"INSERT INTO reminder {columns} VALUES (?, ?, ?);"
    execute_query(sql_query, values)


def select_reminder(user_id:int):
    columns = '(send_time, text_mes)'
    row = execute_selection_query(f"SELECT {columns} FROM reminder WHERE VALUES user_id = {user_id};")
    print(row)
    return row


def select_all_reminder():
    row = execute_selection_query(f"SELECT user_id, send_time, text_mes FROM reminder;")
    print(row)
    return row


def its_time(now_time:str):
    '''возвращает список из кортежей: [(user_id, send_time, text_mes), ... ]'''
    values = select_all_reminder()
    now_need = []
    for value in values:
        if now_time == value[1]:
            now_need += value
    return now_need
            

if __name__ == '__main__':
    create_database()
    create_db_gtd()
    create_db_kanban()
    create_db_matrix()
    create_db_reminder()