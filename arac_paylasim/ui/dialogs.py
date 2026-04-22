# ============================================================
#   ui/dialogs.py — Paylaşımlı Diyaloglar (Premium UI)
# ============================================================

import os
import tempfile
import webbrowser

from PyQt6.QtCore    import Qt, QDateTime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QDateTimeEdit, QTextEdit, QMessageBox,
    QScrollArea, QWidget,
)
from PyQt6.QtGui import QFont, QPixmap

from pricing           import fiyat_ozeti, SINIF_FIYAT
from ui.components     import RoundedImageWidget, gorsel_bul

# ── Renk Paleti (user_panel ile tam uyumlu) ─────────────────
CARD    = "#ffffff"
BG      = "#f4f6ff"
PRIMARY = "#6366f1"
PRIM2   = "#8b5cf6"
TEXT    = "#0f172a"
MUTED   = "#64748b"
BORDER  = "#e2e8f0"
ACCENT  = "#eef2ff"
SUCCESS = "#10b981"
DANGER  = "#ef4444"

_SINIF_RENK = {
    "eco":      "#10b981",
    "standart": "#6366f1",
    "premium":  "#8b5cf6",
    "vip":      "#f59e0b",
}


# ── Yardımcılar ──────────────────────────────────────────────
def _lbl(text, bold=False, size=13, color=TEXT):
    lbl = QLabel(text)
    f   = QFont("Segoe UI", size)
    if bold:
        f.setWeight(QFont.Weight.Bold)
    lbl.setFont(f)
    lbl.setStyleSheet(f"color:{color}; background:transparent;")
    return lbl


def _sep():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFixedHeight(1)
    line.setStyleSheet(f"background:{BORDER}; border:none;")
    return line



