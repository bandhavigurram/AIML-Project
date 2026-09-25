# Data Pipeline – Books to Scrape

## Overview

This module implements an end-to-end data pipeline using Python, Pandas, Requests, BeautifulSoup, and SQLite.

The pipeline:

1. Retrieves book categories from Books to Scrape.
2. Randomly selects 5 categories using a fixed random seed.
3. Scrapes book title, price, rating, availability, and category.
4. Cleans and converts the scraped data.
5. Handles invalid numeric prices using coercion and median imputation.
6. Converts star ratings from text to integers.
7. Converts availability into a Boolean `in_stock` field.
8. Converts GBP price to INR using a fixed conversion rate.
9. Creates two related SQLite tables: `categories` and `books`.
10. Loads the cleaned data into SQLite.
11. Executes SQL queries demonstrating filtering, sorting, limiting, distinct values, `BETWEEN`, `IN`, and `JOIN`.
12. Reads SQL results back into Pandas DataFrames.
13. Reproduces the SQL JOIN using `pd.merge()` and compares the result.

## Project Structure

```text
data_pipeline/
│
├── main.py
├── database.db
├── README.md
└── requirements.txt
```

## Technologies Used

- Python 3.x
- Pandas
- Requests
- BeautifulSoup4
- SQLite
- SQL
- Git/GitHub

## Python Dependencies

The external Python packages required by this project are:

- `pandas`
- `requests`
- `beautifulsoup4`

The following modules are part of Python's standard library and do not need to be installed separately:

- `random`
- `sqlite3`

## Installation

Clone the repository and navigate to the project directory.

Create a virtual environment if required:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Pipeline

Run the Python script:

```bash
python main.py
```

If the script is inside the `data_pipeline` package and the project is run from the repository root:

```bash
python -m data_pipeline.main
```

The script creates/updates:

```text
database.db
```

## Data Source

The pipeline uses:

```text
http://books.toscrape.com/
```

The website is used as the source for the book category and book-level information.

## Scraping Process

The pipeline first retrieves the main website page and identifies the category links from the `side_categories` section.

Only links containing:

```text
/category/books/
```

are treated as book categories.

A fixed random seed is used:

```python
random.seed(32)
random_categ = random.sample(categ_name, k=5)
```

This selects exactly five categories while keeping the selection reproducible.

For each selected category, the scraper extracts:

- `title`
- `price (as listed, in GBP)`
- `star_rating`
- `availability`
- `category`

## Data Cleaning

### Price Cleaning

The scraped price is initially stored as text.

The currency symbol is removed and the value is converted to numeric:

```python
df["price (as listed, in GBP)"] = (
    pd.to_numeric(
        df["price (as listed, in GBP)"]
        .str.replace("Â£", "", regex=False)
        .str.strip(),
        errors="coerce"
    )
)
```

`errors="coerce"` converts unexpected or invalid values to `NaN` instead of causing the pipeline to fail.

Missing/invalid numeric values are then replaced using the median:

```python
df["price (as listed, in GBP)"] = (
    df["price (as listed, in GBP)"]
    .fillna(df["price (as listed, in GBP)"].median())
)
```

### Star Rating Conversion

The textual ratings are converted to integers:

```python
{
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}
```

This produces a numeric `star_rating` field suitable for SQL sorting and filtering.

### Availability Conversion

The availability text is converted to a Boolean value:

```python
df["in_stock"] = (
    df["availability"].str.strip().str.lower() == "in stock"
)
```

The resulting field is:

- `True` – book is in stock
- `False` – book is not in stock

### GBP to INR Conversion

The project uses the specified fixed conversion rate:

```text
1 GBP = 105.50 INR
```

The INR price is calculated as:

```python
df["price_inr"] = df["price (as listed, in GBP)"] * 105.50
```

This is a fixed project conversion rate and is not a live exchange rate.

## Database Design

SQLite is used for database storage.

The database contains two tables:

```text
categories
    |
    | category_id
    |
    ↓
books
```

### Categories Table

```sql
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE
);
```

Columns:

| Column | Type | Description |
|---|---|---|
| `category_id` | INTEGER | Primary key |
| `category_name` | TEXT | Unique category name |

### Books Table

```sql
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    price_gbp REAL,
    price_inr REAL,
    star_rating INTEGER,
    in_stock BOOLEAN,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
```

Columns:

| Column | Type | Description |
|---|---|---|
| `book_id` | INTEGER | Primary key |
| `title` | TEXT | Book title |
| `price_gbp` | REAL | Book price in GBP |
| `price_inr` | REAL | Converted price in INR |
| `star_rating` | INTEGER | Rating from 1 to 5 |
| `in_stock` | BOOLEAN | Availability status |
| `category_id` | INTEGER | Foreign key referencing `categories` |

## Relationship Between Tables

The relationship is:

