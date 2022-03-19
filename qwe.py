import pymysql
from config import db_name, password, host, user
import pandas as pd
import os
import base64
df = pd.read_excel(r'd.xls', sheet_name='Лист1')
numberOfStudents = len(df['name'].tolist())


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

        # with connection.cursor() as cursor:
        #     create_table_query = " CREATE TABLE users (id int AUTO_INCREMENT," \
        #                          " name varchar(32)," \
        #                          " surname varchar(32)," \
        #                          " class varchar(32)," \
        #                          " photos LONGBLOB," \
        #                          " PRIMARY KEY(id));"
        #     cursor.execute(create_table_query)
        #     print("Table created")


        # with connection.cursor() as cursor:
        #     sql_select_Query = "SELECT * FROM users"
        #     cursor = connection.cursor()
        #     cursor.execute(sql_select_Query)
        #     # get all records
        #     records = cursor.fetchall()
        #     print("Total number of rows in table: ", cursor.rowcount)
        #
        #     print("\nPrinting each row")
        #     for row in records:
        #         print("Id = ", row[0], )
        #         print("Name = ", row[1])
        #         print("Surname  = ", row[2])
        #         print("class  = ", row[3], "\n")


        # image = open('robert.jpg', 'rb')
        # image_read = image.read()
        # image_64_encode = base64.encodestring(image_read)
        # image_64_decode = base64.decodestring(image_64_encode)
        # image_result = open('robert_new.jpg', 'wb')  # create a writable image and write the decoding result
        # image_result.write(image_64_decode)




        # for i in df.values:
        #
        #     with connection.cursor() as cursor:
        #         insert_query = "INSERT INTO users(name, surname, class) VALUES (%s, %s, %s);"
        #         var = (str(i[0]), str(i[1]), str(i[2]))
        #         cursor.execute(insert_query, var)
        #         connection.commit()


        # with connection.cursor() as cursor:
        #     insert_query = "DELETE FROM users;"
        #     cursor.execute(insert_query)
        #     connection.commit()







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
                                print('*' * 100)
                                base64_img_bytes = base64_img.encode('utf-8')

                            with connection.cursor() as cursor:
                                update_query = """ UPDATE users SET photos = (%s) WHERE name = (%s) and surname = (%s) """
                                var = (base64_img_bytes, name, surname)
                                cursor.execute(update_query, var)
                                connection.commit()
                            # im = Image.open(f'photo/{classe}/{file}')
                            # im.show()

                            #print(nameFromFile, surnameFromFile)

    finally:
        connection.close()
    print('Goof')
except Exception as ex:
    print('Connection refused')
    print(ex)