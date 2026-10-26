<?php
/**
 * admin.php
 * Halaman Khusus Admin: Menampilkan Grafik Masing-Masing Input & Tabel Kelola Data (Edit / Hapus)
 * Menggunakan HTML Murni (Tanpa JS dan CSS Eksternal)
 */

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Cek autentikasi admin
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header("Location: login.php?msg=perlu_login");
    exit;
}

require_once __DIR__ . '/koneksi.php';

$list_pengajuan = [];
$total_data = 0;

// Variabel Penampung Statistik / Grafik Masing-Masing Input
$stat_penghasilan = ['Rendah' => 0, 'Sedang' => 0, 'Tinggi' => 0];
$stat_anak        = ['Sedikit' => 0, 'Sedang' => 0, 'Banyak' => 0];
$stat_rumah       = ['Kecil' => 0, 'Sedang' => 0, 'Besar' => 0];
$stat_usia        = ['Muda' => 0, 'Paruh_Baya' => 0, 'Lansia' => 0];
$stat_tanggungan  = ['Sedikit' => 0, 'Sedang' => 0, 'Banyak' => 0];
$stat_keputusan   = ['Layak' => 0, 'Tidak_Layak' => 0];

if ($pdo) {
    try {
        $stmt = $pdo->query("
            SELECT p.*, w.nik, w.nama_lengkap, w.alamat,
                   h.skor_defuzzifikasi, h.status_keputusan
            FROM pengajuan_bansos p
            JOIN warga w ON p.id_warga = w.id_warga
            LEFT JOIN hasil_evaluasi_fuzzy h ON p.id_pengajuan = h.id_pengajuan
            ORDER BY p.id_pengajuan DESC
        ");
        $list_pengajuan = $stmt->fetchAll();
        $total_data = count($list_pengajuan);

        // Hitung distribusi statistik untuk grafik masing-masing input (Sesuai batas baru)
        foreach ($list_pengajuan as $row) {
            // 1. Penghasilan
            $gaji = (float)$row['penghasilan_perbulan'];
            if ($gaji <= 1000000) {
                $stat_penghasilan['Rendah']++;
            } elseif ($gaji <= 2000000) {
                $stat_penghasilan['Sedang']++;
            } else {
                $stat_penghasilan['Tinggi']++;
            }

            // 2. Jumlah Anak
            $anak = (int)$row['jumlah_anak'];
            if ($anak <= 2) {
                $stat_anak['Sedikit']++;
            } elseif ($anak <= 5) {
                $stat_anak['Sedang']++;
            } else {
                $stat_anak['Banyak']++;
            }

            // 3. Ukuran Rumah
            $rumah = (float)$row['ukuran_rumah'];
            if ($rumah <= 10) {
                $stat_rumah['Kecil']++;
            } elseif ($rumah <= 20) {
                $stat_rumah['Sedang']++;
            } else {
                $stat_rumah['Besar']++;
            }

            // 4. Usia
            $usia = (int)$row['usia'];
            if ($usia < 35) {
                $stat_usia['Muda']++;
            } elseif ($usia <= 55) {
                $stat_usia['Paruh_Baya']++;
            } else {
                $stat_usia['Lansia']++;
            }

            // 5. Tanggungan
            $tanggungan = (int)$row['jumlah_tanggungan'];
            if ($tanggungan <= 2) {
                $stat_tanggungan['Sedikit']++;
            } elseif ($tanggungan <= 5) {
                $stat_tanggungan['Sedang']++;
            } else {
                $stat_tanggungan['Banyak']++;
            }

            // Keputusan Output
            $kep = $row['status_keputusan'] ?? 'Tidak_Layak';
            if (isset($stat_keputusan[$kep])) {
                $stat_keputusan[$kep]++;
            }
        }
    } catch (PDOException $e) {
        // Table not ready
    }
}

/**
 * Fungsi pembantu menggambar batang grafik dengan murni HTML
 */
function buatGrafikBarHtml($label, $jumlah, $total, $warna = '#2980b9') {
    $persen = ($total > 0) ? round(($jumlah / $total) * 100) : 0;
    ?>
    <div style="margin-bottom:8px;">
        <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">
            <span><strong><?= htmlspecialchars($label) ?></strong></span>
            <span><?= $jumlah ?> orang (<?= $persen ?>%)</span>
        </div>
        <div style="background-color:#e0e0e0; width:100%; height:18px; border-radius:3px; overflow:hidden;">
            <div style="background-color:<?= $warna ?>; width:<?= $persen ?>%; height:18px; min-width:<?= $jumlah > 0 ? '8px' : '0' ?>;"></div>
        </div>
    </div>
    <?php
}
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Halaman Admin - Grafik & Kelola Data Bansos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f7f7f7;
            margin: 20px auto;
            max-width: 950px;
            color: #333;
        }
        .nav-menu {
            background-color: #2c3e50;
            padding: 10px 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .nav-menu a {
            color: #fff;
            text-decoration: none;
            margin-right: 15px;
            font-weight: bold;
        }
        .nav-menu a:hover {
            text-decoration: underline;
        }
        .box {
            background: #fff;
            border: 1px solid #ccc;
            padding: 15px 20px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 13px;
        }
        table, th, td {
            border: 1px solid #bbb;
        }
        th, td {
            padding: 7px 9px;
            text-align: left;
        }
        th {
            background-color: #eee;
        }
        .grid-grafik {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .kotak-grafik {
            background: #fafafa;
            border: 1px solid #ddd;
            padding: 12px;
            border-radius: 4px;
        }
        .btn-edit {
            background-color: #f39c12;
            color: white;
            text-decoration: none;
            padding: 3px 7px;
            font-size: 11px;
            border-radius: 3px;
        }
        .btn-hapus {
            background-color: #c0392b;
            color: white;
            text-decoration: none;
            padding: 3px 7px;
            font-size: 11px;
            border-radius: 3px;
        }
        .alert-sukses {
            background-color: #d4edda;
            color: #155724;
            padding: 10px;
            border: 1px solid #c3e6cb;
            margin-bottom: 15px;
            border-radius: 4px;
        }
    </style>
</head>
<body>

<!-- Menu Navigasi Sederhana -->
<div class="nav-menu">
    <a href="index.php">Form Input Pengunjung</a>
    <a href="admin.php">Grafik & Kelola Data (Admin)</a>
    <a href="logout.php" style="float:right; color:#ffdddd;">Logout (<?= htmlspecialchars($_SESSION['admin_user']) ?>)</a>
</div>

<h2>Panel Administrator - SPK Bansos Fuzzy</h2>
<p>Selamat datang <strong><?= htmlspecialchars($_SESSION['admin_nama'] ?? 'Admin') ?></strong>. Di halaman ini Anda dapat melihat grafik distribusi untuk masing-masing kriteria input serta mengedit atau menghapus data pengajuan.</p>

<?php if (isset($_GET['msg']) && $_GET['msg'] === 'deleted'): ?>
    <div class="alert-sukses">Data berhasil dihapus dari sistem!</div>
<?php elseif (isset($_GET['msg']) && $_GET['msg'] === 'edit_sukses'): ?>
    <div class="alert-sukses">Data berhasil diubah dan nilai Fuzzy telah dihitung ulang!</div>
<?php endif; ?>

<!-- ======================================================== -->
<!-- BAGIAN 1: GRAFIK MASING-MASING INPUT (MURNI HTML)        -->
<!-- ======================================================== -->
<div class="box">
    <h3 style="margin-top:0;">Grafik Statistik Masing-Masing Kriteria Masukan (Total: <?= $total_data ?> Data)</h3>
    <p style="font-size:12px; color:#666; margin-top:0;">Grafik batang murni HTML yang menampilkan sebaran nilai pemohon pada setiap kategori kriteria:</p>

    <div class="grid-grafik">
        <!-- Grafik Input 1: Penghasilan -->
        <div class="kotak-grafik">
            <h4 style="margin:0 0 10px 0; font-size:14px; color:#2c3e50;">1. Grafik Penghasilan Perbulan</h4>
            <?php buatGrafikBarHtml('Rendah (≤ Rp 1.000.000 / Layak)', $stat_penghasilan['Rendah'], $total_data, '#27ae60'); ?>
            <?php buatGrafikBarHtml('Sedang (Rp 1.000.000 - Rp 2.000.000 / Menengah)', $stat_penghasilan['Sedang'], $total_data, '#f39c12'); ?>
            <?php buatGrafikBarHtml('Tinggi (≥ Rp 4.000.000 / Tidak Layak)', $stat_penghasilan['Tinggi'], $total_data, '#c0392b'); ?>
        </div>

        <!-- Grafik Input 2: Jumlah Anak -->
        <div class="kotak-grafik">
            <h4 style="margin:0 0 10px 0; font-size:14px; color:#2c3e50;">2. Grafik Jumlah Anak</h4>
            <?php buatGrafikBarHtml('Sedikit (≤ 2 anak)', $stat_anak['Sedikit'], $total_data, '#3498db'); ?>
            <?php buatGrafikBarHtml('Sedang (3 - 5 anak)', $stat_anak['Sedang'], $total_data, '#9b59b6'); ?>
            <?php buatGrafikBarHtml('Banyak (> 5 anak)', $stat_anak['Banyak'], $total_data, '#e67e22'); ?>
        </div>

        <!-- Grafik Input 3: Ukuran Rumah -->
        <div class="kotak-grafik">
            <h4 style="margin:0 0 10px 0; font-size:14px; color:#2c3e50;">3. Grafik Ukuran Rumah (m²)</h4>
            <?php buatGrafikBarHtml('Kecil (1 - 10 m² / Layak)', $stat_rumah['Kecil'], $total_data, '#16a085'); ?>
            <?php buatGrafikBarHtml('Sedang (10 - 20 m² / Menengah)', $stat_rumah['Sedang'], $total_data, '#f1c40f'); ?>
            <?php buatGrafikBarHtml('Besar (20 - 50 m² / Tidak Layak)', $stat_rumah['Besar'], $total_data, '#e74c3c'); ?>
        </div>

        <!-- Grafik Input 4: Usia Pemohon -->
        <div class="kotak-grafik">
            <h4 style="margin:0 0 10px 0; font-size:14px; color:#2c3e50;">4. Grafik Usia Pemohon</h4>
            <?php buatGrafikBarHtml('Muda (≤ 35 tahun)', $stat_usia['Muda'], $total_data, '#2980b9'); ?>
            <?php buatGrafikBarHtml('Paruh Baya (30 - 55 tahun)', $stat_usia['Paruh_Baya'], $total_data, '#d35400'); ?>
            <?php buatGrafikBarHtml('Lansia (≥ 50 tahun)', $stat_usia['Lansia'], $total_data, '#8e44ad'); ?>
        </div>

        <!-- Grafik Input 5: Jumlah Tanggungan -->
        <div class="kotak-grafik">
            <h4 style="margin:0 0 10px 0; font-size:14px; color:#2c3e50;">5. Grafik Jumlah Tanggungan</h4>
            <?php buatGrafikBarHtml('Sedikit (≤ 2 orang)', $stat_tanggungan['Sedikit'], $total_data, '#1abc9c'); ?>
            <?php buatGrafikBarHtml('Sedang (3 - 5 orang)', $stat_tanggungan['Sedang'], $total_data, '#34495e'); ?>
            <?php buatGrafikBarHtml('Banyak (> 5 orang)', $stat_tanggungan['Banyak'], $total_data, '#c0392b'); ?>
        </div>

        <!-- Grafik Hasil Keputusan Kelayakan -->
        <div class="kotak-grafik">
            <h4 style="margin:0 0 10px 0; font-size:14px; color:#2c3e50;">6. Grafik Hasil Keputusan Kelayakan</h4>
            <?php buatGrafikBarHtml('Layak Menerima Bansos', $stat_keputusan['Layak'], $total_data, '#27ae60'); ?>
            <?php buatGrafikBarHtml('Tidak Layak', $stat_keputusan['Tidak_Layak'], $total_data, '#c0392b'); ?>
        </div>
    </div>
</div>

<!-- ======================================================== -->
<!-- BAGIAN 2: TABEL DATA PENGAJUAN (EDIT & HAPUS)            -->
<!-- ======================================================== -->
<div class="box">
    <h3 style="margin-top:0;">Tabel Data Pemohon Bansos (Admin Bisa Mengedit & Menghapus)</h3>
    <table>
        <thead>
            <tr>
                <th style="width:4%;">No</th>
                <th>NIK & Nama</th>
                <th>Alamat</th>
                <th>5 Kriteria Masukan</th>
                <th>Skor Z</th>
                <th>Keputusan</th>
                <th style="width:14%; text-align:center;">Aksi</th>
            </tr>
        </thead>
        <tbody>
            <?php if (!empty($list_pengajuan)): ?>
                <?php $no = 1; foreach ($list_pengajuan as $row): ?>
                    <tr>
                        <td style="text-align:center;"><?= $no++ ?></td>
                        <td>
                            <strong><?= htmlspecialchars($row['nama_lengkap']) ?></strong><br>
                            <small style="color:#666;">NIK: <?= htmlspecialchars($row['nik']) ?></small>
                        </td>
                        <td><?= htmlspecialchars($row['alamat']) ?></td>
                        <td style="font-size:12px;">
                            Gaji: Rp <?= number_format($row['penghasilan_perbulan'], 0, ',', '.') ?><br>
                            Anak: <?= $row['jumlah_anak'] ?> | Rumah: <?= $row['ukuran_rumah'] ?> m²<br>
                            Usia: <?= $row['usia'] ?> th | Tanggungan: <?= $row['jumlah_tanggungan'] ?> org
                        </td>
                        <td style="font-weight:bold; color:#2980b9; text-align:center;">
                            <?= number_format($row['skor_defuzzifikasi'], 2) ?>
                        </td>
                        <td style="font-weight:bold;">
                            <?php if ($row['status_keputusan'] === 'Layak'): ?>
                                <span style="color:#27ae60;">Layak</span>
                            <?php else: ?>
                                <span style="color:#c0392b;">Tidak Layak</span>
                            <?php endif; ?>
                        </td>
                        <td style="text-align:center;">
                            <a href="edit.php?id=<?= $row['id_pengajuan'] ?>" class="btn-edit">Edit</a>
                            <a href="hapus.php?id=<?= $row['id_pengajuan'] ?>" class="btn-hapus" onclick="return confirm('Apakah Anda yakin ingin menghapus data ini?')">Hapus</a>
                        </td>
                    </tr>
                <?php endforeach; ?>
            <?php else: ?>
                <tr>
                    <td colspan="7" style="text-align:center; color:#888;">Belum ada data pengajuan yang tersimpan.</td>
                </tr>
            <?php endif; ?>
        </tbody>
    </table>
</div>

<div style="text-align:center; font-size:12px; color:#777; margin-top:20px;">
    Panel Admin SPK Bansos &bull; Murni PHP & HTML
</div>

</body>
</html>
