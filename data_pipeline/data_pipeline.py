import pandas as pd
import requests
import random
from bs4 import BeautifulSoup
import sqlite3

def get_book_details(categories):
  book_details = []
  for category in categories:
    res = requests.get(category["URL"])
    Category = category["Category"]
    soup = BeautifulSoup(res.text, 'html.parser')
    articles = soup.find_all('article', class_ = 'product_pod')
    
    for book in articles:
        book_name = book.find('h3').find('a').get('title')
        details = book.find('div', class_='product_price')
        prod_price = details.find('p',class_='price_color').text.strip() 
        pro_rating = book.find('p',class_ = 'star-rating').get('class')[1].strip()
        availability = details.find('p', class_ = 'availability').text.strip()
        book_data = {
        'title': book_name,
        'price (as listed, in GBP)': prod_price,
        'star_rating': pro_rating,
        'availability': availability,
        'category': Category
        }
        book_details.append(book_data)
  return book_details

def create_tables(df):
    #create a connection to the SQLite database
    conn = sqlite3.connect('database.db')
    #create a cursor object to execute SQL commands
    cursor = conn.cursor()
    #create a table to store the category details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE
        )
    ''')
    #create a table to store the book details
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price_gbp REAL,
            price_inr REAL,
            star_rating INTEGER,
            in_stock BOOLEAN,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )
    ''')
    #insert the category details into the categories table
    for category in df['category'].unique():
        cursor.execute('''
            INSERT OR IGNORE INTO categories (category_name)
            VALUES (?)
        ''', (category,))
    #insert the book details into the books table
    #to process each row of the DataFrame used df.iterrows() 
    data = []
    for _,row in df.iterrows():
       data.append((
            row['title'],
            row['price (as listed, in GBP)'],
            row['price_inr'],
            row['star_rating'],
            row['in_stock'],
            row['category']
       ))
    cursor.executemany("""
    INSERT INTO books (title, price_gbp, price_inr, star_rating, in_stock, category_id)
    VALUES (?, ?, ?, ?, ?, (SELECT category_id FROM categories WHERE category_name = ?))
    """, data)
    conn.commit()
    conn.close()  
     
    
url = "http://books.toscrape.com/"
#download the page content
response = requests.get(url)
#BeautifulSoup is a library that allows you to parse HTML and XML documents. It creates a parse tree for parsing HTML and XML documents. In this code, we are using BeautifulSoup to parse the HTML content of the webpage we downloaded using the requests library.
soup = BeautifulSoup(response.text, 'html.parser')
# Find all categories in the website  
category_section = soup.find('div', class_='side_categories')    
categories = category_section.find_all('a')
categ_name = []

for categ in categories:
    link = categ.get('href')
    #to avoid books which is not a category
    if "/category/books/" in link:
        categ_name.append({
            'Category' : categ.text.strip(),
            'URL' : url + link
        })
#to get random categatories
random.seed(32)
random_categ = random.sample(categ_name, k=5)
book_details = get_book_details(random_categ)
df = pd.DataFrame(book_details)        

#get info 
df.info()
#As per info price is string.So, convert price to float and remove symbol
#to handle unexpected text like NaN, we can use the errors parameter of the pd.to_numeric() function to coerce any non-numeric values to NaN. This will allow us to convert the price column to a numeric data type without raising an error.
df["price (as listed, in GBP)"] =(
    pd.to_numeric(
        df["price (as listed, in GBP)"]
        .str.replace("Â£", "", regex=False)
        .str.strip(),
        errors="coerce"
    )
)
#replace NaN values with median
df["price (as listed, in GBP)"] = (
    df["price (as listed, in GBP)"]
    .fillna(df["price (as listed, in GBP)"].median())
)
#convert star_rating to int
df["star_rating"] = df["star_rating"].map({'One':1, 'Two':2, 'Three':3, 'Four':4, 'Five':5})
#distinct values of availability
df["availability"].unique()
#parse the availability text into boolean values
df["in_stock"] = (
    df["availability"].str.strip().str.lower() == "in stock"
)
#convert price from GBP to INR using a conversion rate of 1 GBP = 105.50 INR
df["price_inr"] = df["price (as listed, in GBP)"] * 105.50

#create a table in SQLite database and insert the data from the DataFrame into the table
create_tables(df)
'''SQL queries against the database that collectively demonstrate:
    SELECT/WHERE, ORDER BY, LIMIT, DISTINCT, and (IN or BETWEEN)
    — plus at least one JOIN between your two tables
'''
queries = {
    "query_1": '''
        SELECT title,price_inr 
        FROM books 
        WHERE price_inr > 1000
    ''',
    "query_2": '''
        SELECT DISTINCT category_name
        FROM categories
    ''',
    "query_3": '''
        SELECT title, price_inr, star_rating
        FROM books
        order by star_rating desc
    ''',
    "query_4": '''
        SELECT books.book_id,books.title,categories.category_id,categories.category_name,
        books.price_inr, books.star_rating
        FROM books
        JOIN categories ON categories.category_id = books.category_id
        ORDER BY price_inr ASC LIMIT 5
    ''',
    "query_5": '''
        SELECT title as book_name, price_inr, star_rating  
        FROM books
        WHERE price_inr between 500 and 1000
    ''',
    "query_6": '''
        SELECT title, price_inr, star_rating
        FROM books 
        WHERE star_rating in (4,5) AND price_inr < 500
    '''
}
query_results = {}
#execute the queries and store the results in a dictionary
for query in queries:
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(queries[query])
    query_results[query] = cursor.fetchall()
    conn.close()

'''Read back at least two of the above query 
results into pandas DataFrames using pd.read_sql(...)'''
df_query_1 = pd.read_sql(queries["query_1"], sqlite3.connect('database.db'))
df_query_3 = pd.read_sql(queries["query_3"], sqlite3.connect('database.db'))

# get the categories DataFrame from the database and book DataFrame from the database
with sqlite3.connect('database.db') as conn:
    categories_df = pd.read_sql('SELECT * FROM categories', conn)
    books_df = pd.read_sql('SELECT * FROM books', conn)

#get result of query_4 which is a join query
df_query_4 = pd.read_sql(queries["query_4"], sqlite3.connect('database.db'))

'''reproduce the join-query's result using pd.merge(...)
     directly on your in-memory DataFrames (no SQL)
    — show that both approaches produce equivalent output.
'''
#merge the two DataFrames on category_id to reproduce the join query's result
merged_df = pd.merge(books_df, categories_df, on='category_id', how='left')
sort_book_df = merged_df.sort_values("price_inr",ascending=True).head(5).reset_index()
sort_book_df = sort_book_df[['book_id','title','category_id','category_name','price_inr','star_rating']]
#result of qury_4
df_query_4 = pd.read_sql(queries["query_4"], sqlite3.connect('database.db'))
#check if both approaches produce equivalent output
print(f"Sorted df without using SQL :\n{sort_book_df}\nSorted df using SQL:\n{df_query_4}")