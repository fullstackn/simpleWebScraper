Script read articles (title, text, some other metadata) from https://pikabu.ru/ , filtered by tags.

Requires Python3. 

For installing dependencies run:
```
pip install -r requirements.txt
```

Example of usage from command line:
```
python pikabu.py --output_filename my_articles_filename.csv --tags Politics,Mars
```