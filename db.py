import sqlite3
import logging
from config import LOGS, DB_FILE

logging.basicConfig(filename=LOGS,
                    level=logging.DEBUG,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s",
                    filemode="w")

path_to_db = DB_FILE

def execute_query(query:str, data=None):
    try:
        logging.info(f"DATABASE: Execute query: {query}")
        con = sqlite3.connect(path_to_db)
        cursor = con.cursor()
        if data is not None:
            print('query w/h data:', query, data)
            cursor.execute(query, data)
        else:
            print('query:', query)
            cursor.execute(query)
        con.commit()
        return cursor
    
    except sqlite3.Error as e:
        logging.error(f"DATABASE: Request error: {e}")
        print("Ошибка при выполнении запроса:", e)

    finally:
        con.close()


def execute_selection_query(sql_query:str, data=None):
    '''Функция для выполнения любого sql-запроса для получения данных (возвращает значение)'''
    try:
        logging.info(f"DATABASE: Execute query: {sql_query}")
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()
        if data is not None:
            cursor.execute(sql_query, data)
        else:
            cursor.execute(sql_query)
        rows = cursor.fetchall()
        connection.close()
        return rows

    except sqlite3.Error as e:
        logging.error(f"DATABASE: Request error: {e}")
        print("Ошибка при выполнении запроса:", e)


def is_value_in_table(table_name:str, column_name:str, value):
    ''' возвращает bool, row данных'''
    '''Функция для проверки, есть ли элемент в указанном столбце таблицы'''
    sql_query = f'SELECT * FROM {table_name} WHERE {column_name} = ? LIMIT 1;'
    rows = execute_selection_query(sql_query, (value, ))
    print(rows)
    if rows == None or rows == []:
        logging.error(f'the {value} of the {column_name} does not exist in the table {table_name}')
        print('abc')
        return (False, None)
    print('efg')
    return (True, rows)


def is_user_data_here(user_id:int, system:str):
    '''возвращает bool + row данных'''
    if is_value_in_table('plan_system', 'user_id', user_id)[0] is True:
        row = is_value_in_table(system, 'user_id', user_id)[1]
        if row:
            print(True, row[0])
            return (True, row[0])
        else:
            logging.error(f'user data {user_id} does not exist in the table {system}')
            msg = 'Пока у Вас нет запланированных задач'
            return (False, msg)
    else:
        logging.error(f'the user {user_id}  does not exist in the table {system}')
        msg = 'Пока у Вас нет систем планирования'
        return (False, msg)
    

def clean_record(user_id:int, table_name:str, column_name:str, column_value):
    '''возвращает msg'''
    try:
        print('is_value_in_table:', is_value_in_table(table_name, column_name, column_value))
        if is_value_in_table(table_name, column_name, column_value):
            sql_query = f'DELETE FROM {table_name} WHERE {column_name} = "{column_value}" and user_id = {user_id};'
            execute_query(sql_query)
            print('execute_query:', execute_query(sql_query))
        else:
            msg = 'Пока у Вас нет внесённых задач'
            print(msg)
            logging.error(f'recird {user_id} does not find in the table {table_name}')
            return msg
    except sqlite3.Error as e:
        logging.error(f'Error when deleting record {user_id} : {e}')
        print("Ошибка при удалении данных:", e)


def clean_user(user_id:int, table_name:str):
    '''возвращает msg'''
    try:
        if is_value_in_table(table_name, 'user_id', user_id)[0]:
            sql_query = f'DELETE FROM {table_name} WHERE user_id = {user_id};'
            execute_query(sql_query)
            return True
        else:
            msg = 'Пока у Вас нет внесённых задач'
            print(msg)
            logging.error(f'recird {user_id} does not find in the table {table_name}')
            return msg
    except sqlite3.Error as e:
        logging.error(f'Error when deleting user data {user_id} from the {table_name}:', e)
        print("Ошибка при удалении данных:", e)


def clean_table(table_name:str):
    try:
        execute_query(f'DELETE FROM {table_name}')
        return True
    except sqlite3.Error as e:
        logging.error(f'Error when deleting data from the {table_name}:', e)
        print("Ошибка при удалении данных:", e)

#db
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
            logging.info("DATABASE: The database exists")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None


