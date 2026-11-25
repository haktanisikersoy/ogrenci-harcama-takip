"""Öğrenci Harcama Takip - basit Flask uygulaması."""
import os
import sqlite3
from datetime import date

from flask import Flask, g, redirect, render_template, request, url_for

KATEGORILER = ["Yemek", "Ulaşım", "Kira/Fatura", "Eğitim", "Eğlence", "Diğer"]


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # Veritabanı instance/ klasöründe tutulur (Python .gitignore şablonu bu klasörü yok sayar)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "harcamalar.db"),
    )
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(exc=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        with app.app_context():
            get_db().execute(
                """CREATE TABLE IF NOT EXISTS harcamalar (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       tutar REAL NOT NULL,
                       kategori TEXT NOT NULL,
                       aciklama TEXT,
                       tarih TEXT NOT NULL
                   )"""
            )
            get_db().commit()

    init_db()

    def harcamalari_getir():
        return get_db().execute(
            "SELECT * FROM harcamalar ORDER BY tarih DESC, id DESC"
        ).fetchall()

    @app.route("/", methods=["GET"])
    def index():
        return render_template(
            "index.html",
            harcamalar=harcamalari_getir(),
            kategoriler=KATEGORILER,
            bugun=date.today().isoformat(),
            hata=None,
            form={},
        )

    @app.route("/harcama", methods=["POST"])
    def harcama_ekle():
        form = request.form
        tutar_str = form.get("tutar", "").strip().replace(",", ".")
        kategori = form.get("kategori", "")
        aciklama = form.get("aciklama", "").strip()
        tarih = form.get("tarih", "").strip() or date.today().isoformat()

        hata = None
        try:
            tutar = float(tutar_str)
            if tutar <= 0:
                hata = "Tutar sıfırdan büyük olmalıdır."
        except ValueError:
            hata = "Lütfen geçerli bir tutar girin."

        if not hata and kategori not in KATEGORILER:
            hata = "Lütfen geçerli bir kategori seçin."

        if not hata:
            try:
                date.fromisoformat(tarih)
            except ValueError:
                hata = "Lütfen geçerli bir tarih girin."

        if hata:
            return (
                render_template(
                    "index.html",
                    harcamalar=harcamalari_getir(),
                    kategoriler=KATEGORILER,
                    bugun=date.today().isoformat(),
                    hata=hata,
                    form=form,
                ),
                400,
            )

        db = get_db()
        db.execute(
            "INSERT INTO harcamalar (tutar, kategori, aciklama, tarih) VALUES (?, ?, ?, ?)",
            (round(tutar, 2), kategori, aciklama, tarih),
        )
        db.commit()
        return redirect(url_for("index"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
