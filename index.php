<?php
/**
 * index.php - Form Input Pengunjung & Hasil Keputusan Fuzzy Mamdani
 * Tampilan Murni HTML Sederhana & Ringkas
 */

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

require_once __DIR__ . '/koneksi.php';
require_once __DIR__ . '/fuzzy/MamdaniEvaluator.php';

$hasil_evaluasi = null;
$pesan_sukses   = '';
$pesan_error    = '';

$nik               = $_POST['nik'] ?? '';
$nama_lengkap      = $_POST['nama_lengkap'] ?? '';
$alamat            = $_POST['alamat'] ?? '';
$penghasilan       = $_POST['penghasilan_perbulan'] ?? '';
$jumlah_anak       = $_POST['jumlah_anak'] ?? '';
$ukuran_rumah      = $_POST['ukuran_rumah'] ?? '';
$usia              = $_POST['usia'] ?? '';
$jumlah_tanggungan = $_POST['jumlah_tanggungan'] ?? '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (empty($nik) || empty($nama_lengkap) || empty($alamat) || $penghasilan === '' || $jumlah_anak === '' || $ukuran_rumah === '' || $usia === '' || $jumlah_tanggungan === '') {
        $pesan_error = "Harap lengkapi seluruh isian form!";
    } elseif ($pdo) {
        try {
            // 1. Simpan Warga
            $stmt = $pdo->prepare("SELECT id_warga FROM warga WHERE nik = ?");
            $stmt->execute([$nik]);
            $id_warga = $stmt->fetchColumn();

            if ($id_warga) {
                $pdo->prepare("UPDATE warga SET nama_lengkap = ?, alamat = ? WHERE id_warga = ?")->execute([$nama_lengkap, $alamat, $id_warga]);
            } else {
                $ins = $pdo->prepare("INSERT INTO warga (nik, nama_lengkap, alamat) VALUES (?, ?, ?)");
                $ins->execute([$nik, $nama_lengkap, $alamat]);
                $id_warga = $pdo->lastInsertId();
            }

            // 2. Simpan Pengajuan
            $ins_p = $pdo->prepare("INSERT INTO pengajuan_bansos (id_warga, penghasilan_perbulan, jumlah_anak, ukuran_rumah, usia, jumlah_tanggungan, tanggal_pengajuan) VALUES (?, ?, ?, ?, ?, ?, CURDATE())");
            $ins_p->execute([$id_warga, (float)$penghasilan, (int)$jumlah_anak, (float)$ukuran_rumah, (int)$usia, (int)$jumlah_tanggungan]);
            $id_pengajuan = $pdo->lastInsertId();

            // 3. Evaluasi Fuzzy Mamdani
            $evaluator = new MamdaniEvaluator($pdo);
            $hasil_evaluasi = $evaluator->evaluate([
                'penghasilan_perbulan' => (float)$penghasilan,
                'jumlah_anak'          => (int)$jumlah_anak,
                'ukuran_rumah'         => (float)$ukuran_rumah,
                'usia'                 => (int)$usia,
                'jumlah_tanggungan'    => (int)$jumlah_tanggungan
            ]);

            // 4. Simpan Hasil
            $pdo->prepare("INSERT INTO hasil_evaluasi_fuzzy (id_pengajuan, skor_defuzzifikasi, status_keputusan) VALUES (?, ?, ?)")
                ->execute([$id_pengajuan, $hasil_evaluasi['skor_defuzzifikasi'], $hasil_evaluasi['status_keputusan']]);

            $pesan_sukses = "Data berhasil disimpan dan dievaluasi!";
        } catch (Exception $e) {
            $pesan_error = "Error: " . $e->getMessage();
        }
    } else {
        $pesan_error = "Koneksi database belum aktif. Buka <a href='setup.php'>setup.php</a>.";
    }
}
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>SPK Bantuan Sosial (Fuzzy Mamdani)</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f7f7f7; margin: 15px auto; max-width: 850px; color: #333; }
        .nav { background: #2c3e50; padding: 10px 15px; margin-bottom: 15px; border-radius: 4px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 15px; font-weight: bold; font-size: 14px; }
        .box { background: #fff; border: 1px solid #ccc; padding: 15px 20px; margin-bottom: 15px; border-radius: 4px; }
        table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 13px; }
        table, th, td { border: 1px solid #bbb; }
        th, td { padding: 6px 9px; text-align: left; }
        th { background: #eee; }
        .fg { margin-bottom: 10px; }
        .fg label { display: block; font-weight: bold; margin-bottom: 3px; font-size: 13px; }
        .fg input, .fg textarea { width: 100%; padding: 6px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 3px; }
        .btn { background: #27ae60; color: #fff; padding: 9px 18px; border: none; cursor: pointer; font-weight: bold; border-radius: 3px; font-size: 14px; }
        .alert-s { background: #d4edda; color: #155724; padding: 8px 12px; margin-bottom: 12px; border: 1px solid #c3e6cb; border-radius: 3px; }
        .alert-d { background: #f8d7da; color: #721c24; padding: 8px 12px; margin-bottom: 12px; border: 1px solid #f5c6cb; border-radius: 3px; }
        .badge-l { background: #27ae60; color: #fff; padding: 4px 8px; font-weight: bold; border-radius: 3px; }
        .badge-tl { background: #c0392b; color: #fff; padding: 4px 8px; font-weight: bold; border-radius: 3px; }
    </style>
</head>
<body>

<div class="nav">
    <a href="index.php">Form Input Pengunjung</a>
    <a href="admin.php">Panel Admin (Grafik & Data)</a>
    <?php if (isset($_SESSION['admin_logged_in'])): ?>
        <a href="logout.php" style="float:right; color:#ffdddd;">Logout (<?= htmlspecialchars($_SESSION['admin_user']) ?>)</a>
    <?php else: ?>
        <a href="login.php" style="float:right;">Login Admin</a>
    <?php endif; ?>
</div>

<h3>Sistem Penilaian Bantuan Sosial (Fuzzy Mamdani)</h3>
<p style="font-size:13px; color:#555; margin-top:-5px;">Isi formulir di bawah. Rule aktif dan hasil keputusan (Layak / Tidak Layak) langsung tampil di bawah form.</p>

<?php if ($pesan_sukses): ?><div class="alert-s"><?= $pesan_sukses ?></div><?php endif; ?>
<?php if ($pesan_error): ?><div class="alert-d"><?= $pesan_error ?></div><?php endif; ?>

<div class="box">
    <form method="POST" action="index.php">
        <div class="fg">
            <label>1. NIK (Nomor Induk Kependudukan):</label>
            <input type="text" name="nik" maxlength="16" placeholder="Contoh: 3201012508780002" value="<?= htmlspecialchars($nik) ?>" required>
        </div>
        <div class="fg">
            <label>2. Nama Lengkap:</label>
            <input type="text" name="nama_lengkap" placeholder="Contoh: Ibu Aminah Kusuma" value="<?= htmlspecialchars($nama_lengkap) ?>" required>
        </div>
        <div class="fg">
            <label>3. Alamat Lengkap:</label>
            <textarea name="alamat" rows="2" placeholder="Contoh: Kp. Babakan RT 02 / RW 01" required><?= htmlspecialchars($alamat) ?></textarea>
        </div>
        <div class="fg">
            <label>4. Penghasilan Perbulan (Rp):</label>
            <input type="number" name="penghasilan_perbulan" placeholder="Contoh: 950000" value="<?= htmlspecialchars($penghasilan) ?>" required>
            <small style="color:#666;">Batas: Rendah (&le; Rp 1.000.000 / Layak), Sedang (Rp 1.000.000 - Rp 2.000.000 / Menengah), Tinggi (&ge; Rp 4.000.000 / Tidak Layak)</small>
        </div>
        <div class="fg">
            <label>5. Jumlah Anak (Orang):</label>
            <input type="number" name="jumlah_anak" min="0" placeholder="Contoh: 3" value="<?= htmlspecialchars($jumlah_anak) ?>" required>
            <small style="color:#666;">Batas: Sedikit (&le; 2 anak), Sedang (3 - 5 anak), Banyak (&gt; 5 anak)</small>
        </div>
        <div class="fg">
            <label>6. Ukuran Rumah (m²):</label>
            <input type="number" step="any" name="ukuran_rumah" min="1" placeholder="Contoh: 9" value="<?= htmlspecialchars($ukuran_rumah) ?>" required>
            <small style="color:#666;">Batas: Kecil (1 - 10 m² / Layak), Sedang (10 - 20 m² / Menengah), Besar (20 - 50 m² / Tidak Layak)</small>
        </div>
        <div class="fg">
            <label>7. Usia Pemohon (Tahun):</label>
            <input type="number" name="usia" min="17" placeholder="Contoh: 48" value="<?= htmlspecialchars($usia) ?>" required>
            <small style="color:#666;">Batas: Muda (&le; 35 th), Paruh Baya (30 - 55 th), Lansia (&ge; 50 th)</small>
        </div>
        <div class="fg">
            <label>8. Jumlah Tanggungan (Orang):</label>
            <input type="number" name="jumlah_tanggungan" min="0" placeholder="Contoh: 4" value="<?= htmlspecialchars($jumlah_tanggungan) ?>" required>
            <small style="color:#666;">Batas: Sedikit (&le; 2 org), Sedang (3 - 5 org), Banyak (&gt; 5 org)</small>
        </div>
        <button type="submit" class="btn">Proses & Cek Kelayakan Bansos</button>
    </form>
</div>

<!-- HASIL KEPUTUSAN LANGSUNG MUNCUL DI BAWAH -->
<?php if ($hasil_evaluasi): ?>
    <div class="box" style="border: 2px solid #2980b9;">
        <h3 style="margin-top:0; color:#2980b9;">Hasil Keputusan Kelayakan Bantuan Sosial</h3>
        <table>
            <tr>
                <td style="width:25%; font-weight:bold;">Nama Pemohon:</td>
                <td><?= htmlspecialchars($nama_lengkap) ?> (NIK: <?= htmlspecialchars($nik) ?>)</td>
                <td style="width:25%; font-weight:bold;">Alamat:</td>
                <td><?= htmlspecialchars($alamat) ?></td>
            </tr>
            <tr>
                <td style="font-weight:bold;">Gaji Perbulan:</td>
                <td>Rp <?= number_format((float)$penghasilan, 0, ',', '.') ?></td>
                <td style="font-weight:bold;">Ukuran Rumah:</td>
                <td><?= htmlspecialchars($ukuran_rumah) ?> m²</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">Jumlah Anak:</td>
                <td><?= htmlspecialchars($jumlah_anak) ?> orang</td>
                <td style="font-weight:bold;">Tanggungan:</td>
                <td><?= htmlspecialchars($jumlah_tanggungan) ?> orang</td>
            </tr>
            <tr>
                <td style="font-weight:bold;">Usia Pemohon:</td>
                <td><?= htmlspecialchars($usia) ?> tahun</td>
                <td style="font-weight:bold;">Status Keputusan:</td>
                <td>
                    <?php if ($hasil_evaluasi['status_keputusan'] === 'Layak'): ?>
                        <span class="badge-l">LAYAK MENERIMA BANSOS</span>
                    <?php else: ?>
                        <span class="badge-tl">TIDAK LAYAK</span>
                    <?php endif; ?>
                </td>
            </tr>
            <tr>
                <td style="font-weight:bold;">Skor Z (Centroid):</td>
                <td colspan="3"><strong style="font-size:16px; color:#2980b9;"><?= number_format($hasil_evaluasi['skor_defuzzifikasi'], 2) ?></strong> (Skala 0 - 100)</td>
            </tr>
        </table>

        <!-- RULE YANG TERKENA / AKTIF -->
        <h4 style="margin:12px 0 4px 0;">Daftar Rule Base yang Terkena / Aktif (&alpha; > 0):</h4>
        <table>
            <thead>
                <tr>
                    <th style="width:10%;">Rule</th>
                    <th>Kondisi Kriteria (IF)</th>
                    <th style="width:18%;">Output (THEN)</th>
                    <th style="width:15%;">Nilai &alpha;</th>
                </tr>
            </thead>
            <tbody>
                <?php if (!empty($hasil_evaluasi['active_rules'])): ?>
                    <?php foreach ($hasil_evaluasi['active_rules'] as $ar): ?>
                        <tr style="background:#fff9e6;">
                            <td style="font-weight:bold; text-align:center;"><?= $ar['kode_rule'] ?></td>
                            <td>
                                Gaji: <?= $ar['penghasilan']['kategori'] ?> (<?= $ar['penghasilan']['mu'] ?>), 
                                Anak: <?= $ar['jumlah_anak']['kategori'] ?> (<?= $ar['jumlah_anak']['mu'] ?>), 
                                Rumah: <?= $ar['ukuran_rumah']['kategori'] ?> (<?= $ar['ukuran_rumah']['mu'] ?>), 
                                Usia: <?= $ar['usia']['kategori'] ?> (<?= $ar['usia']['mu'] ?>), 
                                Tanggungan: <?= $ar['jumlah_tanggungan']['kategori'] ?> (<?= $ar['jumlah_tanggungan']['mu'] ?>)
                            </td>
                            <td style="font-weight:bold;">
                                <?= ($ar['keputusan_output'] === 'Layak') ? '<span style="color:#27ae60;">Layak</span>' : '<span style="color:#c0392b;">Tidak Layak</span>' ?>
                            </td>
                            <td style="font-weight:bold; text-align:center; color:#2980b9;"><?= number_format($ar['alpha'], 4) ?></td>
                        </tr>
                    <?php endforeach; ?>
                <?php else: ?>
                    <tr><td colspan="4" style="text-align:center; color:#888;">Tidak ada rule aktif.</td></tr>
                <?php endif; ?>
            </tbody>
        </table>

        <!-- HASIL AGREGASI KOMPOSISI (MAX) -->
        <h4 style="margin:12px 0 4px 0;">Hasil Agregasi Komposisi (MAX):</h4>
        <table>
            <tr>
                <th style="width:50%; text-align:center;">Max &alpha; (Tidak Layak)</th>
                <th style="width:50%; text-align:center;">Max &alpha; (Layak)</th>
            </tr>
            <tr style="text-align:center; font-weight:bold; font-size:16px;">
                <td style="color:#c0392b;"><?= number_format($hasil_evaluasi['agregasi']['Tidak_Layak'], 4) ?></td>
                <td style="color:#27ae60;"><?= number_format($hasil_evaluasi['agregasi']['Layak'], 4) ?></td>
            </tr>
        </table>
    </div>
<?php endif; ?>

<div style="text-align:center; font-size:12px; color:#888; margin-top:15px;">
    SPK Bantuan Sosial &bull; Fuzzy Mamdani (Fungsi Trapesium)
</div>

</body>
</html>
