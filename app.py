from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import pytz
import sqlite3

app = Flask(__name__)
app.secret_key = "gizli_anahtar"

# --- Veritabanı yardımcı fonksiyonları ---
def veritabani_baglanti():
    return sqlite3.connect("user.db")

def kullanici_var_mi(kullanici_adi, tc):
    if not kullanici_adi or not tc:
        return None
    conn = veritabani_baglanti()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=? AND tc=?", (kullanici_adi, tc))
    user = cursor.fetchone()
    conn.close()
    return user

def kullanici_dogrula(kullanici_adi, tc, sifre):
    conn = veritabani_baglanti()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=? AND tc=? AND sifre=?", (kullanici_adi, tc, sifre))
    user = cursor.fetchone()
    conn.close()
    return user

def kullanici_ekle(kullanici_adi, tc, telefon, sifre):
    conn = veritabani_baglanti()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO kullanicilar (kullanici_adi, tc, telefon, sifre) VALUES (?, ?, ?, ?)", (kullanici_adi, tc, telefon, sifre))
    conn.commit()
    conn.close()

def sifre_guncelle(kullanici_adi, tc, yeni_sifre):
    conn = veritabani_baglanti()
    cursor = conn.cursor()
    cursor.execute("UPDATE kullanicilar SET sifre=? WHERE kullanici_adi=? AND tc=?", (yeni_sifre, kullanici_adi, tc))
    conn.commit()
    conn.close()

def kullanici_sifre_getir(kullanici_adi, tc):
    conn = veritabani_baglanti()
    cursor = conn.cursor()
    cursor.execute("SELECT sifre FROM kullanicilar WHERE kullanici_adi=? AND tc=?", (kullanici_adi, tc))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Randevuları tutacak liste (isteğe bağlı veritabanına da taşıyabilirsin)
randevular = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        kullanici_adi = request.form.get("kullanici_adi")
        sifre = request.form.get("sifre")
        # Sadece admin için sabit kontrol
        if (
            (kullanici_adi == "admin" and sifre == "123") or
            (kullanici_adi == "Bartu Petrova" and sifre == "123") or
            (kullanici_adi == "Burçin Kemal" and sifre == "123") or
            (kullanici_adi == "Deniz Özkan" and sifre == "123") or
            (kullanici_adi == "Elif Gökdoğan" and sifre == "123") or
            (kullanici_adi == "Onurhan Tüzün" and sifre == "123") or
            (kullanici_adi == "Umut Dinçer" and sifre == "123")
        ):
            session["admin"] = True
            session["doktor_adi"] = kullanici_adi   # <-- Burası eklendi
            return redirect(url_for("admin_panel"))
        else:
            flash("Kullanıcı adı veya şifre hatalı!", "danger")
    return render_template("admin_login.html")

@app.route("/admin_panel")
def admin_panel():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    doktor_adi = session.get("doktor_adi", "Doktor")
    return render_template("admin_panel.html", doktor_adi=doktor_adi)

@app.route("/kullanici", methods=["GET", "POST"])
def kullanici_login():
    if request.method == "POST":
        kullanici_adi = request.form.get("kullanici_adi")
        tc = request.form.get("tc")
        sifre = request.form.get("sifre")
        user = kullanici_dogrula(kullanici_adi, tc, sifre)
        if user:
            session["kullanici_adi"] = kullanici_adi
            return redirect(url_for("kullanici_randevu"))
        flash("Hatalı kullanıcı adı, TC veya şifre!")
    return render_template("kullanici_login.html")

@app.route("/kullanici_randevu", methods=["GET", "POST"])
def kullanici_randevu():
    turkiye_saati = datetime.now(pytz.timezone("Europe/Istanbul")).date().isoformat()
    if request.method == "POST":
        klinik = request.form.get("klinik")
        doktor = request.form.get("doktor")
        tarih = request.form.get("tarih")
        saat = request.form.get("saat")
        hasta_adi = session.get("kullanici_adi", "Bilinmeyen")
        # --- BURASI GÜNCELLENDİ ---
        conn = sqlite3.connect("user.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO randevular (hasta_adi, klinik, doktor, tarih, saat) VALUES (?, ?, ?, ?, ?)",
            (hasta_adi, klinik, doktor, tarih, saat)
        )
        conn.commit()
        conn.close()
        flash("Randevunuz başarıyla oluşturuldu!", "success")
        return render_template("kullanici_randevu.html", current_date=turkiye_saati, success=True)
    return render_template("kullanici_randevu.html", current_date=turkiye_saati)

