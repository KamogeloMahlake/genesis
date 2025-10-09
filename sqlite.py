from cs50 import SQL
import os
import psycopg2
from datetime import datetime

psql = psycopg2.connect(
    host="localhost",
    database="novels",
    user="kamogelo",
    password="Shaunmah",
    port="5432"
)

cursor = psql.cursor()

db = SQL("sqlite:///novels.db")

novels = db.execute('SELECT novel_id, name FROM novels')
insert = "INSERT INTO novel_novel (title, status, date, novel_image) VALUES (%s, %s, %s, %s) RETURNING id"

for novel in novels:
    try:
        cursor.execute(insert, (novel['name'], False, datetime.now(), 'placeholder.png'))
        psql.commit()
    except psycopg2.IntegrityError:
        psql.rollback()
        cursor.execute("SELECT id FROM novel_novel WHERE title = %s", (novel['name'],))

    novel_id = cursor.fetchone()[0]
    chapters = db.execute(f"SELECT * FROM chapters WHERE novel_id = {novel["novel_id"]}")

    for chapter in chapters:
        cursor.execute("INSERT INTO novel_chapter (novel_id,  title, content, num, views, date) VALUES (%s, %s, %s, %s, %s, %s)", 
                       (novel_id, chapter["title"], chapter["content"], chapter["chapter_num"], 0, datetime.now()))
        psql.commit()

'''   
for database in os.listdir("novels_databases"):
    db = SQL(f"sqlite:///novels_databases/{database}")
    insert = "INSERT INTO novel_novel (title, status, date) VALUES (%s, %s, %s) RETURNING id"
    title = database.replace(".db", "").replace("_", " ")
    try:
        cursor.execute(insert, (title, False, datetime.now()))
        psql.commit()
    except psycopg2.IntegrityError:
        psql.rollback()
        cursor.execute("SELECT id FROM novel_novel WHERE title = %s", (title,))
    novel_id = cursor.fetchone()[0]
    print(title)
    chapters = db.execute("SELECT * FROM chapter")

    for chapter in chapters:
        cursor.execute("INSERT INTO novel_chapter (novel_id,  title, content, num, views, date) VALUES (%s, %s, %s, %s, %s, %s)", 
                       (novel_id, chapter["title"], chapter["content"], chapter["chapter_num"], 0, datetime.now()))
        psql.commit()
'''
cursor.close()
psql.close()