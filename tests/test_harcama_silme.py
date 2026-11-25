"""Görev #3 - Harcama silme testleri."""

import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    c = app.test_client()
    c.post(
        "/harcama",
        data={
            "tutar": "80",
            "kategori": "Yemek",
            "aciklama": "Silinecek kayit",
            "tarih": "2026-11-10",
        },
    )
    c.post(
        "/harcama",
        data={
            "tutar": "20",
            "kategori": "Ulaşım",
            "aciklama": "Kalacak kayit",
            "tarih": "2026-11-11",
        },
    )
    return c


def test_silinen_harcama_listeden_kalkar(client):
    yanit = client.post("/harcama/1/sil", follow_redirects=True)
    assert yanit.status_code == 200
    sayfa = yanit.get_data(as_text=True)
    assert "Silinecek kayit" not in sayfa
    assert "Kalacak kayit" in sayfa


def test_silinen_harcama_ozete_dahil_edilmez(client):
    client.post("/harcama/1/sil")
    sayfa = client.get("/ozet?ay=2026-11").get_data(as_text=True)
    assert "Yemek" not in sayfa.split("<table>")[1]
    assert 'id="genel-toplam">20.00 ₺' in sayfa


def test_olmayan_harcama_silinemez(client):
    assert client.post("/harcama/999/sil").status_code == 404
