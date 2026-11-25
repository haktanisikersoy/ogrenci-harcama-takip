"""Abonelik takibi testleri."""

from datetime import date

import pytest

from abonelik import kalan_metni, sonraki_odeme
from app import create_app

BUGUN = date(2026, 11, 25)


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db"), "BUGUN": BUGUN})
    return app.test_client()


def abonelik_ekle(client, ad, tutar, gun):
    return client.post("/abonelik", data={"ad": ad, "tutar": tutar, "odeme_gunu": gun})


# --- Tarih hesaplama ---


def test_odeme_gunu_bu_ay_gelmediyse_bu_ay():
    assert sonraki_odeme(28, BUGUN) == date(2026, 11, 28)


def test_odeme_gunu_gectiyse_gelecek_ay():
    assert sonraki_odeme(10, BUGUN) == date(2026, 12, 10)


def test_odeme_bugunse_bugun():
    assert sonraki_odeme(25, BUGUN) == date(2026, 11, 25)


def test_kisa_ayda_son_gune_cekilir():
    assert sonraki_odeme(31, date(2027, 2, 10)) == date(2027, 2, 28)
    assert sonraki_odeme(31, date(2026, 11, 5)) == date(2026, 11, 30)


def test_aralikta_yil_degisir():
    assert sonraki_odeme(5, date(2026, 12, 20)) == date(2027, 1, 5)


def test_kalan_metni():
    assert kalan_metni(0) == "Bugün"
    assert kalan_metni(1) == "Yarın"
    assert kalan_metni(12) == "12 gün sonra"


# --- Sayfa davranışı ---


def test_abonelik_eklenince_listede_ve_toplamda_gorunur(client):
    abonelik_ekle(client, "Spotify", "59,99", "10")
    abonelik_ekle(client, "Telefon faturası", "250", "28")
    sayfa = client.get("/abonelikler").get_data(as_text=True)
    assert "<td>Spotify</td>" in sayfa
    assert "<td>Telefon faturası</td>" in sayfa
    assert "10.12.2026" in sayfa  # Spotify'ın sonraki ödemesi
    assert "28.11.2026" in sayfa
    assert 'id="aylik-toplam">309.99 ₺' in sayfa


def test_en_yakin_odeme_listede_once_gelir(client):
    abonelik_ekle(client, "Netflix", "100", "10")
    abonelik_ekle(client, "YouTube", "50", "27")
    sayfa = client.get("/abonelikler").get_data(as_text=True)
    assert sayfa.index("YouTube") < sayfa.index("Netflix")


@pytest.mark.parametrize(
    "ad, tutar, gun",
    [
        ("", "50", "10"),  # boş ad
        ("Spotify", "-5", "10"),  # negatif tutar
        ("Spotify", "abc", "10"),  # geçersiz tutar
        ("Spotify", "50", "0"),  # gün aralık dışı
        ("Spotify", "50", "32"),
        ("Spotify", "50", "on"),  # gün sayı değil
    ],
)
def test_gecersiz_abonelik_reddedilir(client, ad, tutar, gun):
    yanit = abonelik_ekle(client, ad, tutar, gun)
    assert yanit.status_code == 400
    sayfa = yanit.get_data(as_text=True)
    assert 'class="hata"' in sayfa
    assert "Henüz abonelik eklenmedi." in sayfa


def test_yaklasan_odeme_vurgulanir_ve_ana_sayfada_uyari(client):
    abonelik_ekle(client, "Spotify", "59,99", "27")  # 2 gün sonra
    abonelik_ekle(client, "Netflix", "100", "10")  # 15 gün sonra
    sayfa = client.get("/abonelikler").get_data(as_text=True)
    assert "🔔 2 gün sonra" in sayfa
    assert "(15 gün sonra)" in sayfa

    ana = client.get("/").get_data(as_text=True)
    assert 'id="yaklasan-odemeler"' in ana
    assert "Spotify (59.99 ₺, 2 gün sonra)" in ana
    assert "Netflix" not in ana


def test_yaklasan_yoksa_ana_sayfada_uyari_yok(client):
    abonelik_ekle(client, "Netflix", "100", "10")
    assert 'id="yaklasan-odemeler"' not in client.get("/").get_data(as_text=True)


def test_abonelik_silinir(client):
    abonelik_ekle(client, "Spotify", "59,99", "10")
    abonelik_ekle(client, "Netflix", "100", "12")
    sayfa = client.post("/abonelik/1/sil", follow_redirects=True).get_data(as_text=True)
    assert "<td>Spotify</td>" not in sayfa
    assert 'id="aylik-toplam">100.00 ₺' in sayfa


def test_olmayan_abonelik_silinemez(client):
    assert client.post("/abonelik/99/sil").status_code == 404
