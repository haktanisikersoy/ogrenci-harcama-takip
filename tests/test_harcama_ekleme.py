"""Görev #1 - Harcama ekleme testleri."""

import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


def test_harcama_eklenince_listede_gorunur(client):
    yanit = client.post(
        "/harcama",
        data={
            "tutar": "120,50",
            "kategori": "Yemek",
            "aciklama": "Yemekhane",
            "tarih": "2026-11-20",
        },
        follow_redirects=True,
    )
    assert yanit.status_code == 200
    sayfa = yanit.get_data(as_text=True)
    assert "Yemekhane" in sayfa
    assert "120.50" in sayfa


@pytest.mark.parametrize("tutar", ["", "0", "-50", "abc"])
def test_gecersiz_tutar_reddedilir(client, tutar):
    yanit = client.post(
        "/harcama",
        data={
            "tutar": tutar,
            "kategori": "Yemek",
            "aciklama": "Gecersiz kayit",
            "tarih": "2026-11-20",
        },
    )
    assert yanit.status_code == 400
    sayfa = yanit.get_data(as_text=True)
    assert 'class="hata"' in sayfa
    # Kayıt listeye eklenmemiş olmalı
    assert "<table>" not in sayfa


def test_gecersiz_kategori_reddedilir(client):
    yanit = client.post("/harcama", data={"tutar": "50", "kategori": "Yok", "tarih": "2026-11-20"})
    assert yanit.status_code == 400
