from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import pytz
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import ssl

app = Flask(__name__)
app.secret_key = "gizli_anahtar"

ssl._create_default_https_context = ssl._create_unverified_context

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
    cursor.execute(
        "INSERT INTO kullanicilar (kullanici_adi, tc, eposta, sifre) VALUES (?, ?, ?, ?)",
        (kullanici_adi, tc, telefon, sifre)
    )
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
        kullanici_adi = request.form.get("kullanici_adi").strip()
        sifre = request.form.get("sifre")
        # Eğer admin değilse, başına Dr. ekle
        if kullanici_adi.lower() != "admin" and not kullanici_adi.startswith("Dt. "):
            kullanici_adi = "Dt. " + kullanici_adi
        if (
            (kullanici_adi == "admin" and sifre == "123") or
            (kullanici_adi == "Dt. Bartu Petrova" and sifre == "123") or
            (kullanici_adi == "Dt. Burçin Kemal" and sifre == "123") or
            (kullanici_adi == "Dt. Deniz Özkan" and sifre == "123") or
            (kullanici_adi == "Dt. Elif Gökdoğan" and sifre == "123") or
            (kullanici_adi == "Dt. Onurhan Tüzün" and sifre == "123") or
            (kullanici_adi == "Dt. Umut Dinçer" and sifre == "123")
        ):
            session["admin"] = True
            session["doktor_adi"] = kullanici_adi
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
        eposta = request.form.get("eposta", "").strip()
        sifre = request.form.get("sifre", "").strip()
        if not (isim and soyisim and tc and eposta and sifre):
            flash("Tüm alanları doldurmalısınız!", "danger")
            return redirect(url_for("kayit_ol"))
        kullanici_adi = f"{isim} {soyisim}"
        if kullanici_var_mi(kullanici_adi, tc):
            flash("Bu kullanıcı adı ve TC ile zaten kayıtlı!", "danger")
            return redirect(url_for("kayit_ol"))
        kullanici_ekle(kullanici_adi, tc, eposta, sifre)
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
    if doktor_adi == "admin":
        cursor.execute("SELECT id, hasta_adi, klinik, doktor, tarih, saat FROM randevular")
    else:
        cursor.execute("SELECT id, hasta_adi, klinik, doktor, tarih, saat FROM randevular WHERE doktor = ?", (doktor_adi,))
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

def kod_gonder(eposta, kod):
    try:
        message = Mail(
            from_email='baharfatih043@gmail.com',  # Kendi mail adresin
            to_emails=eposta,  # Veritabanından alınan e-posta
            subject='Diş Kliniği | Şifre Yenileme Kodunuz',
            html_content=f'''
                <p>Merhaba,</p>
                <p>Şifre yenileme talebiniz üzerine doğrulama kodunuz aşağıdadır:</p>
                <h2 style="color:#007BFF;">{kod}</h2>
                <p>Kod 5 dakika geçerlidir. Eğer bu talebi siz yapmadıysanız, lütfen bu mesajı dikkate almayınız.</p>
                <br>
                <p><em>Diş Kliniği Otomasyon Sistemi</em></p>
            '''
        )
        api_key = os.environ.get("SENDGRID_API_KEY")
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(f"Mail gönderildi! Status code: {response.status_code}")
        print(response.body)
        print(response.headers)
        return True
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return False

@app.route("/sifremi_unuttum", methods=["GET", "POST"])
def sifremi_unuttum():
    if request.method == "POST":
        isim = request.form.get("isim")
        tc = request.form.get("tc")
        kod = request.form.get("kod")
        yeni_sifre = request.form.get("yeni_sifre")
        if "dogrulama_iste" in request.form:
            # Kullanıcıyı kontrol et ve e-postasını veritabanından al
            conn = sqlite3.connect("user.db")
            cursor = conn.cursor()
            cursor.execute("SELECT eposta FROM kullanicilar WHERE kullanici_adi=? AND tc=?", (isim, tc))
            result = cursor.fetchone()
            conn.close()
            if result:
                eposta = result[0]
                dogrulama_kodu = str(random.randint(100000, 999999))
                session["dogrulama_kodu"] = dogrulama_kodu
                session["sifremi_unuttum_bilgi"] = {"isim": isim, "tc": tc, "eposta": eposta}
                kod_gonder(eposta, dogrulama_kodu)
                flash("Doğrulama kodu e-posta adresinize gönderildi.", "success")
                return render_template("sifremi_unuttum.html", kod_gonderildi=True, isim=isim, tc=tc, eposta=eposta)
            else:
                flash("Bilgiler hatalı!", "danger")
        elif "sifre_yenile" in request.form:
            isim = request.form.get("isim")
            tc = request.form.get("tc")
            eposta = request.form.get("eposta")
            kod = request.form.get("kod")
            yeni_sifre = request.form.get("yeni_sifre")
            if kod == session.get("dogrulama_kodu"):
                conn = sqlite3.connect("user.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE kullanicilar SET sifre=? WHERE kullanici_adi=? AND tc=? AND eposta=?", (yeni_sifre, isim, tc, eposta))
                conn.commit()
                conn.close()
                session.pop("dogrulama_kodu", None)
                flash("Şifreniz başarıyla yenilendi!", "success")
                return redirect(url_for("kullanici_login"))
            else:
                flash("Doğrulama kodu hatalı!", "danger")
                return render_template("sifremi_unuttum.html", kod_gonderildi=True, isim=isim, tc=tc, eposta=eposta)
    return render_template("sifremi_unuttum.html")

@app.route("/kullanicilar")
def kullanicilar():
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, kullanici_adi, tc, eposta, sifre FROM kullanicilar")
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
