import requests
import os
import psycopg2
from bs4 import BeautifulSoup

psql = psycopg2.connect(
    host="localhost",
    database="novels",
    user="kamogelo",
    password="Shaunmah",
    port="5432"
)

cursor = psql.cursor()

cursor.execute("SELECT title, id FROM novel_novel")
novels = cursor.fetchall()

for novel in novels:
    try: 
        title = novel[0].replace(" ", "-").replace("'", "").replace("!", "").replace("(", "").replace(")", "").replace(":", "-").replace(",", "").lower()
        url = f"https://novelbin.me/novel-book/{title}"
        soup = BeautifulSoup(requests.get(url).text, "html.parser")

        desc = soup.find("div", class_="desc-text")
        print(str(desc))
        cursor.execute("UPDATE novel_novel SET description = %s WHERE id = %s", (str(desc), novel[1]))
        psql.commit()    
    
    except Exception as e:
        print(e)
        continue
cursor.close()
psql.close()