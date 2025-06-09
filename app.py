from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "gizli_anahtar"

# Sabit kullanıcılar ve yeni kayıtlar burada tutuluyor (geçici olarak bellekte)
kullanicilar = {
    "admin": {"sifre": "1234"},
    "erol": {"sifre": "1234"}
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        kullanici_adi = request.form.get("kullanici_adi")
        sifre = request.form.get("sifre")
        if kullanici_adi in kullanicilar and kullanici_adi == "admin" and sifre == kullanicilar[kullanici_adi]["sifre"]:
            return redirect(url_for("admin_panel"))
        else:
            flash("Hatalı kullanıcı adı veya şifre!")
    return render_template("admin_login.html")

@app.route("/kullanici", methods=["GET", "POST"])
def kullanici_login():
    if request.method == "POST":
        kullanici_adi = request.form.get("kullanici_adi")
        sifre = request.form.get("sifre")
        if kullanici_adi in kullanicilar and sifre == kullanicilar[kullanici_adi]["sifre"]:
            return redirect(url_for("kullanici_randevu"))
        else:
            flash("Hatalı kullanıcı adı veya şifre!")
    return render_template("kullanici_login.html")

@app.route("/admin/panel")
def admin_panel():
    return "<h1>Admin Paneline Hoş Geldiniz!</h1><a href='/'>Çıkış</a>"

@app.route("/kullanici_randevu", methods=["GET", "POST"])
def kullanici_randevu():
    if request.method == "POST":
        tarih = request.form.get("tarih")
        saat = request.form.get("saat")
        doktor = request.form.get("doktor")
        aciklama = request.form.get("aciklama")
        # Burada verileri veritabanına kaydedebilirsin
        flash("Randevunuz başarıyla oluşturuldu!", "success")
        return redirect(url_for("kullanici_login"))
    return render_template("kullanici_randevu.html")

@app.route("/kayit_ol", methods=["GET", "POST"])
def kayit_ol():
    if request.method == "POST":
        isim = request.form.get("isim")
        soyisim = request.form.get("soyisim")
        telefon = request.form.get("telefon")
        sifre = request.form.get("sifre")
        kullanici_adi = f"{isim} {soyisim}"
        # Kullanıcıyı kaydet (örnek olarak bellekte tutulan sözlüğe ekleniyor)
        kullanicilar[kullanici_adi] = {"sifre": sifre, "telefon": telefon}
        flash("Kayıt başarılı! Giriş yapabilirsiniz.", "success")
        # Kullanıcı adı bilgisini giriş formuna göndermek için query string ile yönlendir
        return redirect(url_for("kullanici_login", kullanici_adi=kullanici_adi))
    return render_template("kayit_ol.html")

if __name__ == "__main__":
    app.run(debug=True)
