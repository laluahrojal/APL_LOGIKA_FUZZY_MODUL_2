# SPK Bantuan Sosial - Fuzzy Mamdani (100% Python Murni)

Sistem Pendukung Keputusan (SPK) Penilaian Kelayakan Penerima Bantuan Sosial berbasis **Python Murni**.
**Tanpa HTML, Tanpa CSS, Tanpa Web Browser, dan Tanpa Server Web.**

---

## 🚀 Cara Menjalankan

### 1. Mode Aplikasi Desktop (GUI Windows)
Cukup jalankan:
```bash
python main.py
```
*(atau `python gui_app.py`)*

Jendela aplikasi desktop Windows akan langsung terbuka dengan fitur:
- 📝 **Formulir Input Pemohon & Perhitungan Otomatis** (Status Layak / Tidak Layak, Skor Z, Rincian Rule Aktif, dan Derajat Keanggotaan).
- 📋 **Kelola Data Pemohon** (Tabel Data, Edit dengan Hitung Ulang Fuzzy Otomatis, dan Hapus Data).
- 📊 **Grafik Batang Statistik** (Digambar langsung secara native menggunakan Python Canvas).

---

### 2. Mode Terminal Interaktif (CLI)
Jika ingin menggunakan antarmuka terminal/konsol:
```bash
python main.py --cli
```
*(atau `python cli.py`)*

---

### 3. Uji Coba Logika Fuzzy Mandiri
```bash
python fuzzy_mamdani.py
```

---

## 📁 Struktur File Python Murni

| File | Deskripsi |
| :--- | :--- |
| **`main.py`** | Titik masuk utama program (menjalankan GUI desktop atau CLI). |
| **`gui_app.py`** | Antarmuka Desktop GUI murni (Tkinter) lengkap dengan Form, Tabel Admin, dan Grafik Vektor Native. |
| **`cli.py`** | Antarmuka interaktif via Terminal/Konsol. |
| **`fuzzy_mamdani.py`** | Algoritma Fuzzy Mamdani lengkap (Fuzzifikasi Trapesium, 15 Rule Base, Agregasi MAX, Defuzzifikasi Centroid). |
| **`db_manager.py`** | Database SQLite lokal (`bansos.db`), otomatis inisialisasi tabel dan data pemohon. |

---

## 💡 Keunggulan
- **100% Standar Library Python**: Menggunakan `tkinter` dan `sqlite3` yang sudah bawaan dari Python di Windows.
- **Tanpa Perlu Instalasi Tambahan**: Tidak membutuhkan `pip install`, tidak membutuhkan Flask, dan tidak membuka browser.
- **Offline & Cepat**: Berjalan langsung di komputer secara instan.
