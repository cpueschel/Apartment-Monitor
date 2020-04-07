import sqlite3

conn = sqlite3.connect('apartments.db')

c = conn.cursor()

c.execute('''CREATE TABLE apartment (
                name TEXT not NULL,
                location TEXT,
                city TEXT
            );''')

c.execute('''CREATE TABLE prices
             (apartment_id INTEGER, price INTEGER, apartment_type TEXT ,date INTEGER)''')

conn.commit()

conn.close()
