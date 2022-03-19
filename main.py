import time
import io
import face_recognition
import cv2
import numpy as np
import cv2
from flask import Flask, request, make_response, render_template, Response, render_template_string
import base64
import numpy as np
import urllib
import pymysql
from config import db_name, password, host, user
import pandas as pd
import os
import base64
from googletrans import Translator, constants
from io import BytesIO
from PIL import Image, ImageFile

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
                if photo!=None:
                    print(name)

                    with open('decoded_image.jpg', 'wb') as file_to_save:
                        decoded_image_data = base64.decodebytes(photo)
                        file_to_save.write(decoded_image_data)

                        print(name, surname)
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
        success, frame = video_capture.read()  # read the camera frame
        if not success:
            break
        else:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
                # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    face_names.append(name)

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                    # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                    # Draw a label with a name below the face
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
    print(Dname)
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

Dname = ''
if __name__ == '__main__':
    app.run()
