aim:
- searching fanfiction.net more easily

starting:
- have a postgresql running with the database
- download([here](https://drive.google.com/file/d/0B7vvgc0KN-9eaDc4T0xPRXJiUTg/view?usp=sharing)), un7zip and import sample database with `psql dbname < sample_db.sql`
- update database credentials `dbname='ff' user='ea'` in ffindex.py
- run this command in local repository `python3 ffindex.py`
- go with a browser on http://127.0.0.1:5503/

features:
- server displaying([screenshot](http://i.imgur.com/l2OWNOL.png)) a fanfiction.net index
- filtering on a tag
- sorting by chapters, words, reviews, favorites, followers

requirements:
- postgresql
- python 3
- psycopg2 (python 3 package)
- flask (python 3 package)

soon:
- fanfiction.net info scrapper
