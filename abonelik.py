"""Abonelik ödeme tarihi hesaplamaları."""

from calendar import monthrange
from datetime import date

YAKLASAN_GUN = 3  # Bu kadar gün (veya daha az) kalan ödemeler "yaklaşan" sayılır


def odeme_tarihi(yil, ay, gun):
    """Ayın gün sayısını aşan ödeme günlerini ayın son gününe çeker (ör. 31 Şubat -> 28 Şubat)."""
    return date(yil, ay, min(gun, monthrange(yil, ay)[1]))


def sonraki_odeme(gun, bugun):
    """Bugün veya sonrasındaki ilk ödeme tarihini döndürür."""
    bu_ay = odeme_tarihi(bugun.year, bugun.month, gun)
    if bu_ay >= bugun:
        return bu_ay
    yil, ay = (bugun.year + 1, 1) if bugun.month == 12 else (bugun.year, bugun.month + 1)
    return odeme_tarihi(yil, ay, gun)


def kalan_metni(kalan_gun):
    if kalan_gun == 0:
        return "Bugün"
    if kalan_gun == 1:
        return "Yarın"
    return f"{kalan_gun} gün sonra"
