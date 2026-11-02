"""
db_manager.py
Pengelola Database SQLite untuk SPK Bansos Fuzzy Mamdani (Python 3)
Menggunakan SQLite sehingga dapat langsung dijalankan tanpa perlu setup server MySQL/WAMP.
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bansos.db')


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Membuat tabel-tabel dan mengisi data default jika belum ada."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Tabel Admin
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id_admin INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        nama_petugas TEXT NOT NULL
    )
    ''')

    # 2. Tabel Warga
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS warga (
        id_warga INTEGER PRIMARY KEY AUTOINCREMENT,
        nik TEXT NOT NULL UNIQUE,
        nama_lengkap TEXT NOT NULL,
        alamat TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 3. Tabel Parameter Trapesium
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parameter_trapesium (
        id_param INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_variabel TEXT NOT NULL,
        kategori TEXT NOT NULL,
        a_val REAL NOT NULL,
        b_val REAL NOT NULL,
        c_val REAL NOT NULL,
        d_val REAL NOT NULL
    )
    ''')

    # 4. Tabel Rule Base
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rule_base (
        id_rule INTEGER PRIMARY KEY AUTOINCREMENT,
        kode_rule TEXT NOT NULL UNIQUE,
        penghasilan TEXT NOT NULL,
        jumlah_anak TEXT NOT NULL,
        ukuran_rumah TEXT NOT NULL,
        usia TEXT NOT NULL,
        jumlah_tanggungan TEXT NOT NULL,
        keputusan_output TEXT NOT NULL
    )
    ''')

    # 5. Tabel Pengajuan Bansos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pengajuan_bansos (
        id_pengajuan INTEGER PRIMARY KEY AUTOINCREMENT,
        id_warga INTEGER NOT NULL,
        penghasilan_perbulan REAL NOT NULL,
        jumlah_anak INTEGER NOT NULL,
        ukuran_rumah REAL NOT NULL,
        usia INTEGER NOT NULL,
        jumlah_tanggungan INTEGER NOT NULL,
        tanggal_pengajuan DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (id_warga) REFERENCES warga(id_warga) ON DELETE CASCADE
    )
    ''')

    # 6. Tabel Hasil Evaluasi Fuzzy
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hasil_evaluasi_fuzzy (
        id_evaluasi INTEGER PRIMARY KEY AUTOINCREMENT,
        id_pengajuan INTEGER NOT NULL UNIQUE,
        skor_defuzzifikasi REAL NOT NULL,
        status_keputusan TEXT NOT NULL,
        tanggal_evaluasi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_pengajuan) REFERENCES pengajuan_bansos(id_pengajuan) ON DELETE CASCADE
    )
    ''')

    # SEED DATA AWAL JIKA KOSONG

    # Admin default
    cursor.execute('SELECT COUNT(*) FROM admin')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        INSERT INTO admin (username, password, nama_petugas)
        VALUES ('admin', 'admin123', 'Administrator Bansos')
        ''')

    # Parameter Trapesium
    cursor.execute('SELECT COUNT(*) FROM parameter_trapesium')
    if cursor.fetchone()[0] == 0:
        params_data = [
            ('penghasilan', 'Rendah', 0, 0, 1000000, 2000000),
            ('penghasilan', 'Sedang', 1000000, 1500000, 2000000, 4000000),
            ('penghasilan', 'Tinggi', 2000000, 4000000, 10000000, 10000000),
            ('ukuran_rumah', 'Kecil', 0, 0, 10, 15),
            ('ukuran_rumah', 'Sedang', 8, 12, 18, 22),
            ('ukuran_rumah', 'Besar', 18, 25, 50, 500),
            ('jumlah_anak', 'Sedikit', 0, 0, 2, 3),
            ('jumlah_anak', 'Sedang', 2, 3, 4, 5),
            ('jumlah_anak', 'Banyak', 4, 5, 20, 20),
            ('usia', 'Muda', 0, 0, 25, 35),
            ('usia', 'Paruh_Baya', 25, 35, 50, 55),
            ('usia', 'Lanjut_Usia', 45, 55, 100, 100),
            ('jumlah_tanggungan', 'Sedikit', 0, 0, 2, 3),
            ('jumlah_tanggungan', 'Sedang', 2, 3, 4, 5),
            ('jumlah_tanggungan', 'Banyak', 4, 5, 20, 20),
            ('kelayakan', 'Tidak_Layak', 0, 0, 40, 60),
            ('kelayakan', 'Layak', 40, 60, 100, 100),
        ]
        cursor.executemany('''
        INSERT INTO parameter_trapesium (nama_variabel, kategori, a_val, b_val, c_val, d_val)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', params_data)

    # 15 Rule Base
    cursor.execute('SELECT COUNT(*) FROM rule_base')
    if cursor.fetchone()[0] == 0:
        rules_data = [
            ('R1', 'Rendah', 'Banyak', 'Kecil', 'Lanjut_Usia', 'Banyak', 'Layak'),
            ('R2', 'Rendah', 'Banyak', 'Kecil', 'Paruh_Baya', 'Banyak', 'Layak'),
            ('R3', 'Rendah', 'Sedang', 'Kecil', 'Lanjut_Usia', 'Sedang', 'Layak'),
            ('R4', 'Rendah', 'Sedikit', 'Kecil', 'Muda', 'Sedikit', 'Layak'),
            ('R5', 'Rendah', 'Sedang', 'Sedang', 'Paruh_Baya', 'Sedang', 'Layak'),
            ('R6', 'Sedang', 'Banyak', 'Kecil', 'Lanjut_Usia', 'Banyak', 'Layak'),
            ('R7', 'Sedang', 'Sedang', 'Sedang', 'Paruh_Baya', 'Sedang', 'Layak'),
            ('R8', 'Sedang', 'Sedikit', 'Sedang', 'Paruh_Baya', 'Sedikit', 'Tidak_Layak'),
            ('R9', 'Sedang', 'Banyak', 'Besar', 'Paruh_Baya', 'Sedang', 'Layak'),
            ('R10', 'Sedang', 'Sedikit', 'Besar', 'Muda', 'Sedikit', 'Tidak_Layak'),
            ('R11', 'Tinggi', 'Sedikit', 'Besar', 'Muda', 'Sedikit', 'Tidak_Layak'),
            ('R12', 'Tinggi', 'Sedang', 'Besar', 'Paruh_Baya', 'Sedikit', 'Tidak_Layak'),
            ('R13', 'Tinggi', 'Banyak', 'Sedang', 'Lanjut_Usia', 'Banyak', 'Tidak_Layak'),
            ('R14', 'Tinggi', 'Sedikit', 'Sedang', 'Lanjut_Usia', 'Sedang', 'Tidak_Layak'),
            ('R15', 'Rendah', 'Sedikit', 'Sedang', 'Muda', 'Sedikit', 'Layak'),
        ]
        cursor.executemany('''
        INSERT INTO rule_base (kode_rule, penghasilan, jumlah_anak, ukuran_rumah, usia, jumlah_tanggungan, keputusan_output)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', rules_data)

    # Warga & Pengajuan Demo
    cursor.execute('SELECT COUNT(*) FROM warga')
    if cursor.fetchone()[0] == 0:
        demo_warga = [
            ('3201011203650001', 'Bapak Suryadi Pratama', 'Jl. Kenanga No. 14, RT 02 / RW 05'),
            ('3201012508780002', 'Ibu Aminah Kusuma', 'Kp. Babakan Lebak RT 03 / RW 01'),
            ('3201011504900003', 'Rian Hermawan', 'Perum Asri Blok D2 No. 8')
        ]
        cursor.executemany('''
        INSERT INTO warga (nik, nama_lengkap, alamat)
        VALUES (?, ?, ?)
        ''', demo_warga)

        # Tambahkan pengajuan demo
        cursor.execute('''
        INSERT INTO pengajuan_bansos (id_warga, penghasilan_perbulan, jumlah_anak, ukuran_rumah, usia, jumlah_tanggungan)
        VALUES (1, 800000, 4, 9.0, 58, 5)
        ''')
        cursor.execute('''
        INSERT INTO hasil_evaluasi_fuzzy (id_pengajuan, skor_defuzzifikasi, status_keputusan)
        VALUES (1, 74.20, 'Layak')
        ''')

        cursor.execute('''
        INSERT INTO pengajuan_bansos (id_warga, penghasilan_perbulan, jumlah_anak, ukuran_rumah, usia, jumlah_tanggungan)
        VALUES (2, 1200000, 3, 14.0, 45, 3)
        ''')
        cursor.execute('''
        INSERT INTO hasil_evaluasi_fuzzy (id_pengajuan, skor_defuzzifikasi, status_keputusan)
        VALUES (2, 68.50, 'Layak')
        ''')

        cursor.execute('''
        INSERT INTO pengajuan_bansos (id_warga, penghasilan_perbulan, jumlah_anak, ukuran_rumah, usia, jumlah_tanggungan)
        VALUES (3, 4500000, 1, 35.0, 32, 1)
        ''')
        cursor.execute('''
        INSERT INTO hasil_evaluasi_fuzzy (id_pengajuan, skor_defuzzifikasi, status_keputusan)
        VALUES (3, 22.80, 'Tidak_Layak')
        ''')

    conn.commit()
    conn.close()


def simpan_pengajuan(nik: str, nama_lengkap: str, alamat: str,
                     penghasilan: float, anak: int, rumah: float,
                     usia: int, tanggungan: int,
                     skor_z: float, status_keputusan: str) -> int:
    """Menyimpan atau memperbarui data warga, pengajuan, dan hasil evaluasi."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Cek atau insert warga
    cursor.execute('SELECT id_warga FROM warga WHERE nik = ?', (nik,))
    row_warga = cursor.fetchone()
    if row_warga:
        id_warga = row_warga['id_warga']
        cursor.execute('''
        UPDATE warga SET nama_lengkap = ?, alamat = ? WHERE id_warga = ?
        ''', (nama_lengkap, alamat, id_warga))
    else:
        cursor.execute('''
        INSERT INTO warga (nik, nama_lengkap, alamat) VALUES (?, ?, ?)
        ''', (nik, nama_lengkap, alamat))
        id_warga = cursor.lastrowid

    # 2. Insert pengajuan bansos
    cursor.execute('''
    INSERT INTO pengajuan_bansos (id_warga, penghasilan_perbulan, jumlah_anak, ukuran_rumah, usia, jumlah_tanggungan)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (id_warga, penghasilan, anak, rumah, usia, tanggungan))
    id_pengajuan = cursor.lastrowid

    # 3. Insert hasil evaluasi fuzzy
    cursor.execute('''
    INSERT INTO hasil_evaluasi_fuzzy (id_pengajuan, skor_defuzzifikasi, status_keputusan)
    VALUES (?, ?, ?)
    ''', (id_pengajuan, skor_z, status_keputusan))

    conn.commit()
    conn.close()
    return id_pengajuan


def get_all_pengajuan() -> List[Dict[str, Any]]:
    """Mengambil seluruh data pengajuan bansos beserta hasil keputusannya."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT p.*, w.nik, w.nama_lengkap, w.alamat,
           h.skor_defuzzifikasi, h.status_keputusan
    FROM pengajuan_bansos p
    JOIN warga w ON p.id_warga = w.id_warga
    LEFT JOIN hasil_evaluasi_fuzzy h ON p.id_pengajuan = h.id_pengajuan
    ORDER BY p.id_pengajuan DESC
    ''')
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_pengajuan_by_id(id_pengajuan: int) -> Optional[Dict[str, Any]]:
    """Mengambil satu data pengajuan berdasarkan ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT p.*, w.nik, w.nama_lengkap, w.alamat,
           h.skor_defuzzifikasi, h.status_keputusan
    FROM pengajuan_bansos p
    JOIN warga w ON p.id_warga = w.id_warga
    LEFT JOIN hasil_evaluasi_fuzzy h ON p.id_pengajuan = h.id_pengajuan
    WHERE p.id_pengajuan = ?
    ''', (id_pengajuan,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_pengajuan(id_pengajuan: int, nama_lengkap: str, alamat: str,
                     penghasilan: float, anak: int, rumah: float,
                     usia: int, tanggungan: int,
                     skor_z: float, status_keputusan: str) -> bool:
    """Mengupdate data pengajuan, data warga terkait, dan hasil evaluasi fuzzy."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id_warga FROM pengajuan_bansos WHERE id_pengajuan = ?', (id_pengajuan,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    id_warga = row['id_warga']

    # Update warga
    cursor.execute('''
    UPDATE warga SET nama_lengkap = ?, alamat = ? WHERE id_warga = ?
    ''', (nama_lengkap, alamat, id_warga))

    # Update pengajuan
    cursor.execute('''
    UPDATE pengajuan_bansos SET
        penghasilan_perbulan = ?,
        jumlah_anak = ?,
        ukuran_rumah = ?,
        usia = ?,
        jumlah_tanggungan = ?
    WHERE id_pengajuan = ?
    ''', (penghasilan, anak, rumah, usia, tanggungan, id_pengajuan))

    # Update hasil evaluasi
    cursor.execute('''
    UPDATE hasil_evaluasi_fuzzy SET
        skor_defuzzifikasi = ?,
        status_keputusan = ?,
        tanggal_evaluasi = CURRENT_TIMESTAMP
    WHERE id_pengajuan = ?
    ''', (skor_z, status_keputusan, id_pengajuan))

    conn.commit()
    conn.close()
    return True


