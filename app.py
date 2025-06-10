from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import pytz
from jinja2 import Template

app = Flask(__name__)
app.secret_key = "gizli_anahtar"

# Sabit kullanıcılar ve yeni kayıtlar burada tutuluyor (geçici olarak bellekte)
kullanicilar = {
    "admin": {"sifre": "1234"},
    "Fatih Bahar": {
        "sifre": "123",
        "telefon": "05300633798",
        "tc": "49867226666"
    }
}

# 1. Randevuları tutacak liste
randevular = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        kullanici_adi = request.form.get("kullanici_adi")
        sifre = request.form.get("sifre")
        # Burada kendi doğrulama mantığınız olmalı
        if kullanici_adi == "admin" and sifre == "1234":  # Örnek kontrol
            session["admin"] = True
            return redirect(url_for("admin_panel"))
        else:
            flash("Kullanıcı adı veya şifre hatalı!", "danger")
    return render_template("admin_login.html")

@app.route("/admin_panel")
def admin_panel():
    # Giriş kontrolü yapılabilir
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    return render_template("admin_panel.html")

@app.route("/kullanici", methods=["GET", "POST"])
def kullanici_login():
    if request.method == "POST":
        kullanici_adi = request.form.get("kullanici_adi")
        tc = request.form.get("tc")
        sifre = request.form.get("sifre")
        for ad, bilgiler in kullanicilar.items():
            if ad == kullanici_adi and bilgiler.get("tc") == tc and bilgiler.get("sifre") == sifre:
                session["kullanici_adi"] = kullanici_adi  # Burada session'a ekle
                return redirect(url_for("kullanici_randevu"))
        flash("Hatalı kullanıcı adı, TC veya şifre!")
    return render_template("kullanici_login.html")

@app.route("/kullanici_randevu", methods=["GET", "POST"])
def kullanici_randevu():
    from datetime import datetime
    import pytz
    turkiye_saati = datetime.now(pytz.timezone("Europe/Istanbul")).date().isoformat()
    if request.method == "POST":
        klinik = request.form.get("klinik")
        doktor = request.form.get("doktor")
        tarih = request.form.get("tarih")
        saat = request.form.get("saat")
        # Hasta adını session'dan al
        hasta_adi = session.get("kullanici_adi", "Bilinmeyen")
        randevular.append({
            "hasta_adi": hasta_adi,
            "klinik": klinik,
            "doktor": doktor,
            "tarih": tarih,
            "saat": saat
        })
        flash("Randevunuz başarıyla oluşturuldu!", "success")
        # Randevu başarıyla oluşturulduysa:
        return render_template("kullanici_randevu.html", current_date=turkiye_saati, success=True)
    return render_template("kullanici_randevu.html", current_date=turkiye_saati)

@app.route("/kayit_ol", methods=["GET", "POST"])
def kayit_ol():
    if request.method == "POST":
        isim = request.form.get("isim")
        soyisim = request.form.get("soyisim")
        tc = request.form.get("tc")  # TC bilgisini al
        telefon = request.form.get("telefon")
        sifre = request.form.get("sifre")
        kullanici_adi = f"{isim} {soyisim}"
        # TC'yi de kaydet
        kullanicilar[kullanici_adi] = {
            "sifre": sifre,
            "telefon": telefon,
            "tc": tc
        }
        flash("Kayıt başarılı! Giriş yapabilirsiniz.", "success")
        return redirect(url_for("kullanici_login", kullanici_adi=kullanici_adi))
    return render_template("kayit_ol.html")

@app.route("/logout")
def logout():
    session.clear()  # Oturum bilgilerini temizle
    return redirect(url_for("index"))

@app.route("/admin__randevular")
def admin_randevular():
    # 3. Randevular listesini şablona gönder
    return render_template("admin__randevular.html", randevular=randevular)

@app.route("/sifremi_unuttum", methods=["GET", "POST"])
def sifremi_unuttum():
    if request.method == "POST":
        kullanici_adi = request.form.get("kullanici_adi")
        tc = request.form.get("tc")
        yeni_sifre = request.form.get("yeni_sifre")
        yeni_sifre_tekrar = request.form.get("yeni_sifre_tekrar")

        # Şifreler aynı mı kontrol et
        if yeni_sifre != yeni_sifre_tekrar:
            flash("Yeni şifreler aynı olmalı!", "danger")
            return redirect(url_for("sifremi_unuttum"))

        # Kullanıcıyı bul ve TC de eşleşiyor mu kontrol et
        bilgiler = kullanicilar.get(kullanici_adi)
        if bilgiler and bilgiler.get("tc") == tc:
            if bilgiler.get("sifre") == yeni_sifre:
                flash("Yeni şifre eski şifreyle aynı olamaz!", "danger")
                return redirect(url_for("sifremi_unuttum"))
            bilgiler["sifre"] = yeni_sifre
            flash("Şifreniz başarıyla güncellendi. Giriş yapabilirsiniz.", "success")
            return redirect(url_for("kullanici_login"))
        else:
            flash("Kullanıcı adı veya TC Kimlik Numarası hatalı!", "danger")
            return redirect(url_for("sifremi_unuttum"))

    return render_template("sifremi_unuttum.html")

if __name__ == "__main__":
    app.run(debug=True)
