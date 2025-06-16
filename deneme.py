import sqlite3
conn = sqlite3.connect("user.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM randevular WHERE doktor = 'Dt. Deniz Özkan'")
print(cursor.fetchall())
conn.close()