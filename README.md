# Система безопастности на основе визуальной идентификации на основе библиотеки Opencv с подключением MySQL
![](https://user-images.githubusercontent.com/72812832/159159893-1255f09b-e399-4683-a70d-27b1d4b96963.png)

## Установка

Используйте установшик пакетов [pip](https://pip.pypa.io/en/stable/) чтобы скачать библиотеки.

```bash
pip install face_recognition
pip install pymysql
pip install base64
pip install googletrans
pip install PIL
pip install numpy
pip install cv2
pip install flask
```
Туториал по установке [MySql](https://www.youtube.com/watch?v=ZfoIDR1w_VA).

![](https://user-images.githubusercontent.com/72812832/159158291-93b7e7aa-cf33-47b2-9cb7-e447d3c25cd3.png)

## config.py
```python

host = '' # адресс БД
user = '' # имя пользователя
password = '' # пароль пользователя
db_name = '' # названия базы данных

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
# библиотека для кодирования фотографий в бинарный код
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


        # в директор проекта создаем папку photo, в которой храняться папки формата класса прим.(9А)
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
# Flask 

Лучший фреймворк для Python!

![](https://user-images.githubusercontent.com/72812832/159159316-1c3c99b3-5920-47ca-8e45-9ca5e50d4f67.png)

## Cамой интересная часть проекта Распознование лиц
![](https://user-images.githubusercontent.com/72812832/159158542-c43abad3-460a-45b5-b16a-5b7b8a60de8f.png)
## main.py
```python
# библиотека для распознования лиц
import face_recognition
# библиотека для обрабоки изображений
import cv2
# библиотека для фрэймворка flask 
from flask import Flask, render_template, Response
# библиотека для многомерных массивов
import numpy as np
# библиотека для БД
import pymysql
# из файла config.py импортируем параметры для подключениея к БД
from config import db_name, password, host, user
# библиотека для работы с ОС
import os
# библиотека для кодирования фотографий в бинарный код
import base64
# библиотека от гуууугл для перевода 
from googletrans import Translator
# библиотека для работы с изображениями 
from PIL import ImageFile

# Объявляем переводчик)
translator = Translator()
# создаем веб-приложение на основе flask
app = Flask(__name__)
# считываем видео с встроеной видеокамеры
video_capture = cv2.VideoCapture(0)
ImageFile.LOAD_TRUNCATED_IMAGES = True


try:
    # Подключаемся к БД
    connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        # Берем данные о всех пользователях. Фотографии переводим из бинарного кода в простое изображение
        known_face_encodings = []
        known_face_names = []
        with connection.cursor() as cursor:
            select_all_rows = "SELECT name, surname, photos, class FROM users"
            cursor.execute(select_all_rows)
            rows = cursor.fetchall()
            for row in rows:
                name, surname, photo, classe = row['name'], row['surname'], row['photos'], row['class']
                if photo != None:
                    print(name)
                    with open('decoded_image.jpg', 'wb') as file_to_save:
                        decoded_image_data = base64.decodebytes(photo)
                        file_to_save.write(decoded_image_data)
                    print('*' * 50)
                    imagea = face_recognition.load_image_file('decoded_image.jpg')
                    face_encoding = face_recognition.face_encodings(imagea)[0]
                    known_face_encodings.append(face_encoding)
                    os.remove('decoded_image.jpg')
                    
                    
                    # добавляем каждого пользователя в массив, для полседующей обработки
                    known_face_names.append(f'{translator.translate(name).text} {translator.translate(surname).text}')
            print(1)
        print(known_face_names)

    finally:
        connection.close()
    print('Goof')
except Exception as ex:
    print('Connection refused')
    print(ex)



face_locations = []
face_encodings = []
face_names = []
process_this_frame = True


def gen_frames():
    while True:
        # считываем изображение с видео камеры
        success, frame = video_capture.read()
        if not success:
            break
        else:
            # изменяем размер видео для более быстрой обратки 
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)


            rgb_small_frame = small_frame[:, :, ::-1]
            # поиск лица и его расположения. Перевод в несколько мерные массивы 
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
            face_names = []
            for face_encoding in face_encodings:
                # поисе лица из массива загруженых лиц
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    face_names.append(name)

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                global Dname
                Dname = name

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():

    return render_template('index.html', namess = Dname)


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

Dname = ''

if __name__ == '__main__':
    # запуск приложения
    app.run()

```

# Итоги
![](https://user-images.githubusercontent.com/72812832/159159592-bac236bb-a66a-47a1-abe2-e7d924f49ecd.png)