import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
BASE_URL = 'https://dou.ua/calendar/city/%D0%9A%D0%B8%D0%B5%D0%B2/'


def soupit(url):
    page = requests.get(url, headers=headers).content
    soup = BeautifulSoup(page, "html.parser")
    return soup


def cleanup(string):
    new_string = re.sub(r'[\t\n]', '', string)
    return new_string


# Getting number of pages
def paggination(soup):
    pages = soup.find('div', class_="b-paging")
    a = pages.find_all('span')
    return len(a) - 2


# Function to parse and update information in base
def parse():
    soup = soupit(BASE_URL)
    pages = paggination(soup)
    result = []
    for i in range(1, pages + 1):
        soup = soupit(BASE_URL + str(i))
        block = soup.find('div', class_="col50 m-cola")
        block2 = list(block)[2:49]
        for j in block2:
            # Finding exactly tags, which contains useful information or skip i in block
            if not hasattr(j, 'text'):
                continue
            if j.find('a').parent.name == "div" and j.find('a').text != "RSS":
                # Formatting parsed date
                date = (j.find('a')).get('href')
                date = re.search(r'\d+\-\d+\-\d+', date)
                date = date.group(0)
                date = re.sub(r'-', '.', date)
                a = date[5:7]
                b = date[8:]
                date = b + "." + a
                week = datetime.date(2018, int(a), int(b)).isocalendar()[1]
            elif j.find('a').parent.name == "h2":
                title = j.find('a').parent.text
                href = j.find('a')['href']
                when_and_where = j.find('div', class_="when-and-where")
                date_and_price = when_and_where.find_all('span')
                try:
                    price = date_and_price[1].text
                except IndexError:
                    price = 'Нет данных'
                result.append((cleanup(title), cleanup(price), date, href, week))
    connection = sqlite3.connect('events.db')
    cursor = connection.cursor()
    cursor.executemany("INSERT OR REPLACE INTO calendar (title, price, date, href, week) VALUES (?, ?, ?, ?, ?);", result)
    connection.commit()
    connection.close()


if __name__ == '__main__':
    parse()
