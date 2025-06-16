import sqlite3

def get_db_connection():
    conn = sqlite3.connect('user.db')
    conn.row_factory = sqlite3.Row
    return conn

def tablo_olustur():
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT NOT NULL,
            tc TEXT,
            eposta TEXT,
            sifre TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

tablo_olustur()

def kullanicilari_cek():
    try:
        conn = sqlite3.connect("user.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kullanicilar")
        kullanicilar = cursor.fetchall()
        return kullanicilar
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        return []
    finally:
        conn.close()

kullanicilar = kullanicilari_cek()
print("Kayıtlı Kullanıcılar:")
for kullanici in kullanicilar:
    print(f"ID: {kullanici[0]}, Kullanıcı Adı: {kullanici[1]}, TC: {kullanici[2]}, E-posta: {kullanici[3]}, Şifre: {kullanici[4]}")

