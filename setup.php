<?php
/**
 * setup.php
 * Skrip Instalasi dan Inisialisasi Database 'db_bansos_fuzzy'
 * Output Keputusan Hanya: Layak atau Tidak Layak (Tanpa Menengah)
 */

$is_cli = (php_sapi_name() === 'cli');

$db_host = '127.0.0.1';
$db_user = 'root';
$db_pass = '';
$db_name = 'db_bansos_fuzzy';
$candidate_ports = ['3306', '3308', '3307'];

$message = '';
$status = '';
$step_logs = [];
$active_port = '3306';

if ($is_cli || (isset($_POST['action']) && $_POST['action'] === 'install')) {
    if (isset($_POST['db_port']) && !empty($_POST['db_port'])) {
        $candidate_ports = [$_POST['db_port']];
    }

    $pdo_init = null;
    $connected_port = null;

    foreach ($candidate_ports as $p) {
        try {
            $pdo_init = new PDO("mysql:host={$db_host};port={$p};charset=utf8mb4", $db_user, $db_pass, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
            ]);
            $connected_port = $p;
            $active_port = $p;
            break;
        } catch (PDOException $e) {
            // Lanjut ke port berikutnya
        }
    }

    if (!$pdo_init) {
        $status = 'danger';
        $message = "Tidak dapat terhubung ke MySQL di port " . implode(', ', $candidate_ports) . ". Pastikan WampServer sedang berjalan.";
        $step_logs[] = "Gagal koneksi: Pastikan ikon WampServer berwarna hijau di taskbar.";
    } else {
        try {
            $step_logs[] = "Berhasil terhubung ke server MySQL ({$db_host}:{$connected_port})";

            // 1. Buat Database
            $pdo_init->exec("CREATE DATABASE IF NOT EXISTS `{$db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
            $step_logs[] = "Database '{$db_name}' berhasil dipastikan/dibuat";

            // 2. Hubungkan ke database db_bansos_fuzzy
            $pdo = new PDO("mysql:host={$db_host};port={$connected_port};dbname={$db_name};charset=utf8mb4", $db_user, $db_pass, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
            ]);

            // 3. Buat Tabel admin
            $pdo->exec("CREATE TABLE IF NOT EXISTS admin (
                id_admin INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                nama_petugas VARCHAR(100) NOT NULL
            ) ENGINE=InnoDB");
            $step_logs[] = "Tabel 'admin' siap";

            $chkAdmin = $pdo->query("SELECT COUNT(*) FROM admin WHERE username = 'admin'")->fetchColumn();
            if ($chkAdmin == 0) {
                $pdo->exec("INSERT INTO admin (username, password, nama_petugas) VALUES ('admin', 'admin123', 'Administrator')");
                $step_logs[] = "Akun Admin default dibuat (username: admin | password: admin123)";
            }

            // 4. Buat Tabel warga
            $pdo->exec("CREATE TABLE IF NOT EXISTS warga (
                id_warga INT AUTO_INCREMENT PRIMARY KEY,
                nik VARCHAR(16) NOT NULL UNIQUE,
                nama_lengkap VARCHAR(100) NOT NULL,
                alamat TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB");
            $step_logs[] = "Tabel 'warga' siap";

            // 5. Buat Tabel parameter_trapesium
            $pdo->exec("CREATE TABLE IF NOT EXISTS parameter_trapesium (
                id_param INT AUTO_INCREMENT PRIMARY KEY,
                nama_variabel ENUM('penghasilan', 'jumlah_anak', 'ukuran_rumah', 'usia', 'jumlah_tanggungan', 'kelayakan') NOT NULL,
                kategori VARCHAR(30) NOT NULL,
                a_val DECIMAL(12,2) NOT NULL,
                b_val DECIMAL(12,2) NOT NULL,
                c_val DECIMAL(12,2) NOT NULL,
                d_val DECIMAL(12,2) NOT NULL
            ) ENGINE=InnoDB");
            $step_logs[] = "Tabel 'parameter_trapesium' siap";

            // 6. Buat Tabel rule_base (Hanya Layak & Tidak Layak)
            $pdo->exec("CREATE TABLE IF NOT EXISTS rule_base (
                id_rule INT AUTO_INCREMENT PRIMARY KEY,
                kode_rule VARCHAR(10) NOT NULL UNIQUE,
                penghasilan VARCHAR(20) NOT NULL,
                jumlah_anak VARCHAR(20) NOT NULL,
                ukuran_rumah VARCHAR(20) NOT NULL,
                usia VARCHAR(20) NOT NULL,
                jumlah_tanggungan VARCHAR(20) NOT NULL,
                keputusan_output ENUM('Tidak_Layak', 'Layak') NOT NULL
            ) ENGINE=InnoDB");
            // Alter jika sebelumnya ENUM ada Menengah
            $pdo->exec("ALTER TABLE rule_base MODIFY keputusan_output ENUM('Tidak_Layak', 'Layak') NOT NULL");
            $step_logs[] = "Tabel 'rule_base' siap (Output: Layak / Tidak Layak)";

            // 7. Buat Tabel pengajuan_bansos
            $pdo->exec("CREATE TABLE IF NOT EXISTS pengajuan_bansos (
                id_pengajuan INT AUTO_INCREMENT PRIMARY KEY,
                id_warga INT NOT NULL,
                penghasilan_perbulan DECIMAL(12,2) NOT NULL,
                jumlah_anak INT NOT NULL,
                ukuran_rumah DECIMAL(8,2) NOT NULL,
                usia INT NOT NULL,
                jumlah_tanggungan INT NOT NULL,
                tanggal_pengajuan DATE NOT NULL,
                FOREIGN KEY (id_warga) REFERENCES warga(id_warga) ON DELETE CASCADE
            ) ENGINE=InnoDB");
            $step_logs[] = "Tabel 'pengajuan_bansos' siap";

            // 8. Buat Tabel hasil_evaluasi_fuzzy (Hanya Layak & Tidak Layak)
            $pdo->exec("CREATE TABLE IF NOT EXISTS hasil_evaluasi_fuzzy (
                id_evaluasi INT AUTO_INCREMENT PRIMARY KEY,
                id_pengajuan INT NOT NULL UNIQUE,
                skor_defuzzifikasi DECIMAL(5,2) NOT NULL,
                status_keputusan ENUM('Tidak_Layak', 'Layak') NOT NULL,
                tanggal_evaluasi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_pengajuan) REFERENCES pengajuan_bansos(id_pengajuan) ON DELETE CASCADE
            ) ENGINE=InnoDB");
            // Alter jika sebelumnya ENUM ada Menengah
            $pdo->exec("ALTER TABLE hasil_evaluasi_fuzzy MODIFY status_keputusan ENUM('Tidak_Layak', 'Layak') NOT NULL");
            $step_logs[] = "Tabel 'hasil_evaluasi_fuzzy' siap (Output: Layak / Tidak Layak)";

            // 9. Seed Parameter Trapesium (Hanya Layak & Tidak Layak)
            $pdo->exec("TRUNCATE TABLE parameter_trapesium");
            $sql_params = "INSERT INTO parameter_trapesium (nama_variabel, kategori, a_val, b_val, c_val, d_val) VALUES
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
            ('kelayakan', 'Layak', 40, 60, 100, 100)";
            $pdo->exec($sql_params);
            $step_logs[] = "Data 'parameter_trapesium' diperbarui (Kelayakan: Layak & Tidak Layak)";

            // 10. Seed 15 Rule Base (Hanya Layak & Tidak Layak)
            $pdo->exec("TRUNCATE TABLE rule_base");
            $sql_rules = "INSERT INTO rule_base (kode_rule, penghasilan, jumlah_anak, ukuran_rumah, usia, jumlah_tanggungan, keputusan_output) VALUES
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
            ('R15', 'Rendah', 'Sedikit', 'Sedang', 'Muda', 'Sedikit', 'Layak')";
            $pdo->exec($sql_rules);
            $step_logs[] = "Data 15 Rule Base diperbarui (Output: Layak / Tidak Layak)";

            // 11. Data Pemohon Demo
            $chkWarga = $pdo->query("SELECT COUNT(*) FROM warga")->fetchColumn();
            if ($chkWarga == 0) {
                $pdo->exec("INSERT INTO warga (nik, nama_lengkap, alamat) VALUES
                ('3201011203650001', 'Bapak Suryadi Pratama', 'Jl. Kenanga No. 14, RT 02 / RW 05'),
                ('3201012508780002', 'Ibu Aminah Kusuma', 'Kp. Babakan Lebak RT 03 / RW 01'),
                ('3201011504900003', 'Rian Hermawan', 'Perum Asri Blok D2 No. 8')");
                $step_logs[] = "3 Data Contoh Warga berhasil ditambahkan";
            }

            $status = 'success';
            $message = "Inisialisasi Database Berhasil! Sistem kini hanya menggunakan 2 status: LAYAK dan TIDAK LAYAK.";
        } catch (PDOException $e) {
            $status = 'danger';
            $message = "Terjadi kegagalan: " . $e->getMessage();
            $step_logs[] = "Error: " . $e->getMessage();
        }
    }

    if ($is_cli) {
        echo "=== HASIL SETUP DATABASE ===\n";
        echo "Status: " . ($status === 'success' ? 'SUKSES' : 'GAGAL') . "\n";
        echo "Pesan: " . $message . "\n";
        foreach ($step_logs as $log) {
            echo " - " . $log . "\n";
        }
        exit;
    }
}
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Setup Database - SPK Bansos</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f7f7f7; margin: 30px auto; max-width: 600px; }
        .box { background: #fff; border: 1px solid #ccc; padding: 20px; border-radius: 4px; }
        .btn { background: #27ae60; color: #fff; padding: 10px 15px; border: none; cursor: pointer; font-weight: bold; border-radius: 3px; width: 100%; }
        .alert-success { background: #d4edda; color: #155724; padding: 10px; border: 1px solid #c3e6cb; margin-bottom: 15px; }
        .alert-danger { background: #f8d7da; color: #721c24; padding: 10px; border: 1px solid #f5c6cb; margin-bottom: 15px; }
    </style>
</head>
<body>
<div class="box">
    <h3 style="margin-top:0;">Setup Database SPK Bansos (Hanya Layak / Tidak Layak)</h3>
    <?php if (!empty($message)): ?>
        <div class="alert-<?= $status ?>"><?= htmlspecialchars($message) ?></div>
        <?php if (!empty($step_logs)): ?>
            <ul>
                <?php foreach ($step_logs as $log): ?>
                    <li><?= htmlspecialchars($log) ?></li>
                <?php endforeach; ?>
            </ul>
        <?php endif; ?>
        <div style="margin-top:15px;">
            <a href="index.php" style="color:#2980b9; font-weight:bold; text-decoration:none;">&larr; Ke Halaman Input Pengunjung</a> | 
            <a href="admin.php" style="color:#27ae60; font-weight:bold; text-decoration:none;">Ke Panel Admin &rarr;</a>
        </div>
    <?php else: ?>
        <p>Klik tombol di bawah untuk memperbarui database: output hasil hanya ada <strong>Layak</strong> dan <strong>Tidak Layak</strong> (kategori Menengah telah dihilangkan):</p>
        <form method="POST" action="setup.php">
            <input type="hidden" name="action" value="install">
            <button type="submit" class="btn">Update Database Sekarang</button>
        </form>
    <?php endif; ?>
</div>
</body>
</html>
