import sqlite3
import pandas as pd

def create_local_db():
    try:
        with sqlite3.connect("shopping.db") as conn:
            print("db file created")
    except Exception as e:
        print(f"error occured : {e}")

def create_tables():
    try:
        conn = sqlite3.connect("shopping.db")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS CATEGORIES")
        categories_table = """
            CREATE TABLE CATEGORIES(
                category_id INTEGER PRIMARY KEY,
                category_name TEST NOT NULL,
                items TEXT,
                spend_capacity REAL
            )
        """
        cursor.execute(categories_table)
        cursor.execute("DROP TABLE IF EXISTS USERS")
        users_table = """
            CREATE TABLE USERS(
                user_id INTEGER PRIMARY KEY,
                user_name TEXT NOT NULL,
                user_mail TEXT NOT NULL,
                category_id INTEGER,
                FOREIGN KEY (category_id) references CATEGORIES (category_id)
            )
        """
        cursor.execute(users_table)
        cursor.execute("DROP TABLE IF EXISTS ORDERS")
        orders_table = """
            CREATE TABLE ORDERS(
                order_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                order_name TEXT NOT NULL,
                order_value REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES USERS (user_id)
            )
        """
        cursor.execute(orders_table)
        conn.close()
        print("Tables created sucessfully")
    except Exception as e:
        print(f"error occured while creating tables : {e}")

def upload_existing_data():
    try:
        users = pd.read_csv('./sample_datas/users.csv').dropna(how="all")
        categories = pd.read_csv('./sample_datas/categories.csv').dropna(how="all")
        orders = pd.read_csv('./sample_datas/orders.csv').dropna(how="all")

        conn = sqlite3.connect("shopping.db")
        users.to_sql("USERS",conn,if_exists="append",index=True,index_label="user_id")
        categories.to_sql("CATEGORIES",conn,if_exists="append",index=False)
        orders.to_sql("ORDERS",conn,if_exists="append",index=True,index_label="order_id")
        conn.close()
        print(f"Data upload to tables completed successfuly")
    except Exception as e:
        print(f"error occured while uploading : {e}")