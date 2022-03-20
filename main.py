import face_recognition
import cv2
from flask import Flask, render_template, Response
import numpy as np
import pymysql
from config import db_name, password, host, user
import os
import base64
from googletrans import Translator
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

translator = Translator()
app = Flask(__name__)
video_capture = cv2.VideoCapture(0)


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
                    known_face_names.append(f'{translator.translate(name).text} {translator.translate(surname).text}')
            print(1)
        print(known_face_names)

    finally:
        connection.close()
    print('Goof')
except Exception as ex:
    print('Connection refused')
    print(ex)


# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True


def gen_frames():
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        else:

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)


            rgb_small_frame = small_frame[:, :, ::-1]

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:

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

    return render_template('index.html', namess=Dname)


@app.route('/video_feed')
def video_feed():
    print(Dname)
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

Dname = ''
if __name__ == '__main__':
    app.run()
