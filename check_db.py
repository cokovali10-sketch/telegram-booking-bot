import sqlite3
conn = sqlite3.connect('data/booking.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
print('Tables:', cursor.fetchall())
for table in ['users', 'services', 'masters', 'bookings', 'reviews']:
    cursor.execute(f'PRAGMA table_info({table})')
    print(f'{table}:', cursor.fetchall())
conn.close()