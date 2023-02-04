import mysql.connector
from mysql.connector import Error


def insert_tg_user(tg_id, tg_first_name, tg_last_name, username):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='aviators',
                                             user='root',
                                             password='3356')
        cursor = connection.cursor()
        mySql_insert_query = f"""INSERT INTO tg_users (tg_id, tg_first_name, tg_last_name, username)
        VALUES ({tg_id}, "{tg_first_name}", "{tg_last_name}", "{username}")
        ON DUPLICATE KEY UPDATE tg_first_name="{tg_first_name}", tg_last_name="{tg_last_name}", username="{username}" """

        cursor.execute(mySql_insert_query)
        connection.commit()
        print("Запись успешно вставлена в таблицу пользователей")

    except mysql.connector.Error as error:
        print("Не удалось выполнить вставку в таблицу MySQL {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            


def insert_varibles_into_table(tg_id, first_name, last_name, academ_group):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='aviators',
                                             user='root',
                                             password='3356')
        cursor = connection.cursor()
        mySql_insert_query = f"""INSERT INTO users (tg_id, first_name, last_name, academ_group) 
        VALUES ({tg_id}, "{first_name}", "{last_name}", "{academ_group}")
        ON DUPLICATE KEY UPDATE first_name="{first_name}", last_name="{last_name}", academ_group="{academ_group}" """

        cursor.execute(mySql_insert_query)
        connection.commit()
        return('Запись успешно вставлена в таблицу пользователей')

    except mysql.connector.Error as error:
        return("Не удалось выполнить вставку в таблицу MySQL {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            


def insert_key(tg_id, card):
    try:

        if in_table(tg_id) == True:
            return("Ключ уже зарегистрирован в системе")
        else:
            connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='root',
                                            password='3356')
            cursor = connection.cursor()
            mySql_insert_query = f"""Update users set RFID = {card} where tg_id = {tg_id}"""

            cursor.execute(mySql_insert_query)
            connection.commit()
            return("Ключ успешно записан")

    except mysql.connector.Error as error:
        print("Не удалось обновить запись в таблице: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()
            

def in_table(tg_id):
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='root',
                                            password='3356')
        cursor = connection.cursor()
        
        #Проверка перед обновлением записи
        sql_select_query = f"""SELECT EXISTS(SELECT RFID FROM users WHERE tg_id = {tg_id})"""
        cursor.execute(sql_select_query)
        # fetch result
        record = cursor.fetchall()
        print(record)
        return(record)

    except mysql.connector.Error as error:
        print("Не удалось проверить наличие в таблице: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()
            

def select():
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='root',
                                            password='3356')

        sql_select_Query = """SELECT users.tg_id, tg_users.username, users.first_name, users.last_name, users.academ_group, users.approved FROM users
                              JOIN tg_users ON tg_users.tg_id = users.tg_id
                              WHERE approved = FALSE """
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
                                        user='root',
                                        password='3356')
        cursor = connection.cursor()
        mySql_insert_query = f"""SELECT tg_id FROM tg_users WHERE username = "{username}" """
        cursor.execute(mySql_insert_query)
        id = str(cursor.fetchone())
        id = "".join(i for i in id if i.isdecimal())
        mySql_insert_query = f"""Update users set approved = {approve} where tg_id = {id}"""

        cursor.execute(mySql_insert_query)
        connection.commit()
        return("Пользователь успешно подтверждён")

    except mysql.connector.Error as error:
        return("Не удалось обновить запись в таблице: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()