# ============================================================
#   ARAÇ DETAY DİYALOGU
# ============================================================
class AracDetayDiyalogu(QDialog):
    """
    Araç detay penceresi — büyük görsel + premium bilgi düzeni.
    Kullanıcı buradan kiralama başlatabilir veya favorilere ekleyebilir.
    """

    KIRALA_CODE = 10

    def __init__(self, arac, backend, hesap, parent=None):
        super().__init__(parent)
        self.arac    = arac
        self.backend = backend
        self.hesap   = hesap

        self.setWindowTitle(f"{arac.marka} {arac.model} — Detay")
        self.setMinimumWidth(580)
        self.setMaximumWidth(660)
        self.setStyleSheet(f"background:{CARD}; color:{TEXT};")

        sinif      = arac.sinif.lower()
        sinif_renk = _SINIF_RENK.get(sinif, PRIMARY)
        durum_ok   = arac.musait_mi

        ana = QVBoxLayout(self)
        ana.setContentsMargins(0, 0, 0, 0)
        ana.setSpacing(0)

        # ── Araç Görseli (üst) ──────────────────────────────
        path = gorsel_bul(arac)
        px   = QPixmap(path) if path else None

        if px and not px.isNull():
            img_widget = RoundedImageWidget(px, radius=0, fixed_height=230)
            ana.addWidget(img_widget)
        else:
            # Sınıfa göre degradeli fallback banner
            banner = QFrame()
            banner.setFixedHeight(140)
            banner.setStyleSheet(
                f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                f"stop:0 {sinif_renk}22, stop:1 {sinif_renk}55);"
                f"border:none;"
            )
            b_lay = QVBoxLayout(banner)
            b_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            car_ico = QLabel("🚗")
            car_ico.setFont(QFont("Segoe UI", 52))
            car_ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
            car_ico.setStyleSheet("color:rgba(0,0,0,0.2); background:transparent;")
            b_lay.addWidget(car_ico)
            ana.addWidget(banner)

        # ── Scroll içeriği ───────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            f"QScrollArea {{ background:{CARD}; border:none; }}"
            f"QScrollBar:vertical {{ background:#f1f5f9; width:5px; border-radius:3px; }}"
            f"QScrollBar::handle:vertical {{ background:{BORDER}; border-radius:3px; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}"
        )

        icerik = QWidget()
        icerik.setStyleSheet(f"background:{CARD};")
        ic = QVBoxLayout(icerik)
        ic.setContentsMargins(28, 22, 28, 20)
        ic.setSpacing(16)

        # Başlık + durum badge
        baslik_row = QHBoxLayout()
        baslik_lbl = QLabel(f"{arac.marka} {arac.model}")
        f = QFont("Segoe UI", 20)
        f.setWeight(QFont.Weight.Bold)
        baslik_lbl.setFont(f)
        baslik_lbl.setStyleSheet(f"color:{TEXT}; background:transparent;")
        baslik_row.addWidget(baslik_lbl)
        baslik_row.addStretch()

        durum_lbl = QLabel("  Müsait  " if durum_ok else "  Kirada  ")
        durum_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        durum_lbl.setStyleSheet(
            f"background:{SUCCESS if durum_ok else DANGER}; color:#fff;"
            f" border-radius:7px; padding:3px 8px;"
        )
        baslik_row.addWidget(durum_lbl)
        ic.addLayout(baslik_row)

        # Sınıf badge + yıldız puanı
        meta_row = QHBoxLayout()
        meta_row.setSpacing(10)
        sinif_badge = QLabel(f"  {arac.sinif.upper()}  ")
        sinif_badge.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        sinif_badge.setStyleSheet(
            f"background:{sinif_renk}; color:#fff; border-radius:7px; padding:3px 8px;"
        )
        sinif_badge.setFixedHeight(24)
        stars = "★" * round(arac.puan) + "☆" * (5 - round(arac.puan))
        puan_lbl = QLabel(f"  {stars}  {arac.puan:.1f}")
        puan_lbl.setFont(QFont("Segoe UI", 11))
        puan_lbl.setStyleSheet("color:#f59e0b; background:transparent;")
        meta_row.addWidget(sinif_badge)
        meta_row.addWidget(puan_lbl)
        meta_row.addStretch()
        ic.addLayout(meta_row)

        # Fiyat kutusu
        fiyat_frame = QFrame()
        fiyat_frame.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #eef2ff, stop:1 #faf5ff);"
            "border:none; border-radius:14px;"
        )
        fiyat_lay = QHBoxLayout(fiyat_frame)
        fiyat_lay.setContentsMargins(20, 14, 20, 14)

        gun_col = QVBoxLayout()
        gun_col.setSpacing(2)
        gun_num = QLabel(f"{arac.gunluk_fiyat:,.0f} TL")
        gun_num.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        gun_num.setStyleSheet(f"color:{PRIMARY}; background:transparent;")
        gun_cap = QLabel("/ gün")
        gun_cap.setFont(QFont("Segoe UI", 10))
        gun_cap.setStyleSheet(f"color:{MUTED}; background:transparent;")
        gun_col.addWidget(gun_num)
        gun_col.addWidget(gun_cap)
        fiyat_lay.addLayout(gun_col, 1)

        # dikey ince çizgi
        vdiv = QFrame()
        vdiv.setFrameShape(QFrame.Shape.VLine)
        vdiv.setStyleSheet("background:#ddd6fe; border:none;")
        vdiv.setFixedWidth(1)
        fiyat_lay.addWidget(vdiv)
        fiyat_lay.addSpacing(18)

        saat_col = QVBoxLayout()
        saat_col.setSpacing(2)
        saatlik = SINIF_FIYAT.get(arac.sinif, 0)
        saat_num = QLabel(f"{saatlik:,} TL")
        saat_num.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        saat_num.setStyleSheet(f"color:{PRIMARY}; background:transparent;")
        saat_cap = QLabel("/ saat")
        saat_cap.setFont(QFont("Segoe UI", 10))
        saat_cap.setStyleSheet(f"color:{MUTED}; background:transparent;")
        saat_col.addWidget(saat_num)
        saat_col.addWidget(saat_cap)
        fiyat_lay.addLayout(saat_col)

        ic.addWidget(fiyat_frame)

        # Özellikler başlığı
        ic.addWidget(_sep())
        ic.addWidget(_lbl("Araç Özellikleri", bold=True, size=11, color=MUTED))

        def chip(ikon, baslik, deger):
            f = QFrame()
            f.setStyleSheet(
                f"background:#f8fafc; border:none; border-radius:10px;"
            )
            fl = QVBoxLayout(f)
            fl.setContentsMargins(14, 10, 14, 10)
            fl.setSpacing(3)
            cap = QLabel(f"{ikon}  {baslik}")
            cap.setFont(QFont("Segoe UI", 9))
            cap.setStyleSheet(f"color:{MUTED}; background:transparent; border:none;")
            val = QLabel(str(deger))
            val.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            val.setStyleSheet(f"color:{TEXT}; background:transparent; border:none;")
            fl.addWidget(cap)
            fl.addWidget(val)
            return f

        row1 = QHBoxLayout()
        row1.setSpacing(10)
        row1.addWidget(chip("🚗", "Tür",     arac.tur))
        row1.addWidget(chip("⚙", "Vites",   arac.vites))
        row1.addWidget(chip("⛽", "Yakıt",   arac.yakit))
        ic.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        row2.addWidget(chip("💺", "Koltuk",    str(arac.koltuk)))
        row2.addWidget(chip("📍", "Kilometre", f"{arac.kilometre:,} km"))
        row2.addWidget(chip("📊", "Durum",
                            "Müsait" if durum_ok else "Kirada"))
        ic.addLayout(row2)

        # Açıklama
        if arac.aciklama and arac.aciklama.strip():
            ic.addWidget(_sep())
            ic.addWidget(_lbl("Açıklama", bold=True, size=11, color=MUTED))
            ac_lbl = QLabel(arac.aciklama)
            ac_lbl.setFont(QFont("Segoe UI", 12))
            ac_lbl.setWordWrap(True)
            ac_lbl.setStyleSheet(f"color:{TEXT}; background:transparent;")
            ic.addWidget(ac_lbl)

        ic.addStretch()
        scroll.setWidget(icerik)
        ana.addWidget(scroll, 1)

        # ── Buton çubuğu (sabit alt) ────────────────────────
        btn_bar = QFrame()
        btn_bar.setStyleSheet(
            f"background:{CARD}; border-top:1px solid {BORDER};"
        )
        bb = QHBoxLayout(btn_bar)
        bb.setContentsMargins(24, 12, 24, 14)
        bb.setSpacing(8)

        # Haritada gör
        if arac.enlem and arac.boylam:
            btn_harita = QPushButton("📍 Haritada Gör")
            btn_harita.setFixedHeight(38)
            btn_harita.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_harita.setFont(QFont("Segoe UI", 10))
            btn_harita.setStyleSheet(
                "QPushButton { background:#f0fdfa; color:#0f766e;"
                " border:1.5px solid #99f6e4; border-radius:9px; padding:0 14px; }"
                "QPushButton:hover { background:#ccfbf1; }"
            )
            btn_harita.clicked.connect(lambda: harita_ac(arac))
            bb.addWidget(btn_harita)

        # Favori
        if hesap and not hesap.is_admin():
            fav_var = backend.favori_var_mi(hesap.kullanici_id, arac.arac_id)
            self._fav_var = fav_var
            self._btn_fav = QPushButton(
                "♥ Çıkar" if fav_var else "♥ Favorile"
            )
            self._btn_fav.setFixedHeight(38)
            self._btn_fav.setCursor(Qt.CursorShape.PointingHandCursor)
            self._btn_fav.setFont(QFont("Segoe UI", 10))
            self.__fav_stil_uygula()
            self._btn_fav.clicked.connect(self.__favori_toggle)
            bb.addWidget(self._btn_fav)

        bb.addStretch()

        # Kapat
        btn_kapat = QPushButton("Kapat")
        btn_kapat.setFixedHeight(38)
        btn_kapat.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_kapat.setFont(QFont("Segoe UI", 10))
        btn_kapat.setStyleSheet(
            f"QPushButton {{ background:#f1f5f9; color:{MUTED};"
            f" border:none; border-radius:9px; padding:0 20px; }}"
            f"QPushButton:hover {{ background:{BORDER}; color:{TEXT}; }}"
        )
        btn_kapat.clicked.connect(self.reject)
        bb.addWidget(btn_kapat)

        # Kirala
        if hesap and not hesap.is_admin() and durum_ok:
            btn_kirala = QPushButton("Kirala  →")
            btn_kirala.setFixedHeight(38)
            btn_kirala.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_kirala.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            btn_kirala.setStyleSheet(
                f"QPushButton {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"stop:0 {PRIMARY}, stop:1 {PRIM2}); color:#fff;"
                f" border:none; border-radius:9px; padding:0 22px; }}"
                f"QPushButton:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                f"stop:0 {PRIM2}, stop:1 {PRIMARY}); }}"
            )
            btn_kirala.clicked.connect(self.__kirala_ac)
            bb.addWidget(btn_kirala)

        ana.addWidget(btn_bar)

    def __fav_stil_uygula(self):
        if self._fav_var:
            self._btn_fav.setStyleSheet(
                "QPushButton { background:#fff1f2; color:#dc2626;"
                " border:1.5px solid #fda4af; border-radius:9px; padding:0 14px; }"
                "QPushButton:hover { background:#dc2626; color:#fff; }"
            )
        else:
            self._btn_fav.setStyleSheet(
                "QPushButton { background:#f0fdf4; color:#16a34a;"
                " border:1.5px solid #86efac; border-radius:9px; padding:0 14px; }"
                "QPushButton:hover { background:#16a34a; color:#fff; }"
            )

    def __favori_toggle(self):
        self.backend.favori_toggle(self.hesap.kullanici_id, self.arac.arac_id)
        self._fav_var = self.backend.favori_var_mi(
            self.hesap.kullanici_id, self.arac.arac_id
        )
        self._btn_fav.setText("♥ Çıkar" if self._fav_var else "♥ Favorile")
        self.__fav_stil_uygula()

    def __kirala_ac(self):
        self.done(AracDetayDiyalogu.KIRALA_CODE)