def insert_database(user_id:int, system_name:str):
    values = (user_id, system_name)
    columns = '(user_id, system)'
    sql_query = f"INSERT INTO plan_system {columns} VALUES (?, ?);"
    execute_query(sql_query, values)


def select_plan_system(user_id:int):
    '''возвращает список систем или None'''
    if is_value_in_table('plan_system', 'user_id', user_id)[0] is True:
        rows = execute_selection_query(f"SELECT system FROM plan_system WHERE user_id = ?;", (user_id, ))
        b = []
        for row in rows:
            b += row
        print(b)
        return b
    else:
        msg = 'Пока у Вас нет систем планирования'
        return msg


#возможно стоит удалить
def tasks_list(user_id: int):
    '''возвращает список кортежей, где нулевой элемент - подзадача или сообщение'''
    if is_value_in_table('gtd', 'user_id', user_id)[0] is True:
        sql_query = f'SELECT task, main_task FROM gtd WHERE user_id = {user_id};'
        row = execute_selection_query(sql_query)
        print(row)
        return row
    else:
        msg = 'Пока у Вас нет запланированных задач'
        return msg


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
            logging.info("DATABASE: The database GTD exists")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None


def insert_gtd(user_id:int, main_task:str, task:str):
    values = (user_id, main_task, task)
    columns = '(user_id, main_task, task)'
    sql_query = f"INSERT INTO gtd {columns} VALUES (?, ?, ?);"
    execute_query(sql_query, values)


def update_row_value_gtd(user_id:int, column_name:str, new_value:str):
    '''возвращает bool'''
    try:
        if is_value_in_table('gtd', 'user_id', user_id)[0] is True:
            sql_query = f'UPDATE gtd SET {column_name} = "{new_value}" WHERE user_id = {user_id};'
            execute_query(sql_query)
            return True
        else:
            msg = 'Пока у Вас нет запланированных задач'
            return (False, msg)
    except Exception as e:
        logging.error(e)
        return False


def select_gtd(user_id:int):
    '''возвращает список кортеей, где нулевой элемент - задача, а первый - подзадача к ней или сообщение'''
    if is_value_in_table('gtd', 'user_id', user_id)[0] is True:
        columns = 'main_task, task'
        rows = execute_selection_query(f"SELECT {columns} FROM gtd WHERE user_id = {user_id};")
        print(rows)
        return rows
    else:
        msg = 'Пока у Вас нет запланированных задач'
        return msg


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
                will_do TEXT);
            ''')
            logging.info("DATABASE: The database KANBAN exists")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None


def insert_kanban(user_id:int, done:str, doing:str, will_do:str):
    clean_user(user_id, 'kanban')
    values = (user_id, done, doing, will_do) 
    columns = '(user_id, done, doing, will_do)'
    sql_query = f"INSERT INTO kanban {columns} VALUES (?, ?, ?, ?);"
    execute_query(sql_query, values)


def update_row_value_kanban(user_id:int, column_name:str, new_value:str):
    '''возвращает bool'''
    try:
        if is_value_in_table('kanban', 'user_id', user_id)[0] is True:
            sql_query = f'UPDATE kanban SET {column_name} = "{new_value}" WHERE user_id = {user_id};'
            execute_query(sql_query)
            return True
        else:
            msg = 'Пока у Вас нет внесённых задач'
            return (False, msg)
    except Exception as e:
        logging.error(e)
        return False


def select_kanban(user_id:int):
    if is_value_in_table('kanban', 'user_id', user_id)[0] is True:
        columns = 'done, doing, will_do'
        row = execute_selection_query(f"SELECT {columns} FROM kanban WHERE user_id = {user_id};")
        print(row)
        return row
    else:
        msg = 'Пока у Вас нет внесённых задач'
        print(msg)
        return '', '', ''
    

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
            logging.info("DATABASE: The database MATRIX exists")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None


def insert_matrix(user_id:int, imp_urg:str, imp_nonur:str, unimp_urg:str, unimp_nonurg:str):
    '''важное срочное, важное несрочное, неважное срочное, неважное несрочное'''
    clean_user(user_id, 'matrix')
    values = (user_id, imp_urg, imp_nonur, unimp_urg, unimp_nonurg)
    columns = '(user_id, imp_urg, imp_nonur, unimp_urg, unimp_nonurg)'
    sql_query = f"INSERT INTO matrix {columns} VALUES (?, ?, ?, ?, ?);"
    execute_query(sql_query, values)


def update_row_value_matrix(user_id:int, column_name:str, new_value:str):
    '''возвращает bool'''
    try:
        if is_value_in_table('matrix', 'user_id', user_id)[0] is True:
            sql_query = f'UPDATE matrix SET {column_name} = "{new_value}" WHERE user_id = {user_id};'
            execute_query(sql_query)
            print(True)
            return True
        else:
            msg = 'Пока у Вас нет внесённых задач'
            print((False, msg))
            return (False, msg)
    except Exception as e:
        logging.error(e)
        return False


def select_matrix(user_id:int):
    if is_value_in_table('matrix', 'user_id', user_id)[0] is True:
        columns = 'imp_urg, imp_nonur, unimp_urg, unimp_nonurg'
        row = execute_selection_query(f"SELECT {columns} FROM matrix WHERE user_id = {user_id};")
        print(row)
        return row
    else:
        msg = 'Пока у Вас нет внесённых задач'
        print(msg)
        return msg


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
            logging.info("DATABASE: The database REMINDER exists")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None


def insert_reminder(user_id:int, send_time:str, text_mes:str):
    values = (user_id, send_time, text_mes)
    columns = '(user_id, send_time, text_mes)'
    sql_query = f"INSERT INTO reminder {columns} VALUES (?, ?, ?);"
    execute_query(sql_query, values)


def select_reminder(user_id:int):
    if is_value_in_table('reminder', 'user_id', user_id)[0] is True:
        columns = 'send_time, text_mes'
        row = execute_selection_query(f"SELECT {columns} FROM reminder WHERE user_id = {user_id};")
        print(row)
        return row
    else:
        msg = 'Пока у Вас нет внесённых напоминаний'
        print(msg)
        return msg


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
            now_need.append(value)
    print(now_need)
    return now_need


#speechkit & gpt
def create_database():
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                message TEXT,
                role TEXT,
                total_gpt_tokens INTEGER,
                tts_symbols INTEGER,
                stt_blocks INTEGER)
            ''')
            logging.info("DATABASE: The database MESSAGES exists")  # делаем запись в логах
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None


