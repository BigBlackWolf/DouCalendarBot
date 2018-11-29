# DouCalendarBot

## Getting started

### About

[DouCalendarBot](http://t.me/doucalendarbot) is telegram bot, which parse events from dou.ua related with Kiev

### Stack 

- Python 3
    - Flask
    - Beautiful Soup
    - pyTelegramBotAPI
- SQLite

### Note
This project is placed on Heroku. If you want to run project you have to create **settings.py** file and write
```python
token = "putyourtokenhere"
url = "https://yourappname.herokuapp.com/"
```

And you have to create SQLite database named **events.db** with 2 tables:
```sql
CREATE TABLE calendar (
title VARCHAR(300) UNIQUE, 
price VARCHAR(50), 
date VARCHAR(30), 
href VARCHAR(120), 
week INTEGER
);

CREATE TABLE users (
id INTEGER PRIMARY KEY AUTOINCREMENT, 
chat_id INTEGER(50), 
enabled_alarm INTEGER(2), 
time VARCHAR(30)
);
```

Don't forget to install requirements
```bash
pip install -r requirements.txt
```

#### License
This project is licensed under MIT [License](https://github.com/BigBlackWolf/DouCalendarBot/blob/master/LICENSE)
