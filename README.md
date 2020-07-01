# flask-app

### create database
python initdb.py

### how to run
python api.py

### sql to create a new field
ALTER TABLE kifu ADD column is_analyse boolean NOT NULL default 0;
ALTER TABLE kifu ADD column analyse_data char(2500);