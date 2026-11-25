"""Görev #2 - Aylık kategori özeti testleri."""

import re

import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    c = app.test_client()
    ornekler = [
        ("100", "Yemek", "2026-11-03"),
        ("50,25", "Yemek", "2026-11-15"),
        ("30", "Ulaşım", "2026-11-20"),
        ("999", "Eğlence", "2026-10-31"),  # başka ay - özete girmemeli
    ]
    for tutar, kategori, tarih in ornekler:
        c.post("/harcama", data={"tutar": tutar, "kategori": kategori, "tarih": tarih})
    return c


def satir_toplami(sayfa, kategori):
    """Tablodaki ilgili kategori satırının toplam tutarını döndürür."""
    eslesme = re.search(
        rf"<td>{kategori}</td>\s*<td class=\"sayi\">\d+</td>\s*<td class=\"sayi\">([\d.]+) ₺</td>",
        sayfa,
    )
    return eslesme.group(1) if eslesme else None


def test_kategori_toplamlari_dogru(client):
    sayfa = client.get("/ozet?ay=2026-11").get_data(as_text=True)
    assert satir_toplami(sayfa, "Yemek") == "150.25"
    assert satir_toplami(sayfa, "Ulaşım") == "30.00"


def test_genel_toplam_gosterilir(client):
    sayfa = client.get("/ozet?ay=2026-11").get_data(as_text=True)
    assert 'id="genel-toplam">180.25 ₺' in sayfa


def test_baska_ay_ozete_dahil_edilmez(client):
    sayfa = client.get("/ozet?ay=2026-11").get_data(as_text=True)
    assert "Eğlence" not in sayfa
    assert "999" not in sayfa

    ekim = client.get("/ozet?ay=2026-10").get_data(as_text=True)
    assert satir_toplami(ekim, "Eğlence") == "999.00"
    assert 'id="genel-toplam">999.00 ₺' in ekim


def test_harcama_olmayan_ay(client):
    sayfa = client.get("/ozet?ay=2025-01").get_data(as_text=True)
    assert "harcama yok" in sayfa


def test_gecersiz_ay_bicimi(client):
    yanit = client.get("/ozet?ay=kasim")
    assert yanit.status_code == 400
