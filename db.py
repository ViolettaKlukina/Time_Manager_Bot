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