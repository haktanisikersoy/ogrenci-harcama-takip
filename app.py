"""Öğrenci Harcama Takip - basit Flask uygulaması."""

import math
import os
import sqlite3
from datetime import date, datetime

from flask import Flask, g, redirect, render_template, request, url_for

from abonelik import YAKLASAN_GUN, kalan_metni, sonraki_odeme

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
            get_db().execute(
                "CREATE TABLE IF NOT EXISTS ayarlar (anahtar TEXT PRIMARY KEY, deger TEXT NOT NULL)"
            )
            get_db().execute(
                """CREATE TABLE IF NOT EXISTS abonelikler (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       ad TEXT NOT NULL,
                       tutar REAL NOT NULL,
                       odeme_gunu INTEGER NOT NULL
                   )"""
            )
            get_db().commit()

    init_db()

    def harcamalari_getir():
        return get_db().execute("SELECT * FROM harcamalar ORDER BY tarih DESC, id DESC").fetchall()

    def tutar_coz(metin):
        """Kullanıcının girdiği tutarı sayıya çevirir. (tutar, hata) döndürür."""
        try:
            tutar = float(metin.strip().replace(",", "."))
        except ValueError:
            return None, "Lütfen geçerli bir tutar girin."
        if not math.isfinite(tutar) or tutar <= 0:
            return None, "Tutar sıfırdan büyük olmalıdır."
        return round(tutar, 2), None

    def butce_limiti_getir():
        satir = (
            get_db().execute("SELECT deger FROM ayarlar WHERE anahtar = 'aylik_limit'").fetchone()
        )
        return float(satir["deger"]) if satir else None

    def butce_durumu(ay):
        """Seçilen ay için bütçe bilgisini döndürür; limit yoksa None."""
        limit = butce_limiti_getir()
        if limit is None:
            return None
        harcanan = (
            get_db()
            .execute(
                "SELECT COALESCE(ROUND(SUM(tutar), 2), 0) AS toplam "
                "FROM harcamalar WHERE substr(tarih, 1, 7) = ?",
                (ay,),
            )
            .fetchone()["toplam"]
        )
        return {
            "limit": limit,
            "harcanan": harcanan,
            "kalan": round(limit - harcanan, 2),
            "asildi": harcanan > limit,
            "yuzde": min(round(harcanan / limit * 100, 1), 100),
        }

    def bugunu_al():
        # Testlerde sabit bir tarih verilebilsin diye BUGUN ayarı kullanılabilir
        return app.config.get("BUGUN") or date.today()

    def abonelikleri_getir():
        """Abonelikleri bir sonraki ödeme tarihine göre (en yakın önce) döndürür."""
        bugun = bugunu_al()
        liste = []
        for a in get_db().execute("SELECT * FROM abonelikler"):
            tarih = sonraki_odeme(a["odeme_gunu"], bugun)
            kalan = (tarih - bugun).days
            liste.append(
                {
                    "id": a["id"],
                    "ad": a["ad"],
                    "tutar": a["tutar"],
                    "odeme_gunu": a["odeme_gunu"],
                    "sonraki_odeme": tarih.strftime("%d.%m.%Y"),
                    "kalan_gun": kalan,
                    "kalan_metni": kalan_metni(kalan),
                    "yaklasan": kalan <= YAKLASAN_GUN,
                }
            )
        return sorted(liste, key=lambda a: (a["kalan_gun"], a["ad"]))

    def ana_sayfa(hata=None, form=None, butce_hata=None, durum_kodu=200):
        return (
            render_template(
                "index.html",
                harcamalar=harcamalari_getir(),
                kategoriler=KATEGORILER,
                bugun=date.today().isoformat(),
                hata=hata,
                form=form or {},
                butce=butce_durumu(date.today().strftime("%Y-%m")),
                butce_hata=butce_hata,
                yaklasan_abonelikler=[a for a in abonelikleri_getir() if a["yaklasan"]],
            ),
            durum_kodu,
        )

    @app.route("/", methods=["GET"])
    def index():
        return ana_sayfa()

    @app.route("/butce", methods=["POST"])
    def butce_kaydet():
        limit, hata = tutar_coz(request.form.get("limit", ""))
        if hata:
            return ana_sayfa(
                butce_hata="Bütçe limiti: " + hata[0].lower() + hata[1:], durum_kodu=400
            )
        db = get_db()
        db.execute(
            "INSERT INTO ayarlar (anahtar, deger) VALUES ('aylik_limit', ?) "
            "ON CONFLICT(anahtar) DO UPDATE SET deger = excluded.deger",
            (str(limit),),
        )
        db.commit()
        return redirect(url_for("index"))

    @app.route("/harcama", methods=["POST"])
    def harcama_ekle():
        form = request.form
        kategori = form.get("kategori", "")
        aciklama = form.get("aciklama", "").strip()
        tarih = form.get("tarih", "").strip() or date.today().isoformat()

        tutar, hata = tutar_coz(form.get("tutar", ""))

        if not hata and kategori not in KATEGORILER:
            hata = "Lütfen geçerli bir kategori seçin."

        if not hata:
            try:
                date.fromisoformat(tarih)
            except ValueError:
                hata = "Lütfen geçerli bir tarih girin."

        if hata:
            return ana_sayfa(hata=hata, form=form, durum_kodu=400)

        db = get_db()
        db.execute(
            "INSERT INTO harcamalar (tutar, kategori, aciklama, tarih) VALUES (?, ?, ?, ?)",
            (tutar, kategori, aciklama, tarih),
        )
        db.commit()
        return redirect(url_for("index"))

    @app.route("/harcama/<int:harcama_id>/sil", methods=["POST"])
    def harcama_sil(harcama_id):
        db = get_db()
        silinen = db.execute("DELETE FROM harcamalar WHERE id = ?", (harcama_id,)).rowcount
        db.commit()
        if silinen == 0:
            return "Harcama bulunamadı.", 404
        return redirect(url_for("index"))

    def abonelik_sayfasi(hata=None, form=None, durum_kodu=200):
        abonelikler = abonelikleri_getir()
        return (
            render_template(
                "abonelikler.html",
                abonelikler=abonelikler,
                aylik_toplam=round(sum(a["tutar"] for a in abonelikler), 2),
                yaklasan_gun=YAKLASAN_GUN,
                hata=hata,
                form=form or {},
            ),
            durum_kodu,
        )

    @app.route("/abonelikler", methods=["GET"])
    def abonelikler():
        return abonelik_sayfasi()

    @app.route("/abonelik", methods=["POST"])
    def abonelik_ekle():
        form = request.form
        ad = form.get("ad", "").strip()
        tutar, hata = tutar_coz(form.get("tutar", ""))

        if not hata and not ad:
            hata = "Abonelik adı boş olamaz."
        if not hata:
            try:
                odeme_gunu = int(form.get("odeme_gunu", ""))
                if not 1 <= odeme_gunu <= 31:
                    raise ValueError
            except ValueError:
                hata = "Ödeme günü 1 ile 31 arasında bir sayı olmalıdır."

        if hata:
            return abonelik_sayfasi(hata=hata, form=form, durum_kodu=400)

        db = get_db()
        db.execute(
            "INSERT INTO abonelikler (ad, tutar, odeme_gunu) VALUES (?, ?, ?)",
            (ad, tutar, odeme_gunu),
        )
        db.commit()
        return redirect(url_for("abonelikler"))

    @app.route("/abonelik/<int:abonelik_id>/sil", methods=["POST"])
    def abonelik_sil(abonelik_id):
        db = get_db()
        silinen = db.execute("DELETE FROM abonelikler WHERE id = ?", (abonelik_id,)).rowcount
        db.commit()
        if silinen == 0:
            return "Abonelik bulunamadı.", 404
        return redirect(url_for("abonelikler"))

    @app.route("/ozet", methods=["GET"])
    def ozet():
        db = get_db()
        bu_ay = date.today().strftime("%Y-%m")
        ay = request.args.get("ay", "").strip() or bu_ay

        # Ay "YYYY-AA" biçiminde olmalı
        try:
            datetime.strptime(ay, "%Y-%m")
        except ValueError:
            return render_template(
                "ozet.html",
                hata="Geçersiz ay biçimi. Örnek: 2026-11",
                ay=ay,
                aylar=[bu_ay],
                kategoriler=[],
                genel_toplam=0,
            ), 400

        # Seçim listesi: kaydı olan aylar + içinde bulunulan ay
        aylar = {
            r["ay"] for r in db.execute("SELECT DISTINCT substr(tarih, 1, 7) AS ay FROM harcamalar")
        }
        aylar.update({bu_ay, ay})

        kategoriler = db.execute(
            """SELECT kategori, ROUND(SUM(tutar), 2) AS toplam, COUNT(*) AS adet
               FROM harcamalar
               WHERE substr(tarih, 1, 7) = ?
               GROUP BY kategori
               ORDER BY toplam DESC""",
            (ay,),
        ).fetchall()
        genel_toplam = round(sum(k["toplam"] for k in kategoriler), 2)

        return render_template(
            "ozet.html",
            hata=None,
            ay=ay,
            aylar=sorted(aylar, reverse=True),
            kategoriler=kategoriler,
            genel_toplam=genel_toplam,
            butce=butce_durumu(ay),
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
