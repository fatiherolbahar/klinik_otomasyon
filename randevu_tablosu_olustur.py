import sqlite3

def randevular_tablosu_olustur():
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS randevular (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hasta_adi TEXT NOT NULL,
            klinik TEXT NOT NULL,
            doktor TEXT NOT NULL,
            tarih TEXT NOT NULL,
            saat TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

randevular_tablosu_olustur()