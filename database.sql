-- ========================================================
-- SISTEM PENDUKUNG KEPUTUSAN PENERIMAAN BANTUAN SOSIAL
-- METODE FUZZY MAMDANI (OUTPUT: HANYA LAYAK ATAU TIDAK LAYAK)
-- Database: db_bansos_fuzzy
-- ========================================================

-- 1. Buat Database
CREATE DATABASE IF NOT EXISTS db_bansos_fuzzy CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE db_bansos_fuzzy;

-- 2. Tabel Admin
CREATE TABLE IF NOT EXISTS admin (
    id_admin INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nama_petugas VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

-- 3. Tabel Data Pemohon (Identitas Warga)
CREATE TABLE IF NOT EXISTS warga (
    id_warga INT AUTO_INCREMENT PRIMARY KEY,
    nik VARCHAR(16) NOT NULL UNIQUE,
    nama_lengkap VARCHAR(100) NOT NULL,
    alamat TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 4. Tabel Parameter Fungsi Keanggotaan Trapesium
CREATE TABLE IF NOT EXISTS parameter_trapesium (
    id_param INT AUTO_INCREMENT PRIMARY KEY,
    nama_variabel ENUM('penghasilan', 'jumlah_anak', 'ukuran_rumah', 'usia', 'jumlah_tanggungan', 'kelayakan') NOT NULL,
    kategori VARCHAR(30) NOT NULL,
    a_val DECIMAL(12,2) NOT NULL,
    b_val DECIMAL(12,2) NOT NULL,
    c_val DECIMAL(12,2) NOT NULL,
    d_val DECIMAL(12,2) NOT NULL
) ENGINE=InnoDB;

-- 5. Tabel Rule Base (15 Aturan Fuzzy - Hanya Layak atau Tidak Layak)
CREATE TABLE IF NOT EXISTS rule_base (
    id_rule INT AUTO_INCREMENT PRIMARY KEY,
    kode_rule VARCHAR(10) NOT NULL UNIQUE,
    penghasilan VARCHAR(20) NOT NULL,
    jumlah_anak VARCHAR(20) NOT NULL,
    ukuran_rumah VARCHAR(20) NOT NULL,
    usia VARCHAR(20) NOT NULL,
    jumlah_tanggungan VARCHAR(20) NOT NULL,
    keputusan_output ENUM('Tidak_Layak', 'Layak') NOT NULL
) ENGINE=InnoDB;

-- 6. Tabel Transaksi Input Pengajuan (5 Input Utama)
CREATE TABLE IF NOT EXISTS pengajuan_bansos (
    id_pengajuan INT AUTO_INCREMENT PRIMARY KEY,
    id_warga INT NOT NULL,
    penghasilan_perbulan DECIMAL(12,2) NOT NULL, -- Input 1 (Rp)
    jumlah_anak INT NOT NULL,                   -- Input 2 (Orang)
    ukuran_rumah DECIMAL(8,2) NOT NULL,          -- Input 3 (m2)
    usia INT NOT NULL,                           -- Input 4 (Tahun)
    jumlah_tanggungan INT NOT NULL,              -- Input 5 (Orang)
    tanggal_pengajuan DATE NOT NULL,
    FOREIGN KEY (id_warga) REFERENCES warga(id_warga) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. Tabel Hasil Evaluasi Fuzzy (Output Defuzzifikasi - Hanya Layak atau Tidak Layak)
CREATE TABLE IF NOT EXISTS hasil_evaluasi_fuzzy (
    id_evaluasi INT AUTO_INCREMENT PRIMARY KEY,
    id_pengajuan INT NOT NULL UNIQUE,
    skor_defuzzifikasi DECIMAL(5,2) NOT NULL, -- Skor Z (0 - 100)
    status_keputusan ENUM('Tidak_Layak', 'Layak') NOT NULL,
    tanggal_evaluasi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_pengajuan) REFERENCES pengajuan_bansos(id_pengajuan) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ========================================================
-- ISI DATA AWAL (SEED DATA: HANYA LAYAK ATAU TIDAK LAYAK)
-- ========================================================

-- Akun Admin Default
INSERT INTO admin (username, password, nama_petugas) VALUES
('admin', 'admin123', 'Administrator Bansos')
ON DUPLICATE KEY UPDATE nama_petugas=VALUES(nama_petugas);

-- Parameter Trapesium (Tanpa Menengah pada Kelayakan)
TRUNCATE TABLE parameter_trapesium;
INSERT INTO parameter_trapesium (nama_variabel, kategori, a_val, b_val, c_val, d_val) VALUES
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
('kelayakan', 'Layak', 40, 60, 100, 100);

-- 15 Rule Base (Hanya Layak atau Tidak Layak)
TRUNCATE TABLE rule_base;
INSERT INTO rule_base (kode_rule, penghasilan, jumlah_anak, ukuran_rumah, usia, jumlah_tanggungan, keputusan_output) VALUES
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
('R15', 'Rendah', 'Sedikit', 'Sedang', 'Muda', 'Sedikit', 'Layak');

-- Data Pemohon Demo
INSERT INTO warga (nik, nama_lengkap, alamat) VALUES
('3201011203650001', 'Bapak Suryadi Pratama', 'Jl. Kenanga No. 14, RT 02 / RW 05'),
('3201012508780002', 'Ibu Aminah Kusuma', 'Kp. Babakan Lebak RT 03 / RW 01'),
('3201011504900003', 'Rian Hermawan', 'Perum Asri Blok D2 No. 8')
ON DUPLICATE KEY UPDATE nama_lengkap=VALUES(nama_lengkap);
