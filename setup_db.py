import sqlite3
import random
from datetime import datetime, timedelta
import os

def create_database():
    db_name = 'ecommerce.db'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create Tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            join_date TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            order_date TEXT NOT NULL,
            quantity INTEGER,
            FOREIGN KEY (user_id) REFERENCES Users(user_id),
            FOREIGN KEY (product_id) REFERENCES Products(product_id)
        )
    ''')

    # Clear existing data if any (for idempotency)
    cursor.execute('DELETE FROM Orders')
    cursor.execute('DELETE FROM Products')
    cursor.execute('DELETE FROM Users')

    # Dummy Data Generation
    first_names = ['Alice', 'Bob', 'Charlie', 'David', 'Emma', 'Frank', 'Grace', 'Hannah', 'Ian', 'Jane', 'Kevin', 'Laura', 'Mike', 'Nina', 'Oliver']
    last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor']
    
    products_data = [
        ('Laptop', 'Electronics', 999.99),
        ('Smartphone', 'Electronics', 699.50),
        ('Headphones', 'Electronics', 149.00),
        ('T-Shirt', 'Clothing', 19.99),
        ('Jeans', 'Clothing', 49.99),
        ('Sneakers', 'Clothing', 89.99),
        ('Coffee Maker', 'Home', 79.00),
        ('Desk Lamp', 'Home', 25.00),
        ('Novel', 'Books', 14.50),
        ('Board Game', 'Toys', 35.00)
    ]

    # Insert Products
    cursor.executemany('INSERT INTO Products (name, category, price) VALUES (?, ?, ?)', products_data)
    
    # Insert 50 Users
    users_data = []
    for _ in range(50):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"{name.replace(' ', '.').lower()}{random.randint(1, 999)}@example.com"
        days_ago = random.randint(1, 365)
        join_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        users_data.append((name, email, join_date))
        
    cursor.executemany('INSERT INTO Users (name, email, join_date) VALUES (?, ?, ?)', users_data)

    # Insert 100 Orders
    orders_data = []
    for _ in range(100):
        user_id = random.randint(1, 50)
        product_id = random.randint(1, len(products_data))
        quantity = random.randint(1, 3)
        days_ago = random.randint(1, 180)
        order_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        orders_data.append((user_id, product_id, order_date, quantity))
        
    cursor.executemany('INSERT INTO Orders (user_id, product_id, order_date, quantity) VALUES (?, ?, ?, ?)', orders_data)

    conn.commit()
    conn.close()
    print(f"Database '{db_name}' created successfully in {os.getcwd()} with dummy data!")

if __name__ == '__main__':
    create_database()
