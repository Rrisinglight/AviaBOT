import mysql.connector
from mysql.connector import Error

def connect():
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='root',
                                            password='3356')
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print('Connected to MySQL Server version ', db_Info)
            cursor = connection.cursor()
            cursor.execute('select database();')
            record = cursor.fetchone()
            print('You re connected to database: ', record)

    except Error as e:
        print('Error while connecting to MySQL', e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print('Соединение с MySQL закрыто')

def insert_varibles_into_table(tg_id, first_name, last_name, academ_group):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='aviators',
                                             user='root',
                                             password='3356')
        cursor = connection.cursor()
        mySql_insert_query = """INSERT INTO users (tg_id, first_name, last_name, academ_group) 
                                VALUES (%s, %s, %s, %s) """

        record = (tg_id, first_name, last_name, academ_group)
        cursor.execute(mySql_insert_query, record)
        connection.commit()
        return("Запись успешно вставлена в таблицу пользователей")

    except mysql.connector.Error as error:
        return("Не удалось выполнить вставку в таблицу MySQL {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Соединение с MySQL закрыто")

def insert_key(tg_id, card):

    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='root',
                                            password='3356')
        cursor = connection.cursor()

        print("Перед обновлением записи ")
        sql_select_query = f"""select * from users where tg_id = {tg_id}"""
        cursor.execute(sql_select_query)
        record = cursor.fetchone()
        print(record)

        # Update single record now
        sql_update_query = f"""Update users set RFID = {card} where tg_id = {tg_id}"""
        cursor.execute(sql_update_query)
        connection.commit()
        print("Запись успешно обновлена ")

        print("После обновления записи ")
        cursor.execute(sql_select_query)
        record = cursor.fetchone()
        print(record)

    except mysql.connector.Error as error:
        print("Не удалось обновить запись в таблице: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()
            print("Соединение с MySQL закрыто")


def select(table):
    try:
        connection = mysql.connector.connect(host='localhost',
                                            database='aviators',
                                            user='root',
                                            password='3356')

        sql_select_Query = "select * from " + table
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        # get all records
        records = cursor.fetchall()
        print("Total number of rows in table: ", cursor.rowcount)
        
        print("\nPrinting each row")
        for row in records:
            print("tg_id = ", row[0], )
            print("first_name = ", row[1])
            print("last_name = ", row[2])
            print("group = ", row[3], "\n")

    except mysql.connector.Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("Соединение с MySQL закрыто")

select('users')