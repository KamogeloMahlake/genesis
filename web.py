import os
import requests
import psycopg2
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime

psql = psycopg2.connect(
    host="localhost",
    database="novels",
    user="kamogelo",
    password="Shaunmah",
    port="5432",
)

cursor = psql.cursor()

while True:
    try:
        keyword = input(
            "Enter a keyword to search for novels (or type 'exit' to quit): "
        ).replace(" ", "+")
        r = requests.get(f"https://novelbin.me/search?keyword={keyword}")

        links = BeautifulSoup(r.text, "html.parser").find_all(
            "h3", class_="novel-title"
        )

        i = 0
        array = []

        for link in links:
            array.append(str(link.find("a")["href"]))
            print(f"{i}. {link.find('a').getText()}")
            i += 1

        answer = int(input("Select a novel by entering its number: "))
        ret = BeautifulSoup(requests.get(array[answer]).text, "html.parser")

        title = ret.find("h3", class_="title").getText()
        img = ret.find("img", class_="lazy")["data-src"]
        desc = ret.find("div", class_="desc-text")

        try:
            author = (
                ret.find("ul", class_="info info-meta")
                .getText()
                .split(" ")[0]
                .split("\n")[3]
            )
        except Exception:
            author = "Unknown"

        insert_novel = "INSERT INTO novel_novel (title, creator, description, date, status) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(
            insert_novel,
            (
                title,
                author,
                str(desc),
                datetime.today().strftime("%d %B %Y %H:%M"),
                False,
            ),
        )
        psql.commit()
        cursor.execute("SELECT id FROM novel_novel WHERE title = %s", (title,))
        novel_id = cursor.fetchone()[0]

        with open(f"./media/novel-images/{novel_id}.jpg", "wb") as f:
            img_data = requests.get(img).content
            f.write(img_data)

        next_chapter = ret.find(title="READ NOW", href=True)
        chapter_num = 0
        while next_chapter["href"]:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/",
                }
                page = requests.get(next_chapter["href"])
                print(f"Fetching chapter from {next_chapter['href']}")
            except requests.exceptions.MissingSchema:
                print("Invalid URL. Please try again.")
                break
            soup = BeautifulSoup(page.text, "html.parser")
            content = soup.find("div", id="chr-content")
            print(page.status_code)
            try:
                title = soup.find("span", class_="chr-text").getText()
            except TypeError:
                title = soup.find("h2").getText()

            chapter_num += 1
            insert_chapter = "INSERT INTO novel_chapter (title, num, novel, content, date) VALUES (%s, %s, %s, %s, %s) RETURNING id"
            if novel_id:
                cursor.execute(
                    insert_chapter,
                    (
                        title,
                        chapter_num,
                        novel_id,
                        str(content),
                        datetime.today().strftime("%d %B %Y %H:%M"),
                    ),
                )
                psql.commit()
            next_chapter = soup.find("a", id="next_chap")
    except Exception as e:
        print(e)
        cursor.close()
        psql.close()
