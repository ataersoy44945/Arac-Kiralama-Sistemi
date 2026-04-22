from datetime import datetime

SINIF_FIYAT = {
    "eco":      150,
    "standart": 250,
    "premium":  400,
    "vip":      750,
}

SINIF_LISTESI = list(SINIF_FIYAT.keys())

_GECE_BASLANGIC = 18   # 18:00 dahil
_GECE_BITIS     = 23   # 23:00 dahil (saat 23:xx)
_GECE_ZAM       = 0.20
_HAFTA_SONU_ZAM = 0.15
_GUNLUK_INDIRIM = 0.10  # 24+ saat için %10 indirim
_VIP_MIN_SAAT   = 3
_MIN_UCRET      = 120   # her kiralama için asgari ücret (TL)

_FMT = "%Y-%m-%d %H:%M:%S"


def fiyat_hesapla(sinif: str, baslangic_str: str, bitis_str: str) -> tuple:
    """
    (True, detay_dict) veya (False, hata_mesaji) döndürür.

    detay_dict anahtarları:
        sinif, sure_saat, saatlik_fiyat, base_fiyat,
        gece_zammi, hafta_sonu, gunluk_indirim, toplam_fiyat
    """
    if sinif not in SINIF_FIYAT:
        return False, f"Geçersiz araç sınıfı: '{sinif}'"

    baslangic = datetime.strptime(baslangic_str, _FMT)
    bitis     = datetime.strptime(bitis_str,     _FMT)

    sure_sn = (bitis - baslangic).total_seconds()
    if sure_sn <= 0:
        return False, "Bitiş zamanı başlangıçtan önce olamaz!"

    sure_saat = sure_sn / 3600
    saatlik   = SINIF_FIYAT[sinif]

    if sinif == "vip" and sure_saat < _VIP_MIN_SAAT:
        return False, (
            f"VIP araçlar için minimum kiralama süresi {_VIP_MIN_SAAT} saattir. "
            f"(Mevcut süre: {sure_saat:.1f} saat)"
        )

    base_fiyat = sure_saat * saatlik

    saat        = baslangic.hour
    gece_zammi  = _GECE_BASLANGIC <= saat <= _GECE_BITIS
    hafta_sonu  = baslangic.weekday() >= 5   # 5=Cumartesi, 6=Pazar
    gunluk      = sure_saat >= 24

    toplam = base_fiyat
    if gece_zammi:
        toplam *= (1 + _GECE_ZAM)
    if hafta_sonu:
        toplam *= (1 + _HAFTA_SONU_ZAM)
    if gunluk:
        toplam *= (1 - _GUNLUK_INDIRIM)

    toplam = max(toplam, _MIN_UCRET)

    return True, {
        "sinif":          sinif,
        "sure_saat":      round(sure_saat, 2),
        "saatlik_fiyat":  saatlik,
        "base_fiyat":     round(base_fiyat, 2),
        "gece_zammi":     gece_zammi,
        "hafta_sonu":     hafta_sonu,
        "gunluk_indirim": gunluk,
        "toplam_fiyat":   round(toplam, 2),
    }


def fiyat_ozeti(detay: dict) -> str:
    """Fiyat detaylarını okunabilir metin olarak döndürür."""
    satirlar = [
        f"Araç sınıfı    : {detay['sinif'].upper()}",
        f"Süre           : {detay['sure_saat']:.2f} saat",
        f"Saatlik tarife : {detay['saatlik_fiyat']:,} TL",
        f"Temel fiyat    : {detay['base_fiyat']:,.2f} TL",
    ]
    if detay["gece_zammi"]:
        satirlar.append("Gece zammı     : +%20 (18:00–23:00)")
    if detay["hafta_sonu"]:
        satirlar.append("Hafta sonu     : +%15")
    if detay["gunluk_indirim"]:
        satirlar.append("Günlük indirim : -%10 (24+ saat)")
    if detay["toplam_fiyat"] == _MIN_UCRET and detay["base_fiyat"] < _MIN_UCRET:
        satirlar.append(f"Minimum ücret  : {_MIN_UCRET} TL uygulandı")
    satirlar.append(f"─────────────────────────────")
    satirlar.append(f"TOPLAM ÜCRET   : {detay['toplam_fiyat']:,.2f} TL")
    return "\n".join(satirlar)
