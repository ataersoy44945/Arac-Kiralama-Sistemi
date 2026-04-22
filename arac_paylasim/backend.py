# ============================================================
#   backend.py  —  İş Mantığı Katmanı (Business Logic)
#
#   Görev: Sistem kurallarını uygular.
#   Kural: Konsol yazdırma (print) buraya girmez.
#          Veritabanına doğrudan bağlanmaz, database.py kullanır.
# ============================================================

from datetime import datetime
from database import VeriTabani
from models   import Hesap
from pricing  import fiyat_hesapla, SINIF_LISTESI, SINIF_FIYAT


class Backend:
    """İş mantığını yönetir. Kuralları kontrol eder, database.py ile konuşur."""

    def __init__(self):
        self.__db = VeriTabani()

    # -------------------------------------------------------
    # AUTH
    # -------------------------------------------------------

    def giris_yap(self, kullanici_adi: str, sifre: str):
        """
        Kullanıcı girişi.
        Başarılıysa (True, Hesap), hatalıysa (False, hata_str) döndürür.
        """
        if not kullanici_adi or not sifre:
            return False, "Kullanici adi ve sifre bos birakilamaz!"
        ok, veri = self.__db.kullanici_dogrula(kullanici_adi, sifre)
        if not ok:
            return False, "Kullanici adi veya sifre yanlis!"
        hesap = Hesap(
            kullanici_id=veri["kullanici_id"],
            kullanici_adi=veri["kullanici_adi"],
            ad=veri["ad"],
            rol=veri["rol"],
        )
        return True, hesap

    # -------------------------------------------------------
    # ARAÇ işlemleri
    # -------------------------------------------------------

    def arac_ekle(self, arac_id, tur, marka, model, kilometre, sinif="standart",
                  vites="Manuel", yakit="Benzin", koltuk=5, puan=4.0,
                  aciklama="", gunluk_fiyat=0.0, enlem=None, boylam=None,
                  gorsel=""):
        if not arac_id or not marka or not model:
            return False, "Arac ID, marka ve model bos birakilamaz!"
        if tur not in ("Otomobil", "SUV"):
            return False, "Gecersiz arac turu!"
        if sinif not in SINIF_LISTESI:
            return False, f"Gecersiz sinif! Gecerliler: {', '.join(SINIF_LISTESI)}"
        if self.__db.arac_id_var_mi(arac_id):
            return False, f"'{arac_id}' ID'li arac zaten mevcut!"
        if kilometre < 0:
            return False, "Kilometre negatif olamaz!"

        self.__db.arac_ekle(arac_id, tur, marka, model, kilometre, sinif,
                            vites, yakit, koltuk, puan, aciklama,
                            gunluk_fiyat, enlem, boylam, gorsel)
        return True, f"'{marka} {model}' ({tur} / {sinif}) basariyla eklendi."

    def araclari_getir(self):
        return self.__db.tum_araclar()

    def musait_araclari_getir(self):
        return [a for a in self.__db.tum_araclar() if a.musait_mi]

    def araclari_filtrele(self, tur=None, sinif=None, vites=None, yakit=None,
                          max_km=None, min_puan=None, sadece_musait=True):
        return self.__db.araclari_filtrele(
            tur=tur, sinif=sinif, vites=vites, yakit=yakit,
            max_km=max_km, min_puan=min_puan, sadece_musait=sadece_musait
        )

    def arac_durum_degistir(self, arac_id, durum):
        """durum: 'musait' | 'kirada' | 'bakim'"""
        if durum not in ("musait", "kirada", "bakim"):
            return False, "Gecersiz durum! (musait / kirada / bakim)"
        arac = self.__db.arac_getir(arac_id)
        if not arac:
            return False, f"'{arac_id}' ID'li arac bulunamadi!"
        self.__db.arac_durum_degistir(arac_id, durum)
        return True, f"'{arac.marka} {arac.model}' durumu '{durum}' olarak guncellendi."

    def arac_sil(self, arac_id):
        arac = self.__db.arac_getir(arac_id)
        if not arac:
            return False, f"'{arac_id}' ID'li arac bulunamadi!"
        if not arac.musait_mi:
            return False, "Kirada olan arac silinemez!"
        self.__db.arac_sil(arac_id)
        return True, f"'{arac.marka} {arac.model}' silindi."

    # -------------------------------------------------------
    # KULLANICI işlemleri
    # -------------------------------------------------------

    def kullanici_ekle(self, kullanici_id, ad, ehliyet_no,
                       kullanici_adi=None, sifre=None):
        if not kullanici_id or not ad or not ehliyet_no:
            return False, "Tum alanlar doldurulmalidir!"
        if self.__db.kullanici_id_var_mi(kullanici_id):
            return False, f"'{kullanici_id}' ID'li kullanici zaten mevcut!"

        self.__db.kullanici_ekle(kullanici_id, ad, ehliyet_no,
                                 kullanici_adi, sifre)
        return True, f"'{ad}' basariyla sisteme eklendi."

    def kullanicilari_getir(self):
        return self.__db.tum_kullanicilar()

    def kullanici_harcama_toplamlari(self):
        return self.__db.kullanici_harcama_toplamlari()

    def kullanici_kayit(self, ad, kullanici_adi, ehliyet_no, telefon, sifre):
        """
        Yeni kullanıcı kaydı. ID otomatik üretilir.
        Başarılıysa (True, yeni_id), hatalıysa (False, hata) döndürür.
        """
        ad            = ad.strip()
        kullanici_adi = kullanici_adi.strip()
        ehliyet_no    = ehliyet_no.strip()
        telefon       = telefon.strip()

        if not all([ad, kullanici_adi, ehliyet_no, telefon, sifre]):
            return False, "Tüm alanlar doldurulmalıdır!"
        if len(sifre) < 4:
            return False, "Şifre en az 4 karakter olmalıdır!"
        if self.__db.kullanici_adi_var_mi(kullanici_adi):
            return False, f"'{kullanici_adi}' kullanıcı adı zaten alınmış!"

        yeni_id = self.__db.sonraki_kullanici_id()
        self.__db.kullanici_ekle(yeni_id, ad, ehliyet_no, kullanici_adi, sifre,
                                 telefon=telefon)
        return True, yeni_id

    # -------------------------------------------------------
    # KİRALAMA işlemleri
    # -------------------------------------------------------

    def kiralama_baslat(self, arac_id, kullanici_id):
        arac = self.__db.arac_getir(arac_id)
        if not arac:
            return False, f"'{arac_id}' ID'li arac bulunamadi!"
        if not arac.musait_mi:
            return False, f"'{arac.marka} {arac.model}' su an musait degil!"

        kullanici = self.__db.kullanici_getir(kullanici_id)
        if not kullanici:
            return False, f"'{kullanici_id}' ID'li kullanici bulunamadi!"
        if self.__db.kullanici_aktif_kiralama_var_mi(kullanici_id):
            return False, f"'{kullanici.ad}' adli kullanicinin zaten aktif kiralamasi var!"

        baslangic = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__db.kiralama_ekle(arac_id, kullanici_id, baslangic)
        self.__db.arac_durumu_guncelle(arac_id, False)

        saatlik = SINIF_FIYAT.get(arac.sinif, 0)

        return True, {
            "arac_turu"  : arac.arac_turu(),
            "arac"       : f"{arac.marka} {arac.model}",
            "sinif"      : arac.sinif,
            "saatlik"    : saatlik,
            "kullanici"  : kullanici.ad,
            "baslangic"  : baslangic,
        }

    def kiralama_bitir(self, arac_id, ek_km):
        kiralama = self.__db.aktif_kiralama_getir(arac_id)
        if not kiralama:
            return False, f"'{arac_id}' ID'li arac icin aktif kiralama bulunamadi!"

        if ek_km < 0:
            ek_km = 0

        bitis     = datetime.now()
        bitis_str = bitis.strftime("%Y-%m-%d %H:%M:%S")
        baslangic = datetime.strptime(kiralama.baslangic_saati, "%Y-%m-%d %H:%M:%S")
        sure      = bitis - baslangic
        dakika    = int(sure.total_seconds() // 60)

        arac = self.__db.arac_getir(arac_id)
        ok, fiyat_sonuc = fiyat_hesapla(arac.sinif, kiralama.baslangic_saati, bitis_str)
        toplam_fiyat    = fiyat_sonuc["toplam_fiyat"] if ok else None

        self.__db.kiralama_bitir(arac_id, bitis_str, toplam_fiyat)
        self.__db.arac_durumu_guncelle(arac_id, True)
        self.__db.arac_kilometre_guncelle(arac_id, ek_km)

        arac = self.__db.arac_getir(arac_id)

        return True, {
            "arac"         : f"{arac.marka} {arac.model}",
            "sinif"        : arac.sinif,
            "kullanici"    : kiralama.kullanici_adi,
            "bitis"        : bitis_str,
            "dakika"       : dakika,
            "ek_km"        : ek_km,
            "yeni_km"      : arac.kilometre,
            "fiyat_detay"  : fiyat_sonuc if ok else None,
            "toplam_fiyat" : toplam_fiyat,
        }

    def kiralama_iptal(self, kiralama_id):
        ok = self.__db.kiralama_iptal(kiralama_id)
        if not ok:
            return False, f"#{kiralama_id} no'lu aktif kiralama bulunamadi!"
        return True, f"#{kiralama_id} no'lu kiralama iptal edildi."

    def aktif_kiralamalar(self):
        return self.__db.tum_aktif_kiralamalar()

    def tum_kiralamalar(self):
        return self.__db.tum_kiralamalar()

    def kullanici_kiralama_gecmisi(self, kullanici_id):
        if not self.__db.kullanici_id_var_mi(kullanici_id):
            return False, f"'{kullanici_id}' ID'li kullanici bulunamadi!"
        kullanici   = self.__db.kullanici_getir(kullanici_id)
        kiralamalar = self.__db.kullanici_kiralamalari(kullanici_id)
        return True, {"kullanici": kullanici, "kiralamalar": kiralamalar}

    def kullanici_telefon_guncelle(self, kullanici_id: str, telefon: str):
        """Kullanıcının telefon numarasını günceller."""
        telefon = telefon.strip()
        if not telefon:
            return False, "Telefon numarası boş bırakılamaz!"
        self.__db.kullanici_telefon_guncelle(kullanici_id, telefon)
        return True, "Telefon numarası güncellendi."

    # -------------------------------------------------------
    # FAVORİ işlemleri
    # -------------------------------------------------------

    def favori_ekle(self, kullanici_id, arac_id):
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__db.favori_ekle(kullanici_id, arac_id, tarih)
        return True, "Favorilere eklendi."

    def favori_kaldir(self, kullanici_id, arac_id):
        self.__db.favori_kaldir(kullanici_id, arac_id)
        return True, "Favorilerden kaldirildi."

    def favori_toggle(self, kullanici_id, arac_id):
        if self.__db.favori_var_mi(kullanici_id, arac_id):
            return self.favori_kaldir(kullanici_id, arac_id)
        return self.favori_ekle(kullanici_id, arac_id)

    def favori_var_mi(self, kullanici_id, arac_id):
        return self.__db.favori_var_mi(kullanici_id, arac_id)

    def kullanici_favorileri(self, kullanici_id):
        return self.__db.favori_araclari(kullanici_id)

    # -------------------------------------------------------
    # Dashboard / Admin
    # -------------------------------------------------------

    def dashboard_verileri(self):
        return self.__db.dashboard_ozet()

    def fiyat_on_izle(self, sinif, baslangic_str, bitis_str):
        """Kiralama öncesi fiyat önizlemesi. (True, detay_dict) veya (False, hata)."""
        return fiyat_hesapla(sinif, baslangic_str, bitis_str)
