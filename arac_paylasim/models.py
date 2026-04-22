# ============================================================
#   models.py — Veri Modelleri
# ============================================================

# -------------------------------------------------------
# HESAP — Giriş oturumu
# -------------------------------------------------------
class Hesap:
    """Login sonrası oluşturulan oturum nesnesi."""

    def __init__(self, kullanici_id: str, kullanici_adi: str, ad: str, rol: str):
        self.__kullanici_id  = kullanici_id
        self.__kullanici_adi = kullanici_adi
        self.__ad            = ad
        self.__rol           = rol   # 'admin' | 'kullanici'

    @property
    def kullanici_id(self):  return self.__kullanici_id
    @property
    def kullanici_adi(self): return self.__kullanici_adi
    @property
    def ad(self):            return self.__ad
    @property
    def rol(self):           return self.__rol

    def is_admin(self) -> bool:
        return self.__rol == "admin"

    def __repr__(self):
        return f"Hesap({self.__kullanici_adi!r}, {self.__rol!r})"


# -------------------------------------------------------
# ARAÇ — Base + Alt sınıflar
# -------------------------------------------------------
class Arac:
    """Sistemdeki bir aracı temsil eder."""

    def __init__(self, arac_id, tur, marka, model, kilometre, musait_mi,
                 sinif="standart", vites="Manuel", yakit="Benzin",
                 koltuk=5, puan=4.0, durum_arac="musait",
                 aciklama="", gunluk_fiyat=0.0, enlem=None, boylam=None,
                 gorsel=""):
        self.__arac_id      = arac_id
        self.__tur          = tur
        self.__marka        = marka
        self.__model        = model
        self.__kilometre    = kilometre
        self.__sinif        = sinif        or "standart"
        self.__vites        = vites        or "Manuel"
        self.__yakit        = yakit        or "Benzin"
        self.__koltuk       = koltuk       or 5
        self.__puan         = puan         or 4.0
        self.__aciklama     = aciklama     or ""
        self.__gunluk_fiyat = gunluk_fiyat or 0.0
        self.__enlem        = enlem
        self.__boylam       = boylam
        self.__gorsel       = gorsel       or ""
        # durum_arac: 'musait' | 'kirada' | 'bakim'
        if durum_arac:
            self.__durum_arac = durum_arac
        else:
            self.__durum_arac = "musait" if musait_mi else "kirada"

    # — Properties —
    @property
    def arac_id(self):      return self.__arac_id
    @property
    def tur(self):          return self.__tur
    @property
    def marka(self):        return self.__marka
    @property
    def model(self):        return self.__model
    @property
    def kilometre(self):    return self.__kilometre
    @property
    def sinif(self):        return self.__sinif
    @property
    def vites(self):        return self.__vites
    @property
    def yakit(self):        return self.__yakit
    @property
    def koltuk(self):       return self.__koltuk
    @property
    def puan(self):         return self.__puan
    @property
    def durum_arac(self):   return self.__durum_arac
    @property
    def musait_mi(self):    return self.__durum_arac == "musait"
    @property
    def aciklama(self):     return self.__aciklama
    @property
    def gunluk_fiyat(self): return self.__gunluk_fiyat
    @property
    def enlem(self):        return self.__enlem
    @property
    def boylam(self):       return self.__boylam
    @property
    def gorsel(self):       return self.__gorsel

    def arac_turu(self):
        return "Genel Arac"



class Otomobil(Arac):
    def arac_turu(self): return "Otomobil"


class SUV(Arac):
    def arac_turu(self): return "SUV"


def arac_olustur(satir):
    (arac_id, tur, marka, model, km, musait,
     sinif, vites, yakit, koltuk, puan,
     durum_arac, aciklama, gunluk_fiyat, enlem, boylam, gorsel) = satir

    kwargs = dict(
        sinif=sinif, vites=vites, yakit=yakit, koltuk=koltuk,
        puan=puan, durum_arac=durum_arac, aciklama=aciklama,
        gunluk_fiyat=gunluk_fiyat, enlem=enlem, boylam=boylam, gorsel=gorsel,
    )
    if tur == "Otomobil":
        return Otomobil(arac_id, tur, marka, model, km, musait, **kwargs)
    if tur == "SUV":
        return SUV(arac_id, tur, marka, model, km, musait, **kwargs)
    return Arac(arac_id, tur, marka, model, km, musait, **kwargs)


# -------------------------------------------------------
# KULLANICI
# -------------------------------------------------------
class Kullanici:
    def __init__(self, kullanici_id, ad, ehliyet_no, telefon=""):
        self.__kullanici_id = kullanici_id
        self.__ad           = ad
        self.__ehliyet_no   = ehliyet_no
        self.__telefon      = telefon or ""

    @property
    def kullanici_id(self): return self.__kullanici_id
    @property
    def ad(self):           return self.__ad
    @property
    def ehliyet_no(self):   return self.__ehliyet_no
    @property
    def telefon(self):      return self.__telefon


# -------------------------------------------------------
# KİRALAMA
# -------------------------------------------------------
class Kiralama:
    def __init__(self, kiralama_id, arac_id, kullanici_id,
                 arac_bilgisi, kullanici_adi,
                 baslangic_saati, bitis_saati, aktif_mi,
                 toplam_fiyat=None):
        self.__kiralama_id     = kiralama_id
        self.__arac_id         = arac_id
        self.__kullanici_id    = kullanici_id
        self.__arac_bilgisi    = arac_bilgisi
        self.__kullanici_adi   = kullanici_adi
        self.__baslangic_saati = baslangic_saati
        self.__bitis_saati     = bitis_saati
        self.__aktif_mi        = bool(aktif_mi)
        self.__toplam_fiyat    = toplam_fiyat

    @property
    def kiralama_id(self):     return self.__kiralama_id
    @property
    def arac_id(self):         return self.__arac_id
    @property
    def kullanici_id(self):    return self.__kullanici_id
    @property
    def arac_bilgisi(self):    return self.__arac_bilgisi
    @property
    def kullanici_adi(self):   return self.__kullanici_adi
    @property
    def baslangic_saati(self): return self.__baslangic_saati
    @property
    def bitis_saati(self):     return self.__bitis_saati
    @property
    def aktif_mi(self):        return self.__aktif_mi
    @property
    def toplam_fiyat(self):    return self.__toplam_fiyat


# -------------------------------------------------------
# FAVORİ
# -------------------------------------------------------
class Favori:
    def __init__(self, id, kullanici_id, arac_id, tarih):
        self.id           = id
        self.kullanici_id = kullanici_id
        self.arac_id      = arac_id
        self.tarih        = tarih