def add_message(user_id:int, message:str, role:str, total_gpt_tokens:int, tts_symbols:int, stt_blocks:int):
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO messages (user_id, message, role, total_gpt_tokens, tts_symbols, stt_blocks) 
                            VALUES (?, ?, ?, ?, ?, ?);''',
                           (user_id, message, role, total_gpt_tokens, tts_symbols, stt_blocks)
                           )
            conn.commit()  
            logging.info(f"DATABASE: INSERT INTO messages "
                         f"VALUES ({user_id}, {message}, {role}, {total_gpt_tokens}, {tts_symbols}, {stt_blocks})")
    except Exception as e:
        logging.error(e)
        return None


def count_users(user_id:int):
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT COUNT(DISTINCT user_id) FROM messages WHERE user_id <> ?''', (user_id,))
            count = cursor.fetchone()[0]
            return count 
    except Exception as e:
        logging.error(e)
        return None
    

def select_n_last_messages(user_id:int, n_last_messages:int):
    messages = []
    total_spent_tokens = 0  # количество потраченных токенов за всё время общения
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT message, role, total_gpt_tokens FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?''',
                           (user_id, n_last_messages))
            data = cursor.fetchall()
            if data and data[0]:
                # формируем список сообщений
                for message in reversed(data):
                    messages.append({'text': message[0], 'role': message[1]})
                    total_spent_tokens = max(total_spent_tokens, message[2])  # находим максимальное количество потраченных токенов
            return messages, total_spent_tokens
    except Exception as e:
        logging.error(e) 
        return messages, total_spent_tokens


def count_all_limits(user_id:int, limit_type:str):
    try:
        with sqlite3.connect(path_to_db) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''SELECT SUM({limit_type}) FROM messages WHERE user_id=?''', (user_id,))
            data = cursor.fetchone()
            if data and data[0]:
                logging.info(f"DATABASE: У user_id={user_id} использовано {data[0]} {limit_type}")
                return data[0] 
            else:
                return 0 
    except Exception as e:
        logging.error(e)
        return None