# ============================================================
#   KİRALAMA DİYALOGU
# ============================================================
class KiralamaDiyalogu(QDialog):
    """
    Kiralama başlatma diyalogu.
    Kullanıcı başlangıç/bitiş saati seçer → anlık fiyat önizlemesi görür.
    """

    def __init__(self, arac, backend, hesap, parent=None):
        super().__init__(parent)
        self.arac    = arac
        self.backend = backend
        self.hesap   = hesap

        self.setWindowTitle(f"Kiralama — {arac.marka} {arac.model}")
        self.setMinimumWidth(440)
        self.setStyleSheet(f"background:{CARD}; color:{TEXT};")

        sinif_renk = _SINIF_RENK.get(arac.sinif.lower(), PRIMARY)

        ana = QVBoxLayout(self)
        ana.setSpacing(14)
        ana.setContentsMargins(24, 24, 24, 24)

        ana.addWidget(_lbl(f"{arac.marka} {arac.model}", bold=True, size=16))

        s = QLabel(f"  {arac.sinif.upper()}  ")
        s.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        s.setStyleSheet(
            f"background:{sinif_renk}; color:#fff; border-radius:6px; padding:2px 8px;"
        )
        s.setFixedHeight(24)
        ana.addWidget(s)
        ana.addWidget(_sep())

        now = QDateTime.currentDateTime()

        _dt_style = (
            f"QDateTimeEdit {{ background:#f8fafc; border:1px solid {BORDER};"
            f" border-radius:10px; padding:7px 12px; font-size:12px; color:{TEXT}; }}"
            f"QDateTimeEdit:focus {{ border-color:{PRIMARY}; }}"
        )

        ana.addWidget(_lbl("Başlangıç zamanı:", size=12, color=MUTED))
        self._dt_bas = QDateTimeEdit(now)
        self._dt_bas.setDisplayFormat("dd.MM.yyyy  HH:mm")
        self._dt_bas.setCalendarPopup(True)
        self._dt_bas.setMinimumDateTime(now)
        self._dt_bas.setFont(QFont("Segoe UI", 12))
        self._dt_bas.setStyleSheet(_dt_style)
        self._dt_bas.dateTimeChanged.connect(self.__guncelle_onizleme)
        ana.addWidget(self._dt_bas)

        ana.addWidget(_lbl("Bitiş zamanı:", size=12, color=MUTED))
        self._dt_bit = QDateTimeEdit(now.addSecs(3600))
        self._dt_bit.setDisplayFormat("dd.MM.yyyy  HH:mm")
        self._dt_bit.setCalendarPopup(True)
        self._dt_bit.setMinimumDateTime(now.addSecs(60))
        self._dt_bit.setFont(QFont("Segoe UI", 12))
        self._dt_bit.setStyleSheet(_dt_style)
        self._dt_bit.dateTimeChanged.connect(self.__guncelle_onizleme)
        ana.addWidget(self._dt_bit)

        ana.addWidget(_sep())
        ana.addWidget(_lbl("Fiyat Önizleme:", bold=True, size=13))

        self._txt_onizleme = QTextEdit()
        self._txt_onizleme.setReadOnly(True)
        self._txt_onizleme.setFont(QFont("Consolas", 11))
        self._txt_onizleme.setFixedHeight(180)
        self._txt_onizleme.setStyleSheet(
            f"background:{ACCENT}; border:none;"
            f" border-radius:10px; padding:10px; color:{TEXT};"
        )
        ana.addWidget(self._txt_onizleme)

        self.__guncelle_onizleme()

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_iptal = QPushButton("İptal")
        btn_iptal.setFixedHeight(38)
        btn_iptal.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_iptal.setStyleSheet(
            f"QPushButton {{ background:#f1f5f9; color:{MUTED};"
            f" border:none; border-radius:9px; padding:0 20px; }}"
            f"QPushButton:hover {{ background:{BORDER}; color:{TEXT}; }}"
        )
        btn_iptal.clicked.connect(self.reject)

        self._btn_onayla = QPushButton("Kiralamayı Başlat")
        self._btn_onayla.setFixedHeight(38)
        self._btn_onayla.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_onayla.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._btn_onayla.setStyleSheet(
            f"QPushButton {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {PRIMARY}, stop:1 {PRIM2}); color:#fff;"
            f" border:none; border-radius:9px; padding:0 22px; }}"
            f"QPushButton:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {PRIM2}, stop:1 {PRIMARY}); }}"
        )
        self._btn_onayla.clicked.connect(self.__onayla)

        btn_row.addWidget(btn_iptal)
        btn_row.addWidget(self._btn_onayla)
        ana.addLayout(btn_row)

    def __fmt(self, dt: QDateTime) -> str:
        return dt.toString("yyyy-MM-dd HH:mm:ss")

    def __guncelle_onizleme(self):
        bas_str = self.__fmt(self._dt_bas.dateTime())
        bit_str = self.__fmt(self._dt_bit.dateTime())
        ok, sonuc = self.backend.fiyat_on_izle(self.arac.sinif, bas_str, bit_str)
        if ok:
            self._txt_onizleme.setPlainText(fiyat_ozeti(sonuc))
            self._btn_onayla.setEnabled(True)
        else:
            self._txt_onizleme.setPlainText(f"Hata: {sonuc}")
            self._btn_onayla.setEnabled(False)

    def __onayla(self):
        ok, bilgi = self.backend.kiralama_baslat(self.arac.arac_id, self.hesap.kullanici_id)
        if ok:
            QMessageBox.information(
                self, "Kiralama Başlatıldı",
                f"{bilgi['arac']} kiralamasi baslatildi.\n"
                f"Baslangic: {bilgi['baslangic']}\n"
                f"Saatlik tarife: {bilgi['saatlik']:,} TL"
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", bilgi)


# ============================================================
#   HARİTA YARDIMCISI
# ============================================================
def harita_ac(arac):
    """Aracın konumunu Leaflet + OpenStreetMap ile tarayıcıda açar."""
    if not arac.enlem or not arac.boylam:
        return

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>{arac.marka} {arac.model}</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>html,body,#map{{height:100%;margin:0;padding:0;}}</style>
</head>
<body>
<div id="map"></div>
<script>
  var map = L.map('map').setView([{arac.enlem}, {arac.boylam}], 15);
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '&copy; OpenStreetMap contributors'
  }}).addTo(map);
  L.marker([{arac.enlem}, {arac.boylam}])
    .addTo(map)
    .bindPopup('<b>{arac.marka} {arac.model}</b><br>{arac.sinif.upper()} sinifi')
    .openPopup();
</script>
</body>
</html>"""

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    )
    tmp.write(html)
    tmp.close()
    webbrowser.open(f"file:///{tmp.name.replace(os.sep, '/')}")
