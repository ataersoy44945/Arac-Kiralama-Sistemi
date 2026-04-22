# ============================================================
#   database.py  —  Veritabanı Katmanı
#
#   Görev: Sadece SQLite okuma/yazma işlemleri.
#   Kural: İş mantığı (business logic) buraya girmez.
# ============================================================

import hashlib
import sqlite3
from models import arac_olustur, Kullanici, Kiralama


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


class VeriTabani:
    """SQLite veritabanı işlemlerini yönetir."""

    def __init__(self, db_adi="arac_paylasim.db"):
        self.__db_adi = db_adi
        self.__tablolari_olustur()
        self.__migrasyonlari_uygula()
        self.__ornek_veri_yukle()

    # -------------------------------------------------------
    # Yardımcı: bağlantı aç
    # -------------------------------------------------------

    def __baglanti_ac(self):
        conn = sqlite3.connect(self.__db_adi)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # -------------------------------------------------------
    # Tablo kurulumu
    # -------------------------------------------------------

    def __tablolari_olustur(self):
        conn = self.__baglanti_ac()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS araclar (
                arac_id       TEXT PRIMARY KEY,
                tur           TEXT NOT NULL,
                marka         TEXT NOT NULL,
                model         TEXT NOT NULL,
                kilometre     INTEGER DEFAULT 0,
                musait_mi     INTEGER DEFAULT 1,
                sinif         TEXT    DEFAULT 'standart',
                vites         TEXT    DEFAULT 'Manuel',
                yakit         TEXT    DEFAULT 'Benzin',
                koltuk        INTEGER DEFAULT 5,
                puan          REAL    DEFAULT 4.0,
                durum_arac    TEXT    DEFAULT 'musait',
                aciklama      TEXT    DEFAULT '',
                gunluk_fiyat  REAL    DEFAULT 0.0,
                enlem         REAL,
                boylam        REAL,
                gorsel        TEXT    DEFAULT ''
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS kullanicilar (
                kullanici_id  TEXT PRIMARY KEY,
                ad            TEXT NOT NULL,
                ehliyet_no    TEXT NOT NULL,
                kullanici_adi TEXT UNIQUE,
                sifre         TEXT,
                rol           TEXT DEFAULT 'kullanici',
                telefon       TEXT DEFAULT ''
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS kiralamalar (
                kiralama_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                arac_id         TEXT NOT NULL,
                kullanici_id    TEXT NOT NULL,
                baslangic_saati TEXT NOT NULL,
                bitis_saati     TEXT,
                aktif_mi        INTEGER DEFAULT 1,
                toplam_fiyat    REAL,
                FOREIGN KEY (arac_id)      REFERENCES araclar(arac_id),
                FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(kullanici_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS favoriler (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_id TEXT NOT NULL,
                arac_id      TEXT NOT NULL,
                tarih        TEXT NOT NULL,
                UNIQUE (kullanici_id, arac_id),
                FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(kullanici_id),
                FOREIGN KEY (arac_id)      REFERENCES araclar(arac_id)
            )
        """)

        conn.commit()
        conn.close()

    def __migrasyonlari_uygula(self):
        """Eski DB'ye eksik kolonları güvenli şekilde ekler."""
        conn = self.__baglanti_ac()
        cur = conn.cursor()

        migrasyonlar = [
            "ALTER TABLE araclar      ADD COLUMN sinif         TEXT DEFAULT 'standart'",
            "ALTER TABLE araclar      ADD COLUMN vites         TEXT DEFAULT 'Manuel'",
            "ALTER TABLE araclar      ADD COLUMN yakit         TEXT DEFAULT 'Benzin'",
            "ALTER TABLE araclar      ADD COLUMN koltuk        INTEGER DEFAULT 5",
            "ALTER TABLE araclar      ADD COLUMN puan          REAL DEFAULT 4.0",
            "ALTER TABLE araclar      ADD COLUMN durum_arac    TEXT DEFAULT 'musait'",
            "ALTER TABLE araclar      ADD COLUMN aciklama      TEXT DEFAULT ''",
            "ALTER TABLE araclar      ADD COLUMN gunluk_fiyat  REAL DEFAULT 0.0",
            "ALTER TABLE araclar      ADD COLUMN enlem         REAL",
            "ALTER TABLE araclar      ADD COLUMN boylam        REAL",
            "ALTER TABLE kiralamalar  ADD COLUMN toplam_fiyat  REAL",
            "ALTER TABLE kullanicilar ADD COLUMN kullanici_adi TEXT",
            "ALTER TABLE kullanicilar ADD COLUMN sifre         TEXT",
            "ALTER TABLE kullanicilar ADD COLUMN rol           TEXT DEFAULT 'kullanici'",
            "ALTER TABLE kullanicilar ADD COLUMN telefon       TEXT DEFAULT ''",
            "ALTER TABLE araclar      ADD COLUMN gorsel        TEXT DEFAULT ''",
        ]
        for sql in migrasyonlar:
            try:
                cur.execute(sql)
            except sqlite3.OperationalError:
                pass  # kolon zaten var

        conn.commit()
        conn.close()

    # -------------------------------------------------------
    # ARAÇ işlemleri
    # -------------------------------------------------------

    _ARAC_SELECT = """
        SELECT
            arac_id, tur, marka, model, kilometre, musait_mi,
            COALESCE(sinif,        'standart') AS sinif,
            COALESCE(vites,        'Manuel')   AS vites,
            COALESCE(yakit,        'Benzin')   AS yakit,
            COALESCE(koltuk,       5)          AS koltuk,
            COALESCE(puan,         4.0)        AS puan,
            COALESCE(durum_arac,   'musait')   AS durum_arac,
            COALESCE(aciklama,     '')         AS aciklama,
            COALESCE(gunluk_fiyat, 0.0)        AS gunluk_fiyat,
            enlem, boylam,
            COALESCE(gorsel, '')               AS gorsel
        FROM araclar
    """

    def arac_ekle(self, arac_id, tur, marka, model, kilometre, sinif="standart",
                  vites="Manuel", yakit="Benzin", koltuk=5, puan=4.0,
                  aciklama="", gunluk_fiyat=0.0, enlem=None, boylam=None,
                  gorsel=""):
        conn = self.__baglanti_ac()
        conn.cursor().execute("""
            INSERT INTO araclar
                (arac_id, tur, marka, model, kilometre, sinif,
                 vites, yakit, koltuk, puan, durum_arac, aciklama,
                 gunluk_fiyat, enlem, boylam, gorsel)
            VALUES (?,?,?,?,?,?,?,?,?,?,'musait',?,?,?,?,?)
        """, (arac_id, tur, marka, model, kilometre, sinif,
              vites, yakit, koltuk, puan, aciklama,
              gunluk_fiyat, enlem, boylam, gorsel or ""))
        conn.commit()
        conn.close()

    def arac_gorsel_guncelle(self, arac_id: str, gorsel: str):
        conn = self.__baglanti_ac()
        conn.cursor().execute(
            "UPDATE araclar SET gorsel = ? WHERE arac_id = ?",
            (gorsel, arac_id)
        )
        conn.commit()
        conn.close()

    def arac_id_var_mi(self, arac_id):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM araclar WHERE arac_id = ?", (arac_id,))
        sonuc = cur.fetchone() is not None
        conn.close()
        return sonuc

    def arac_getir(self, arac_id):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute(self._ARAC_SELECT + " WHERE arac_id = ?", (arac_id,))
        satir = cur.fetchone()
        conn.close()
        return arac_olustur(satir) if satir else None

    def tum_araclar(self):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute(self._ARAC_SELECT + " ORDER BY sinif, marka, model")
        satirlar = cur.fetchall()
        conn.close()
        return [arac_olustur(s) for s in satirlar]

    def araclari_filtrele(self, tur=None, sinif=None, vites=None, yakit=None,
                          max_km=None, min_puan=None, sadece_musait=True):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        kosullar = []
        params = []
        if sadece_musait:
            kosullar.append("COALESCE(durum_arac,'musait') = 'musait'")
        if tur:
            kosullar.append("tur = ?")
            params.append(tur)
        if sinif:
            kosullar.append("COALESCE(sinif,'standart') = ?")
            params.append(sinif)
        if vites:
            kosullar.append("COALESCE(vites,'Manuel') = ?")
            params.append(vites)
        if yakit:
            kosullar.append("COALESCE(yakit,'Benzin') = ?")
            params.append(yakit)
        if max_km is not None:
            kosullar.append("kilometre <= ?")
            params.append(max_km)
        if min_puan is not None:
            kosullar.append("COALESCE(puan,4.0) >= ?")
            params.append(min_puan)

        where = ("WHERE " + " AND ".join(kosullar)) if kosullar else ""
        cur.execute(self._ARAC_SELECT + f" {where} ORDER BY sinif, marka, model", params)
        satirlar = cur.fetchall()
        conn.close()
        return [arac_olustur(s) for s in satirlar]

    def arac_durumu_guncelle(self, arac_id, musait_mi):
        durum = "musait" if musait_mi else "kirada"
        conn = self.__baglanti_ac()
        conn.cursor().execute(
            "UPDATE araclar SET musait_mi = ?, durum_arac = ? WHERE arac_id = ?",
            (1 if musait_mi else 0, durum, arac_id)
        )
        conn.commit()
        conn.close()

    def arac_durum_degistir(self, arac_id, durum):
        """durum: 'musait' | 'kirada' | 'bakim'"""
        musait = 1 if durum == "musait" else 0
        conn = self.__baglanti_ac()
        conn.cursor().execute(
            "UPDATE araclar SET musait_mi = ?, durum_arac = ? WHERE arac_id = ?",
            (musait, durum, arac_id)
        )
        conn.commit()
        conn.close()

    def arac_kilometre_guncelle(self, arac_id, ek_km):
        conn = self.__baglanti_ac()
        conn.cursor().execute(
            "UPDATE araclar SET kilometre = kilometre + ? WHERE arac_id = ?",
            (ek_km, arac_id)
        )
        conn.commit()
        conn.close()

    def arac_sil(self, arac_id):
        conn = self.__baglanti_ac()
        conn.cursor().execute("DELETE FROM araclar WHERE arac_id = ?", (arac_id,))
        conn.commit()
        conn.close()

    # -------------------------------------------------------
    # KULLANICI işlemleri
    # -------------------------------------------------------

    def kullanici_ekle(self, kullanici_id, ad, ehliyet_no,
                       kullanici_adi=None, sifre=None, rol="kullanici",
                       telefon=""):
        conn = self.__baglanti_ac()
        conn.cursor().execute("""
            INSERT INTO kullanicilar
                (kullanici_id, ad, ehliyet_no, kullanici_adi, sifre, rol, telefon)
            VALUES (?,?,?,?,?,?,?)
        """, (kullanici_id, ad, ehliyet_no, kullanici_adi,
              _hash(sifre) if sifre else None, rol, telefon or ""))
        conn.commit()
        conn.close()

    def sonraki_kullanici_id(self) -> str:
        """K1, K2, … serisi için bir sonraki kullanılmayan ID'yi döndürür."""
        conn = self.__baglanti_ac()
        cur  = conn.cursor()
        cur.execute("SELECT kullanici_id FROM kullanicilar WHERE kullanici_id LIKE 'K%'")
        mevcutlar = {r[0] for r in cur.fetchall()}
        conn.close()
        i = 1
        while f"K{i}" in mevcutlar:
            i += 1
        return f"K{i}"

    def kullanici_adi_var_mi(self, kullanici_adi: str) -> bool:
        conn = self.__baglanti_ac()
        cur  = conn.cursor()
        cur.execute("SELECT 1 FROM kullanicilar WHERE kullanici_adi = ?", (kullanici_adi,))
        sonuc = cur.fetchone() is not None
        conn.close()
        return sonuc

    def kullanici_id_var_mi(self, kullanici_id):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM kullanicilar WHERE kullanici_id = ?", (kullanici_id,))
        sonuc = cur.fetchone() is not None
        conn.close()
        return sonuc

    def kullanici_getir(self, kullanici_id):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute(
            "SELECT kullanici_id, ad, ehliyet_no, COALESCE(telefon,'') FROM kullanicilar"
            " WHERE kullanici_id = ?",
            (kullanici_id,)
        )
        satir = cur.fetchone()
        conn.close()
        return Kullanici(*satir) if satir else None

    def tum_kullanicilar(self):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute(
            "SELECT kullanici_id, ad, ehliyet_no, COALESCE(telefon,'') FROM kullanicilar"
            " ORDER BY ad"
        )
        satirlar = cur.fetchall()
        conn.close()
        return [Kullanici(*s) for s in satirlar]

    def kullanici_dogrula(self, kullanici_adi, sifre):
        """
        Giriş doğrulama. Başarılıysa (True, satir_dict), hatalıysa (False, None).
        satir_dict: kullanici_id, kullanici_adi, ad, rol
        """
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute("""
            SELECT kullanici_id, kullanici_adi, ad, rol
            FROM kullanicilar
            WHERE kullanici_adi = ? AND sifre = ?
        """, (kullanici_adi, _hash(sifre)))
        satir = cur.fetchone()
        conn.close()
        if satir:
            return True, {
                "kullanici_id":  satir[0],
                "kullanici_adi": satir[1],
                "ad":            satir[2],
                "rol":           satir[3],
            }
        return False, None

    def kullanici_guncelle_auth(self, kullanici_id, kullanici_adi, sifre, rol="kullanici"):
        """Mevcut kullanıcıya kullanici_adi/sifre/rol atar (migrasyon için)."""
        conn = self.__baglanti_ac()
        conn.cursor().execute("""
            UPDATE kullanicilar
            SET kullanici_adi = ?, sifre = ?, rol = ?
            WHERE kullanici_id = ?
        """, (kullanici_adi, _hash(sifre), rol, kullanici_id))
        conn.commit()
        conn.close()

    # -------------------------------------------------------
    # KİRALAMA işlemleri
    # -------------------------------------------------------

    def kiralama_ekle(self, arac_id, kullanici_id, baslangic_saati):
        conn = self.__baglanti_ac()
        conn.cursor().execute(
            "INSERT INTO kiralamalar (arac_id, kullanici_id, baslangic_saati) VALUES (?,?,?)",
            (arac_id, kullanici_id, baslangic_saati)
        )
        conn.commit()
        conn.close()

    def aktif_kiralama_getir(self, arac_id):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute("""
            SELECT k.kiralama_id, k.arac_id, k.kullanici_id,
                   a.marka || ' ' || a.model,
                   ku.ad,
                   k.baslangic_saati, k.bitis_saati, k.aktif_mi, k.toplam_fiyat
            FROM kiralamalar k
            JOIN araclar      a  ON k.arac_id      = a.arac_id
            JOIN kullanicilar ku ON k.kullanici_id = ku.kullanici_id
            WHERE k.arac_id = ? AND k.aktif_mi = 1
        """, (arac_id,))
        satir = cur.fetchone()
        conn.close()
        return Kiralama(*satir) if satir else None

    def kullanici_aktif_kiralama_var_mi(self, kullanici_id):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM kiralamalar WHERE kullanici_id = ? AND aktif_mi = 1",
            (kullanici_id,)
        )
        sonuc = cur.fetchone() is not None
        conn.close()
        return sonuc

    def kiralama_bitir(self, arac_id, bitis_saati, toplam_fiyat=None):
        conn = self.__baglanti_ac()
        conn.cursor().execute("""
            UPDATE kiralamalar
            SET bitis_saati = ?, aktif_mi = 0, toplam_fiyat = ?
            WHERE arac_id = ? AND aktif_mi = 1
        """, (bitis_saati, toplam_fiyat, arac_id))
        conn.commit()
        conn.close()

    def kiralama_iptal(self, kiralama_id):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute(
            "SELECT arac_id FROM kiralamalar WHERE kiralama_id = ? AND aktif_mi = 1",
            (kiralama_id,)
        )
        satir = cur.fetchone()
        if satir:
            cur.execute(
                "UPDATE kiralamalar SET aktif_mi = 0 WHERE kiralama_id = ?",
                (kiralama_id,)
            )
            cur.execute(
                "UPDATE araclar SET musait_mi = 1, durum_arac = 'musait' WHERE arac_id = ?",
                (satir[0],)
            )
        conn.commit()
        conn.close()
        return satir is not None

    def tum_aktif_kiralamalar(self):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute("""
            SELECT k.kiralama_id, k.arac_id, k.kullanici_id,
                   a.marka || ' ' || a.model,
                   ku.ad,
                   k.baslangic_saati, k.bitis_saati, k.aktif_mi, k.toplam_fiyat
            FROM kiralamalar k
            JOIN araclar      a  ON k.arac_id      = a.arac_id
            JOIN kullanicilar ku ON k.kullanici_id = ku.kullanici_id
            WHERE k.aktif_mi = 1
            ORDER BY k.baslangic_saati DESC
        """)
        satirlar = cur.fetchall()
        conn.close()
        return [Kiralama(*s) for s in satirlar]

    def tum_kiralamalar(self):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute("""
            SELECT k.kiralama_id, k.arac_id, k.kullanici_id,
                   a.marka || ' ' || a.model,
                   ku.ad,
                   k.baslangic_saati, k.bitis_saati, k.aktif_mi, k.toplam_fiyat
            FROM kiralamalar k
            JOIN araclar      a  ON k.arac_id      = a.arac_id
            JOIN kullanicilar ku ON k.kullanici_id = ku.kullanici_id
            ORDER BY k.kiralama_id DESC
        """)
        satirlar = cur.fetchall()
        conn.close()
        return [Kiralama(*s) for s in satirlar]

    def kullanici_kiralamalari(self, kullanici_id):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute("""
            SELECT k.kiralama_id, k.arac_id, k.kullanici_id,
                   a.marka || ' ' || a.model,
                   ku.ad,
                   k.baslangic_saati, k.bitis_saati, k.aktif_mi, k.toplam_fiyat
            FROM kiralamalar k
            JOIN araclar      a  ON k.arac_id      = a.arac_id
            JOIN kullanicilar ku ON k.kullanici_id = ku.kullanici_id
            WHERE k.kullanici_id = ?
            ORDER BY k.kiralama_id DESC
        """, (kullanici_id,))
        satirlar = cur.fetchall()
        conn.close()
        return [Kiralama(*s) for s in satirlar]

    def kullanici_harcama_toplamlari(self) -> dict:
        """Her kullanıcının tamamlanmış kiralamalardan toplam harcamasını döndürür.
        {kullanici_id: toplam_fiyat} şeklinde dict."""
        conn = self.__baglanti_ac()
        cur  = conn.cursor()
        cur.execute("""
            SELECT kullanici_id, COALESCE(SUM(toplam_fiyat), 0)
            FROM kiralamalar
            WHERE aktif_mi = 0 AND toplam_fiyat IS NOT NULL
            GROUP BY kullanici_id
        """)
        sonuc = {satir[0]: satir[1] for satir in cur.fetchall()}
        conn.close()
        return sonuc

    def kullanici_telefon_guncelle(self, kullanici_id: str, telefon: str):
        conn = self.__baglanti_ac()
        conn.cursor().execute(
            "UPDATE kullanicilar SET telefon = ? WHERE kullanici_id = ?",
            (telefon, kullanici_id)
        )
        conn.commit()
        conn.close()

    # -------------------------------------------------------
    # FAVORİ işlemleri
    # -------------------------------------------------------

    def favori_ekle(self, kullanici_id, arac_id, tarih):
        conn = self.__baglanti_ac()
        try:
            conn.cursor().execute(
                "INSERT INTO favoriler (kullanici_id, arac_id, tarih) VALUES (?,?,?)",
                (kullanici_id, arac_id, tarih)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # zaten favori
        finally:
            conn.close()

    def favori_kaldir(self, kullanici_id, arac_id):
        conn = self.__baglanti_ac()
        conn.cursor().execute(
            "DELETE FROM favoriler WHERE kullanici_id = ? AND arac_id = ?",
            (kullanici_id, arac_id)
        )
        conn.commit()
        conn.close()

    def favori_var_mi(self, kullanici_id, arac_id):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM favoriler WHERE kullanici_id = ? AND arac_id = ?",
            (kullanici_id, arac_id)
        )
        sonuc = cur.fetchone() is not None
        conn.close()
        return sonuc

    def favori_araclari(self, kullanici_id):
        """Favori araçları Arac nesnesi olarak döndürür."""
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        # JOIN sorgusunda arac_id iki tabloda da var; tablo takma adı zorunlu.
        cur.execute("""
            SELECT
                a.arac_id, a.tur, a.marka, a.model, a.kilometre, a.musait_mi,
                COALESCE(a.sinif,        'standart') AS sinif,
                COALESCE(a.vites,        'Manuel')   AS vites,
                COALESCE(a.yakit,        'Benzin')   AS yakit,
                COALESCE(a.koltuk,       5)          AS koltuk,
                COALESCE(a.puan,         4.0)        AS puan,
                COALESCE(a.durum_arac,   'musait')   AS durum_arac,
                COALESCE(a.aciklama,     '')         AS aciklama,
                COALESCE(a.gunluk_fiyat, 0.0)        AS gunluk_fiyat,
                a.enlem, a.boylam,
                COALESCE(a.gorsel, '')               AS gorsel
            FROM araclar a
            JOIN favoriler f ON a.arac_id = f.arac_id
            WHERE f.kullanici_id = ?
            ORDER BY f.tarih DESC
        """, (kullanici_id,))
        satirlar = cur.fetchall()
        conn.close()
        return [arac_olustur(s) for s in satirlar]

    # -------------------------------------------------------
    # Dashboard özet
    # -------------------------------------------------------

    def dashboard_ozet(self):
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM araclar")
        toplam_arac = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM araclar WHERE COALESCE(durum_arac,'musait') = 'musait'")
        musait_arac = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM kullanicilar WHERE rol = 'kullanici'")
        toplam_kullanici = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM kiralamalar WHERE aktif_mi = 1")
        aktif_kiralama = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(toplam_fiyat),0) FROM kiralamalar WHERE aktif_mi = 0")
        toplam_gelir = cur.fetchone()[0]
        conn.close()
        return {
            "toplam_arac":      toplam_arac,
            "musait_arac":      musait_arac,
            "kirada_arac":      toplam_arac - musait_arac,
            "toplam_kullanici": toplam_kullanici,
            "aktif_kiralama":   aktif_kiralama,
            "toplam_gelir":     round(toplam_gelir, 2),
        }

    # -------------------------------------------------------
    # Başlangıç verisi
    # -------------------------------------------------------

    def __ornek_veri_yukle(self):
        """Veritabanı boşsa 20 araç + kullanıcı + admin ekler."""
        if self.tum_araclar():
            self.__auth_guncelle_eski()
            return

        # ---------- ECO ----------
        self.arac_ekle("E1", "Otomobil", "Renault", "Clio",    12000, "eco",
                        vites="Manuel",    yakit="Benzin", koltuk=5, puan=4.1,
                        aciklama="Sehir ici ideal, dusuk yakit tuketen kompakt.",
                        gunluk_fiyat=150*24, enlem=41.0082, boylam=28.9784)   # Besiktas
        self.arac_ekle("E2", "Otomobil", "Renault", "Symbol",  18000, "eco",
                        vites="Manuel",    yakit="Benzin", koltuk=5, puan=3.9,
                        aciklama="Ekonomik ve guvenilir sedan.",
                        gunluk_fiyat=150*24, enlem=40.9903, boylam=29.0299)   # Kadikoy
        self.arac_ekle("E3", "Otomobil", "Fiat",    "Egea",    9500,  "eco",
                        vites="Otomatik",  yakit="Dizel",  koltuk=5, puan=4.3,
                        aciklama="Konforlu ic mekan, genis bagaj.",
                        gunluk_fiyat=150*24, enlem=41.0601, boylam=28.9877)   # Sisli
        self.arac_ekle("E4", "Otomobil", "Hyundai", "i20",     21000, "eco",
                        vites="Manuel",    yakit="Benzin", koltuk=5, puan=4.0,
                        aciklama="Modern tasarim, guvenli surunum.",
                        gunluk_fiyat=150*24, enlem=40.9795, boylam=28.8688)   # Bakirkoy
        self.arac_ekle("E5", "Otomobil", "Dacia",   "Sandero", 33000, "eco",
                        vites="Manuel",    yakit="Benzin", koltuk=5, puan=3.7,
                        aciklama="Butce dostu, pratik sehir araci.",
                        gunluk_fiyat=150*24, enlem=41.0232, boylam=29.0151)   # Uskudar

        # ---------- STANDART ----------
        self.arac_ekle("S1", "Otomobil", "Peugeot", "308",     27000, "standart",
                        vites="Otomatik", yakit="Dizel",  koltuk=5, puan=4.4,
                        aciklama="Avrupa lezzetli surucululuk deneyimi.",
                        gunluk_fiyat=250*24, enlem=40.9921, boylam=29.1046)   # Atasehir
        self.arac_ekle("S2", "Otomobil", "Seat",    "Leon",    15000, "standart",
                        vites="Otomatik", yakit="Benzin", koltuk=5, puan=4.5,
                        aciklama="Sportif tasarim, dinamik surunum.",
                        gunluk_fiyat=250*24, enlem=41.1663, boylam=29.0542)   # Sariyer
        self.arac_ekle("S3", "Otomobil", "VW",      "Golf",    8700,  "standart",
                        vites="Otomatik", yakit="Benzin", koltuk=5, puan=4.6,
                        aciklama="Kaliteli ic mekan, uzun yol konforu.",
                        gunluk_fiyat=250*24, enlem=40.8895, boylam=29.1880)   # Kartal
        self.arac_ekle("S4", "Otomobil", "Toyota",  "Corolla", 42000, "standart",
                        vites="Otomatik", yakit="Hibrit", koltuk=5, puan=4.3,
                        aciklama="Hibrit teknoloji, dusuk emisyon.",
                        gunluk_fiyat=250*24, enlem=41.0082, boylam=28.9784)   # Besiktas
        self.arac_ekle("S5", "Otomobil", "Honda",   "Civic",   19500, "standart",
                        vites="Manuel",   yakit="Benzin", koltuk=5, puan=4.2,
                        aciklama="Sporif kokpit, guvenilir motor.",
                        gunluk_fiyat=250*24, enlem=40.9903, boylam=29.0299)   # Kadikoy

        # ---------- PREMİUM ----------
        self.arac_ekle("P1", "Otomobil", "BMW",      "3 Serisi",  11000, "premium",
                        vites="Otomatik", yakit="Benzin", koltuk=5, puan=4.7,
                        aciklama="Sportif surucululuk, premium malzeme.",
                        gunluk_fiyat=400*24, enlem=41.0601, boylam=28.9877)   # Sisli
        self.arac_ekle("P2", "Otomobil", "Audi",     "A4",        23000, "premium",
                        vites="Otomatik", yakit="Dizel",  koltuk=5, puan=4.8,
                        aciklama="Quattro cekis, ustsun yol tutusu.",
                        gunluk_fiyat=400*24, enlem=40.9795, boylam=28.8688)   # Bakirkoy
        self.arac_ekle("P3", "Otomobil", "Mercedes", "C Serisi",   7500, "premium",
                        vites="Otomatik", yakit="Benzin", koltuk=5, puan=4.9,
                        aciklama="Luks ic mekan, cok sayida surucututucu.",
                        gunluk_fiyat=400*24, enlem=41.0232, boylam=29.0151)   # Uskudar
        self.arac_ekle("P4", "Otomobil", "Volvo",    "S60",       16000, "premium",
                        vites="Otomatik", yakit="Hibrit", koltuk=5, puan=4.6,
                        aciklama="Skandinav tasarimi, en guclu guvenlik donanimi.",
                        gunluk_fiyat=400*24, enlem=40.9921, boylam=29.1046)   # Atasehir
        self.arac_ekle("P5", "Otomobil", "Skoda",    "Superb",    31000, "premium",
                        vites="Otomatik", yakit="Dizel",  koltuk=5, puan=4.5,
                        aciklama="Cok genis i mekan, birinci sinif yolculuk.",
                        gunluk_fiyat=400*24, enlem=41.1663, boylam=29.0542)   # Sariyer

        # ---------- VIP ----------
        self.arac_ekle("V1", "SUV",      "Mercedes", "Vito",       4500, "vip",
                        vites="Otomatik", yakit="Dizel",  koltuk=8, puan=4.9,
                        aciklama="VIP transfer araci, 8 kisilik luks koltuk.",
                        gunluk_fiyat=750*24, enlem=40.8895, boylam=29.1880)   # Kartal
        self.arac_ekle("V2", "Otomobil", "BMW",      "5 Serisi",   9200, "vip",
                        vites="Otomatik", yakit="Benzin", koltuk=5, puan=4.8,
                        aciklama="Yonetici sinifi sedan, suruculu secenegi.",
                        gunluk_fiyat=750*24, enlem=41.0082, boylam=28.9784)   # Besiktas
        self.arac_ekle("V3", "Otomobil", "Audi",     "A6",        13000, "vip",
                        vites="Otomatik", yakit="Hibrit", koltuk=5, puan=4.9,
                        aciklama="Prestijli ic mekan, diger araclara gore oncelikli park.",
                        gunluk_fiyat=750*24, enlem=40.9903, boylam=29.0299)   # Kadikoy
        self.arac_ekle("V4", "Otomobil", "Mercedes", "E Serisi",   6800, "vip",
                        vites="Otomatik", yakit="Benzin", koltuk=5, puan=4.9,
                        aciklama="Amiral gemisi konfor, hava askisi.",
                        gunluk_fiyat=750*24, enlem=41.0601, boylam=28.9877)   # Sisli
        self.arac_ekle("V5", "Otomobil", "Maserati", "Ghibli",     3200, "vip",
                        vites="Otomatik", yakit="Benzin", koltuk=5, puan=5.0,
                        aciklama="Italyan heyecani, esiz surucululuk zevki.",
                        gunluk_fiyat=750*24, enlem=40.9795, boylam=28.8688)   # Bakirkoy

        # ---------- Kullanıcılar ----------
        self.kullanici_ekle("K1", "Ata Ersoy",   "B12345",
                            kullanici_adi="ata",   sifre="1234")
        self.kullanici_ekle("K2", "Cem Kaya",    "B23456",
                            kullanici_adi="cem",  sifre="1234")
        self.kullanici_ekle("K3", "Beyto Özen",  "B34567",
                            kullanici_adi="beyto", sifre="1234")
        self.kullanici_ekle("K4", "Dença Diktaş", "B1",
                            kullanici_adi="denca", sifre="1234")

        # ---------- Admin ----------
        self.kullanici_ekle("A0", "Admin",        "ADMIN-000",
                            kullanici_adi="admin", sifre="1234", rol="admin")

    def __auth_guncelle_eski(self):
        """Eski DB'deki K1-K3 kayıtlarına kullanici_adi/sifre ekler (yoksa)."""
        conn = self.__baglanti_ac()
        cur = conn.cursor()
        cur.execute("SELECT kullanici_adi FROM kullanicilar WHERE kullanici_id = 'K1'")
        satir = cur.fetchone()
        conn.close()
        if satir and satir[0]:
            return  # zaten güncel

        self.kullanici_guncelle_auth("K1", "ata",    "1234", "kullanici")
        self.kullanici_guncelle_auth("K2", "cem",   "1234", "kullanici")
        self.kullanici_guncelle_auth("K3", "beyto", "1234", "kullanici")

        # Admin yoksa ekle
        conn2 = self.__baglanti_ac()
        cur2 = conn2.cursor()
        cur2.execute("SELECT 1 FROM kullanicilar WHERE kullanici_id = 'A0'")
        if not cur2.fetchone():
            conn2.close()
            self.kullanici_ekle("A0", "Admin", "ADMIN-000",
                                kullanici_adi="admin", sifre="1234", rol="admin")
        else:
            conn2.close()
