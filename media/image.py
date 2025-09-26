import os
import requests
import psycopg2

psql = psycopg2.connect(
    host="localhost",
    database="novels",
    user="kamogelo",
    password="Shaunmah",
    port="5432"
)


cur = psql.cursor()
for file in os.listdir("novel-images"):
    cur.execute("UPDATE novel_novel SET novel_image = %s WHERE id = %s", (f"novel-images/{file}", int(file.split(".")[0])))
    psql.commit()

cur.close()
psql.close()

