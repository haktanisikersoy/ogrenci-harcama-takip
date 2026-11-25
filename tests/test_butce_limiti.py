"""Görev #4 - Aylık bütçe limiti uyarısı testleri."""
from datetime import date

import pytest

from app import create_app

BUGUN = date.today().isoformat()
BU_AY = BUGUN[:7]


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


def harcama_ekle(client, tutar, tarih=BUGUN):
    client.post("/harcama", data={"tutar": tutar, "kategori": "Yemek", "tarih": tarih})


def test_limit_kaydedilir(client):
    sayfa = client.post("/butce", data={"limit": "1500"}, follow_redirects=True).get_data(as_text=True)
    assert 'value="1500.00"' in sayfa
    assert "/ 1500.00 ₺" in sayfa


@pytest.mark.parametrize("limit", ["", "0", "-100", "abc"])
def test_gecersiz_limit_reddedilir(client, limit):
    yanit = client.post("/butce", data={"limit": limit})
    assert yanit.status_code == 400
    assert "Bütçe limiti" in yanit.get_data(as_text=True)


def test_limit_asilmadiysa_uyari_yok(client):
    client.post("/butce", data={"limit": "1000"})
    harcama_ekle(client, "400")
    sayfa = client.get("/").get_data(as_text=True)
    assert 'id="butce-uyari"' not in sayfa
    assert "600.00 ₺ kaldı" in sayfa


def test_limit_asilinca_uyari_gorunur(client):
    client.post("/butce", data={"limit": "1000"})
    harcama_ekle(client, "700")
    harcama_ekle(client, "450")
    sayfa = client.get("/").get_data(as_text=True)
    assert 'id="butce-uyari"' in sayfa
    assert "150.00 ₺ aştın" in sayfa

    ozet = client.get(f"/ozet?ay={BU_AY}").get_data(as_text=True)
    assert 'id="butce-uyari"' in ozet


def test_baska_ayin_harcamasi_limite_sayilmaz(client):
    client.post("/butce", data={"limit": "100"})
    harcama_ekle(client, "500", tarih="2000-01-15")
    sayfa = client.get("/").get_data(as_text=True)
    assert 'id="butce-uyari"' not in sayfa


def test_limit_yoksa_uyari_yok(client):
    harcama_ekle(client, "99999")
    assert 'id="butce-uyari"' not in client.get("/").get_data(as_text=True)