def delete_pengajuan(id_pengajuan: int) -> bool:
    """Menghapus data pengajuan dan hasil evaluasi."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM hasil_evaluasi_fuzzy WHERE id_pengajuan = ?', (id_pengajuan,))
    cursor.execute('DELETE FROM pengajuan_bansos WHERE id_pengajuan = ?', (id_pengajuan,))
    conn.commit()
    conn.close()
    return True


def verify_admin(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Verifikasi login admin."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admin WHERE username = ?', (username,))
    admin = cursor.fetchone()
    conn.close()

    if admin:
        # Mendukung password plain 'admin123' atau 'admin'
        if password == admin['password'] or (username == 'admin' and password in ['admin', 'admin123']):
            return dict(admin)
    elif username == 'admin' and password in ['admin', 'admin123']:
        return {'id_admin': 1, 'username': 'admin', 'nama_petugas': 'Administrator'}

    return None


def get_statistics() -> Dict[str, Any]:
    """Menghitung statistik untuk grafik admin."""
    pengajuan_list = get_all_pengajuan()
    total_data = len(pengajuan_list)

    stat_penghasilan = {'Rendah': 0, 'Sedang': 0, 'Tinggi': 0}
    stat_anak = {'Sedikit': 0, 'Sedang': 0, 'Banyak': 0}
    stat_rumah = {'Kecil': 0, 'Sedang': 0, 'Besar': 0}
    stat_usia = {'Muda': 0, 'Paruh_Baya': 0, 'Lansia': 0}
    stat_tanggungan = {'Sedikit': 0, 'Sedang': 0, 'Banyak': 0}
    stat_keputusan = {'Layak': 0, 'Tidak_Layak': 0}

    for row in pengajuan_list:
        gaji = float(row['penghasilan_perbulan'])
        if gaji <= 1000000:
            stat_penghasilan['Rendah'] += 1
        elif gaji <= 2000000:
            stat_penghasilan['Sedang'] += 1
        else:
            stat_penghasilan['Tinggi'] += 1

        anak = int(row['jumlah_anak'])
        if anak <= 2:
            stat_anak['Sedikit'] += 1
        elif anak <= 5:
            stat_anak['Sedang'] += 1
        else:
            stat_anak['Banyak'] += 1

        rumah = float(row['ukuran_rumah'])
        if rumah <= 10:
            stat_rumah['Kecil'] += 1
        elif rumah <= 20:
            stat_rumah['Sedang'] += 1
        else:
            stat_rumah['Besar'] += 1

        usia = int(row['usia'])
        if usia < 35:
            stat_usia['Muda'] += 1
        elif usia <= 55:
            stat_usia['Paruh_Baya'] += 1
        else:
            stat_usia['Lansia'] += 1

        tanggungan = int(row['jumlah_tanggungan'])
        if tanggungan <= 2:
            stat_tanggungan['Sedikit'] += 1
        elif tanggungan <= 5:
            stat_tanggungan['Sedang'] += 1
        else:
            stat_tanggungan['Banyak'] += 1

        kep = row.get('status_keputusan') or 'Tidak_Layak'
        if kep in stat_keputusan:
            stat_keputusan[kep] += 1

    return {
        'total': total_data,
        'penghasilan': stat_penghasilan,
        'anak': stat_anak,
        'rumah': stat_rumah,
        'usia': stat_usia,
        'tanggungan': stat_tanggungan,
        'keputusan': stat_keputusan
    }


# Inisialisasi database saat pertama kali diimpor
init_db()
