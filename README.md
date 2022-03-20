# Система безопастности на основе визуальной идентификации на основе библиотеки Opencv с подключением MySQL


Система безопастности на основе визуальной идентификации

## Установка

Используйте установшик пакетов [pip](https://pip.pypa.io/en/stable/) чтобы скачать библиотеки.

```bash
pip install foobar
pip install 
pip face_recognition
pip pymysql
pip base64
pip googletrans
pip PIL
pip numpy
```

## CreateDB.py
```python
# подключаем базу данных
import pymysql
# из файла config.py импортируем параметры для подключениея к БД
from config import db_name, password, host, user
# библиотека для создания таблиц из excel файлов
import pandas as pd
# библиотека для работы с файлами и операционой системой
import os
# библиотека для кодирования фотографий в строчный тип
import base64

# подключаемся к БД
try:
    connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
    )
    try:
        # Создаем таблицу users
        # Name - имя пользователя строчный тип данных
        # Surname - фамилия пользователя строчный тип данных
        # Class - класс пользователя строчный тип данных
        # Photos - фотография в массиве двоичных данных
        with connection.cursor() as cursor:
            create_table_query = " CREATE TABLE users (id int AUTO_INCREMENT," \
                                 " name varchar(32)," \
                                 " surname varchar(32)," \
                                 " class varchar(32)," \
                                 " photos LONGBLOB," \
                                 " PRIMARY KEY(id));"
            cursor.execute(create_table_query)
            print("Table created")

        # открывем excel таблицу с данными пользователя вид - Имя Фамилия Класс
        df = pd.read_excel(r'users.xls', sheet_name='Лист1')

        # цикл для добавления каждого пользователя 
        for i in df.values:
            # добавляем пользователей
            with connection.cursor() as cursor:
                insert_query = "INSERT INTO users(name, surname, class) VALUES (%s, %s, %s);"
                var = (str(i[0]), str(i[1]), str(i[2]))
                cursor.execute(insert_query, var)
                connection.commit()


        # в дериктори проекта создаем папку photo, в которой храняться папки формата класса прим.(9А)
        # в папке каждого класса должный хрониться фотографии формата - Фамилия Имя.jpeg (Тагиров Роберт.jpg) в дериктоии /photo/9C/Тагиров Роберт.jpeg
        # фотографии конвектируются в бинарный код и присваиваются своим хозяйнам в БД
        with connection.cursor() as cursor:
            select_all_rows = "SELECT name, surname, id, photos, class FROM users"
            cursor.execute(select_all_rows)
            rows = cursor.fetchall()
            for row in rows:
                name, surname, id, photo, classe = row['name'], row['surname'], row['id'], row['photos'], row['class']
                if name != None and classe != None:
                    files = os.listdir('photo/'+ classe)

                    for file in files:
                        surnameFromFile, nameFromFile = (file.split(' '))
                        nameFromFile, formatFile = nameFromFile.split('.')

                        if name == nameFromFile and surname == surnameFromFile:
                            with open(f'photo/{classe}/{surnameFromFile} {nameFromFile}.jpeg', 'rb') as binary_file:
                                binary_file_data = binary_file.read()
                                base64_encoded_data = base64.b64encode(binary_file_data)
                                base64_message = base64_encoded_data.decode('utf-8')

                                base64_img = base64_message
                                base64_img_bytes = base64_img.encode('utf-8')

                            with connection.cursor() as cursor:
                                update_query = """ UPDATE users SET photos = (%s) WHERE name = (%s) and surname = (%s) """
                                var = (base64_img_bytes, name, surname)
                                cursor.execute(update_query, var)
                                connection.commit()

    # в коцне подключение закрывается 
    finally:
        connection.close()
    print('Goof')
except Exception as ex:
    print('Connection refused')
    print(ex)
```