@app.route("/kayit_ol", methods=["GET", "POST"])
def kayit_ol():
    if request.method == "POST":
        isim = request.form.get("isim", "").strip()
        soyisim = request.form.get("soyisim", "").strip()
        tc = request.form.get("tc", "").strip()
        telefon = request.form.get("telefon", "").strip()
        sifre = request.form.get("sifre", "").strip()
        if not (isim and soyisim and tc and telefon and sifre):
            flash("Tüm alanları doldurmalısınız!", "danger")
            return redirect(url_for("kayit_ol"))
        kullanici_adi = f"{isim} {soyisim}"
        if kullanici_var_mi(kullanici_adi, tc):
            flash("Bu kullanıcı adı ve TC ile zaten kayıtlı!", "danger")
            return redirect(url_for("kayit_ol"))
        kullanici_ekle(kullanici_adi, tc, telefon, sifre)
        flash("Kayıt başarılı! Giriş yapabilirsiniz.", "success")
        return redirect(url_for("kullanici_login"))
    return render_template("kayit_ol.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/admin__randevular")
def admin_randevular():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    doktor_adi = session.get("doktor_adi")
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    # Eğer giriş yapan admin ise tüm randevuları çek, değilse sadece kendi randevularını
    if doktor_adi == "admin":
        cursor.execute("SELECT id, hasta_adi, klinik, doktor, tarih, saat FROM randevular")
    else:
        cursor.execute("SELECT id, hasta_adi, klinik, doktor, tarih, saat FROM randevular WHERE LOWER(doktor) LIKE ?", (f"%{doktor_adi.lower()}%",))
    randevular = [
        {
            "id": row[0],
            "hasta_adi": row[1],
            "klinik": row[2],
            "doktor": row[3],
            "tarih": row[4],
            "saat": row[5]
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return render_template("admin__randevular.html", randevular=randevular, doktor_adi=doktor_adi)

@app.route("/sifremi_unuttum", methods=["GET", "POST"])
def sifremi_unuttum():
    if request.method == "POST":
        kullanici_adi = request.form.get("kullanici_adi")
        tc = request.form.get("tc")
        yeni_sifre = request.form.get("yeni_sifre")
        yeni_sifre_tekrar = request.form.get("yeni_sifre_tekrar")

        if yeni_sifre != yeni_sifre_tekrar:
            flash("Yeni şifreler aynı olmalı!", "danger")
            return redirect(url_for("sifremi_unuttum"))

        eski_sifre = kullanici_sifre_getir(kullanici_adi, tc)
        if eski_sifre is None:
            flash("Kullanıcı adı veya TC Kimlik Numarası hatalı!", "danger")
            return redirect(url_for("sifremi_unuttum"))
        if eski_sifre == yeni_sifre:
            flash("Yeni şifre eski şifreyle aynı olamaz!", "danger")
            return redirect(url_for("sifremi_unuttum"))

        sifre_guncelle(kullanici_adi, tc, yeni_sifre)
        flash("Şifreniz başarıyla güncellendi. Giriş yapabilirsiniz.", "success")
        return redirect(url_for("kullanici_login"))

    return render_template("sifremi_unuttum.html")

@app.route("/kullanicilar")
def kullanicilar():
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, kullanici_adi, tc, telefon FROM kullanicilar")
    kullanicilar = cursor.fetchall()
    conn.close()
    doktor_adi = session.get("doktor_adi", "")
    return render_template("kullanicilar.html", kullanicilar=kullanicilar, doktor_adi=doktor_adi)

def get_db_connection():
    conn = sqlite3.connect('user.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/kullanici_sil/<int:kullanici_id>', methods=['POST'])
def kullanici_sil(kullanici_id):
    if session.get("doktor_adi") != "admin":
        flash("Sadece admin kullanıcı silebilir!", "danger")
        return redirect(url_for('kullanicilar'))
    try:
        conn = sqlite3.connect("user.db")
        conn.execute('DELETE FROM kullanicilar WHERE id = ?', (kullanici_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        return f"Hata oluştu: {e}"
    return redirect(url_for('kullanicilar'))

@app.route('/randevu_sil/<int:randevu_id>', methods=['POST'])
def randevu_sil(randevu_id):
    if session.get("doktor_adi") != "admin":
        flash("Sadece admin randevu silebilir!", "danger")
        return redirect(url_for('admin_randevular'))
    conn = sqlite3.connect("user.db")
    conn.execute('DELETE FROM randevular WHERE id = ?', (randevu_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_randevular'))

@app.route("/hekimler")
def hekimler():
    return render_template("hekimler.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
