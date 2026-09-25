#DataPipeline Module
This module implements an end-to-end data pipeline for scraping, cleaning, transforming, and storing book data in a SQLite database.
The Pipeline performs the following steps:
    Scrapes book data from the source website.
    Cleans and validates the scraped data.
    Handles missing or invalid values.
    Stores the cleaned data in a SQLite database.
    Implement JOIN between the tables
    Executes SQL queries on the stored data.
    On a join query get pd.read_sql and pd.merge 

Requirements

    Python 3.x is required.
    Install the required dependencies using:
    pip install -r requirements.txt
    The main libraries used are:
        pandas
        requests
    beautifulsoup4
SQLite is provided through Python's built-in sqlite3 module.
