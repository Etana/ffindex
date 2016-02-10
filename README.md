aim:
- searching fanfiction.net more easily

starting:
- have a postgresql running with the database
- update db credentials in ffindex.py
- run command in directory `python3 ffindex.py`
- server should have started on http://127.0.0.1:5503/

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
- sample db
