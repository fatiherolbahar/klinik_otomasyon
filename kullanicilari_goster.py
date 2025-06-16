from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import pytz
import sqlite3

app = Flask(__name__)

@app.route("/kullanicilar")
def kullanicilar():
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, kullanici_adi, tc, eposta FROM kullanicilar")
    kullanicilar = cursor.fetchall()
    conn.close()
    return render_template("kullanicilar.html", kullanicilar=kullanicilar)

if __name__ == "__main__":
    app.run(debug=True)
