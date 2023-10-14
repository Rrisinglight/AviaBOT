#!/usr/bin/python3
import mysql.connector
from mysql.connector import Error

def insert_tg_user(tg_id, chat_id, tg_first_name, tg_last_name, username):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='aviators',
                                             user='user1',
                                             password='829')
        cursor = connection.cursor()
        mySql_insert_query = f"""INSERT INTO tg_users (tg_id, chat_id, tg_first_name, tg_last_name, username)
        VALUES ({tg_id}, {chat_id}, "{tg_first_name}", "{tg_last_name}", "{username}")
        ON DUPLICATE KEY UPDATE tg_first_name="{tg_first_name}", tg_last_name="{tg_last_name}", username="{username}" """

        cursor.execute(mySql_insert_query)

        mySql_insert_query = f"""INSERT IGNORE INTO users (tg_id) VALUES ({tg_id})"""

        cursor.execute(mySql_insert_query)
        connection.commit()

    except mysql.connector.Error as error:
        print("Не удалось выполнить вставку в таблицу MySQL {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_key(tg_id, card):
    try:

        if in_table(card) == True:
            return("Ключ уже зарегистрирован в системе")
        else:
            connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='user1',
                                            password='829')
            cursor = connection.cursor()
            mySql_insert_query = f"""UPDATE users SET RFID = '{card}' where tg_id = {tg_id}"""

            cursor.execute(mySql_insert_query)
            connection.commit()
            return("Ключ успешно записан")

    except mysql.connector.Error as error:
        print("Не удалось обновить запись в таблице: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()

def insert_name(tg_id, first_name):
    try:
        connection = mysql.connector.connect(host='localhost',
                                        database='aviators',
                                        user='user1',
                                        password='829')
        cursor = connection.cursor()
        mySql_insert_query = f"""Update users set first_name="{first_name}" where tg_id = {tg_id}"""

        cursor.execute(mySql_insert_query)
        connection.commit()
        return("Запись успешно вставлена в таблицу пользователей")
    
    except mysql.connector.Error as error:
        print("Не удалось обновить запись в таблице: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()
            
def insert_last_name(tg_id, last_name):
    try:
        connection = mysql.connector.connect(host='localhost',
                                        database='aviators',
                                        user='user1',
                                        password='829')
        cursor = connection.cursor()
        mySql_insert_query = f"""UPDATE users SET last_name = '{last_name}' where tg_id = {tg_id};"""
        cursor.execute(mySql_insert_query)
        connection.commit()
        return("Запись успешно вставлена в таблицу пользователей")
    
    except mysql.connector.Error as error:
        print("Не удалось обновить запись в таблице: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()

def insert_group(tg_id, group):
    try:
        connection = mysql.connector.connect(host='localhost',
                                        database='aviators',
                                        user='user1',
                                        password='829')
        cursor = connection.cursor()

        mySql_insert_query = f"""Update users set academ_group="{group}" where tg_id = {tg_id}"""
        cursor.execute(mySql_insert_query)

        sql_select_query = f"""SELECT first_name FROM users WHERE tg_id = {tg_id}"""
        cursor.execute(sql_select_query)

        record = cursor.fetchone()
        connection.commit()

        return(record[0])
    
    except mysql.connector.Error as error:
        print("Не удалось обновить запись в таблице: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()

def insert_stud_type(tg_id, stud_type):
    try:
        connection = mysql.connector.connect(host='localhost',
                                        database='aviators',
                                        user='user1',
                                        password='829')
        cursor = connection.cursor()

        mySql_insert_query = f"""Update users set student_type="{stud_type}" where tg_id = {tg_id}"""
        cursor.execute(mySql_insert_query)

        connection.commit()
    
    except mysql.connector.Error as error:
        print("Не удалось обновить запись в таблице: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()

def in_table(RFID):
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='user1',
                                            password='829')
        cursor = connection.cursor()
        #Проверка перед обновлением записи
        sql_select_query = f"""SELECT EXISTS(SELECT RFID FROM users WHERE RFID = '{RFID}')"""
        cursor.execute(sql_select_query)
        # fetch result
        record = str(cursor.fetchall())
        connection.commit()

        return(bool(int(record[2])))

    except mysql.connector.Error as error:
        print("Не удалось проверить наличие в таблице: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()

def ddos_check(tg_id):
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='user1',
                                            password='829')
        cursor = connection.cursor()

        #Проверка перед обновлением записи
        sql_select_query = f"""SELECT * FROM door_log WHERE door_log.create_at > DATE_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR) AND door_log.door_status = 'Обновил данные' AND door_log.user_id = {tg_id}"""
        
        cursor.execute(sql_select_query)
        # fetch result
        record = cursor.fetchall()
        connection.commit()

        return(len(record))

    except mysql.connector.Error as error:
        print("Не удалось проверить наличие в таблице: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()

def check_id(RFID):
    try:
        connection = mysql.connector.connect(host='localhost',
                                        database='aviators',
                                        user='user1',
                                        password='829')
        cursor = connection.cursor()

        sql_select_query = f"""SELECT tg_id FROM users WHERE RFID = '{RFID}'"""
        cursor.execute(sql_select_query)
        tg_id = cursor.fetchone()
        sql_select_query = f"""SELECT username FROM tg_users WHERE tg_id = {tg_id[0]}"""
        cursor.execute(sql_select_query)
        username = cursor.fetchone()
        connection.commit()
        result = [tg_id[0], username[0]]
        return(result)
    
    except mysql.connector.Error as error:
        print("Не удалось проверить запись в таблице: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()

def insert_info(tg_id, username, door_status):
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='user1',
                                            password='829')
        cursor = connection.cursor()

        sql_select_query = f"""INSERT IGNORE INTO door_log (user_id, username, door_status)
        VALUES ({tg_id}, "{username}", "{door_status}");"""
        cursor.execute(sql_select_query)

        connection.commit()

    except mysql.connector.Error as error:
        print("Не удалось добавить запись в таблицу: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()

def insert_small_info(door_status):
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='user1',
                                            password='829')
        cursor = connection.cursor()

        sql_select_query = f"""INSERT IGNORE INTO door_log (door_status)
        VALUES ("{door_status}");"""
        cursor.execute(sql_select_query)

        connection.commit()

    except mysql.connector.Error as error:
        print("Не удалось добавить данные в таблицу: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()

def if_approved(RFID):
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='user1',
                                            password='829')
        cursor = connection.cursor()
        if in_table(RFID) == True:
            
            sql_select_query = f"""SELECT tg_id FROM users WHERE RFID = '{RFID}'"""
            cursor.execute(sql_select_query)
            id = str(cursor.fetchone())
            id = "".join(i for i in id if i.isdecimal())
            
            sql_select_query = f"""SELECT approved FROM tg_users WHERE tg_id = '{id}'"""
            cursor.execute(sql_select_query)
            record = str(cursor.fetchall())
            if bool(int(record[2])):
                return(True)
            else:
                return(False)
        else:
            return(False)

    except mysql.connector.Error as error:
        print("Не удалось проверить наличие в таблице: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()

def select(status):
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='user1',
                                            password='829')

        sql_select_Query = f"""SELECT users.tg_id, tg_users.username, users.first_name, users.last_name, users.academ_group, tg_users.approved FROM users
                              JOIN tg_users ON tg_users.tg_id = users.tg_id
                              WHERE approved = {status} """
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = []
        records.append(cursor.fetchall())
        records.append(cursor.rowcount)

        return(records)

    except mysql.connector.Error as e:
        print("Ошибка при чтении данных из таблицы MySQL", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()


def approve(username, approve):
    try:
        connection = mysql.connector.connect(host='localhost',
                                        database='aviators',
                                        user='user1',
                                        password='829')
        cursor = connection.cursor()
        mySql_insert_query = f"""SELECT tg_id FROM tg_users WHERE username = "{username}" """
        cursor.execute(mySql_insert_query)
        id = str(cursor.fetchone())
        id = "".join(i for i in id if i.isdecimal())
        mySql_insert_query = f"""Update tg_users set approved = {approve} where tg_id = {id}"""

        cursor.execute(mySql_insert_query)
        connection.commit()
        return(f"Статус пользователя {username} изменён на {bool(approve)}")

    except mysql.connector.Error as error:
        return("Не удалось обновить запись в таблице: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()

def select_message():
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='user1',
                                            password='829')

        sql_select_Query = """SELECT message FROM text ORDER BY id DESC LIMIT 1"""
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        record = str(cursor.fetchone())
        return(record[2:-3])

    except mysql.connector.Error as e:
        print("Ошибка при чтении данных из таблицы MySQL", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()

def insert_message(message):
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='user1',
                                            password='829')
        cursor = connection.cursor()

        sql_select_query = f"""INSERT INTO text (message)
        VALUES ("{message}");"""
        cursor.execute(sql_select_query)

        connection.commit()

    except mysql.connector.Error as error:
        print("Не удалось добавить данные в таблицу: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()
