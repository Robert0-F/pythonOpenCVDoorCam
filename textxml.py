import pandas as pd   # pip install pandas
import base64
import photo
import os
import ntpath
from PIL import Image
classe = '9C'

# files = os.listdir(f'photo/{classe}')
#
# for file in files:
#     nameFromFile, surnameFromFile = (file.split(' '))
#     surnameFromFile, formatFile = surnameFromFile.split('.')
#     #im.show()
#     print(nameFromFile, surnameFromFile)
#
#
# print('*' * 25)
# im = Image.open(f'photo/9C/{file}')
#
# df = pd.read_excel(r'd.xls', sheet_name='Лист1')
# numberOfStudents = len(df['name'].tolist())
#
# for i in df.values:
#     name = i[0]
#     surname = i[1]
#     classe = i[2]
#
#     print(name, surname, classe)


with open('robert.jpg', 'rb') as binary_file:
    binary_file_data = binary_file.read()
    base64_encoded_data = base64.b64encode(binary_file_data)
    base64_message = base64_encoded_data.decode('utf-8')
    base64_img = base64_message
    base64_img_bytes = base64_img.encode('utf-8')

with open('decoded_image.png', 'wb') as file_to_save:
    decoded_image_data = base64.decodebytes(base64_img_bytes)
    file_to_save.write(decoded_image_data)