```text
categories.category_id
          │
          │  Primary Key
          │
          ▼
books.category_id
          │
          └── Foreign Key
```

Each book is associated with its category through `category_id`.

The category name is stored once in the `categories` table rather than repeatedly storing the complete category information for every book.

## SQL Queries

The pipeline executes six SQL queries.

### Query 1 – WHERE

Retrieves books where the INR price is greater than 1000.

```sql
SELECT title, price_inr
FROM books
WHERE price_inr > 1000;
```

### Query 2 – DISTINCT

Retrieves unique category names.

```sql
SELECT DISTINCT category_name
FROM categories;
```

### Query 3 – ORDER BY

Sorts books by star rating in descending order.

```sql
SELECT title, price_inr, star_rating
FROM books
ORDER BY star_rating DESC;
```

### Query 4 – JOIN and LIMIT

Joins `books` and `categories`, sorts by INR price, and returns the five lowest-priced books.

```sql
SELECT
    books.book_id,
    books.title,
    categories.category_id,
    categories.category_name,
    books.price_inr,
    books.star_rating
FROM books
JOIN categories
    ON categories.category_id = books.category_id
ORDER BY price_inr ASC
LIMIT 5;
```

### Query 5 – BETWEEN

Retrieves books whose INR price is between 500 and 1000.

```sql
SELECT
    title AS book_name,
    price_inr,
    star_rating
FROM books
WHERE price_inr BETWEEN 500 AND 1000;
```

### Query 6 – IN and WHERE

Retrieves books with a 4- or 5-star rating and an INR price below 500.

```sql
SELECT title, price_inr, star_rating
FROM books
WHERE star_rating IN (4,5)
  AND price_inr < 500;
```

## Reading SQL Results Using Pandas

The project reads SQL query results back into Pandas DataFrames using `pd.read_sql()`.

For example:

```python
df_query_1 = pd.read_sql(
    queries["query_1"],
    sqlite3.connect("database.db")
)

df_query_3 = pd.read_sql(
    queries["query_3"],
    sqlite3.connect("database.db")
)
```

The category and book tables are also loaded into DataFrames:

```python
categories_df = pd.read_sql(
    "SELECT * FROM categories",
    conn
)

books_df = pd.read_sql(
    "SELECT * FROM books",
    conn
)
```

## Reproducing the SQL JOIN Using Pandas

The SQL JOIN result is reproduced using `pd.merge()` without SQL:

```python
merged_df = pd.merge(
    books_df,
    categories_df,
    on="category_id",
    how="left"
)
```

The result is then sorted and limited to five records:

```python
sort_book_df = (
    merged_df
    .sort_values("price_inr", ascending=True)
    .head(5)
    .reset_index()
)
```

The required columns are selected:

```python
sort_book_df = sort_book_df[
    [
        "book_id",
        "title",
        "category_id",
        "category_name",
        "price_inr",
        "star_rating"
    ]
]
```

The result is compared with the SQL JOIN result:

```python
print(
    f"Sorted df without using SQL:\n{sort_book_df}"
    f"\nSorted df using SQL:\n{df_query_4}"
)
```

This demonstrates that the relationship can be reproduced using both SQL JOIN and Pandas `merge()`.

## Error Handling and Data Quality

The pipeline handles invalid numeric values using:

```python
pd.to_numeric(..., errors="coerce")
```

This prevents unexpected text in the price field from crashing the pipeline.

The resulting missing numeric values are handled using median imputation.

The category table uses:

```sql
category_name TEXT UNIQUE
```

and category insertion uses:

```sql
INSERT OR IGNORE
```

to prevent duplicate category names.

## Reproducibility

The random category selection is reproducible because the pipeline uses:

```python
random.seed(32)
```

The same seed produces the same five-category selection when the source category list remains unchanged.

## Database Recreation

The database is created automatically by the Python script.

The following tables are created if they do not already exist:

```text
categories
books
```

Running the pipeline creates the SQLite database:

```text
database.db
```

## Expected Output

The script prints the Pandas DataFrame generated from the in-memory merge and the SQL JOIN result:

```text
Sorted df without using SQL:
...

Sorted df using SQL:
...
```

The two results are intended to represent the same sorted five-record result.

## Design Decisions

### Pandas

Pandas is used for:

- DataFrame creation
- Data cleaning
- Type conversion
- Missing-value handling
- SQL result analysis
- DataFrame merging

### Requests

Requests is used to retrieve HTML content from the source website.

### BeautifulSoup

BeautifulSoup is used to parse the HTML and extract category and book information.

### SQLite

SQLite is used because it provides a lightweight relational database without requiring a separate database server.

### Relational Database Design

The data is separated into `categories` and `books` tables and connected through a foreign key.

### Median Imputation

Median imputation is used for invalid/missing numeric price values after conversion.

### Fixed Exchange Rate

A fixed rate of `1 GBP = 105.50 INR` is used as specified for this project.