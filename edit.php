<?php
/**
 * edit.php
 * Halaman Edit Data Pengajuan & 5 Kriteria (Murni HTML & PHP Sederhana)
 */

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header("Location: login.php?msg=perlu_login");
    exit;
}

require_once __DIR__ . '/koneksi.php';
require_once __DIR__ . '/fuzzy/MamdaniEvaluator.php';

$id_pengajuan = isset($_GET['id']) ? (int)$_GET['id'] : 0;
$pesan_error  = '';

if (!$pdo || $id_pengajuan <= 0) {
    header("Location: admin.php");
    exit;
}

// Ambil data pengajuan & warga
$stmt = $pdo->prepare("
    SELECT p.*, w.nik, w.nama_lengkap, w.alamat
    FROM pengajuan_bansos p
    JOIN warga w ON p.id_warga = w.id_warga
    WHERE p.id_pengajuan = ?
");
$stmt->execute([$id_pengajuan]);
$data = $stmt->fetch();

if (!$data) {
    die("Data pengajuan tidak ditemukan. <a href='admin.php'>Kembali</a>");
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $nama_lengkap      = trim($_POST['nama_lengkap'] ?? '');
    $alamat            = trim($_POST['alamat'] ?? '');
    $penghasilan       = (float)($_POST['penghasilan_perbulan'] ?? 0);
    $jumlah_anak       = (int)($_POST['jumlah_anak'] ?? 0);
    $ukuran_rumah      = (float)($_POST['ukuran_rumah'] ?? 0);
    $usia              = (int)($_POST['usia'] ?? 0);
    $jumlah_tanggungan = (int)($_POST['jumlah_tanggungan'] ?? 0);

    if (empty($nama_lengkap) || empty($alamat)) {
        $pesan_error = "Nama dan Alamat wajib diisi!";
    } else {
        try {
            $pdo->beginTransaction();

            // 1. Update data warga
            $up_w = $pdo->prepare("UPDATE warga SET nama_lengkap = ?, alamat = ? WHERE id_warga = ?");
            $up_w->execute([$nama_lengkap, $alamat, $data['id_warga']]);

            // 2. Update kriteria pengajuan
            $up_p = $pdo->prepare("
                UPDATE pengajuan_bansos SET 
                    penghasilan_perbulan = ?,
                    jumlah_anak = ?,
                    ukuran_rumah = ?,
                    usia = ?,
                    jumlah_tanggungan = ?
                WHERE id_pengajuan = ?
            ");
            $up_p->execute([$penghasilan, $jumlah_anak, $ukuran_rumah, $usia, $jumlah_tanggungan, $id_pengajuan]);

            // 3. Hitung ulang logika Fuzzy Mamdani
            $evaluator = new MamdaniEvaluator($pdo);
            $fuzzy = $evaluator->evaluate([
                'penghasilan_perbulan' => $penghasilan,
                'jumlah_anak'          => $jumlah_anak,
                'ukuran_rumah'         => $ukuran_rumah,
                'usia'                 => $usia,
                'jumlah_tanggungan'    => $jumlah_tanggungan
            ]);

            // 4. Update tabel hasil evaluasi
            $up_h = $pdo->prepare("
                UPDATE hasil_evaluasi_fuzzy SET 
                    skor_defuzzifikasi = ?,
                    status_keputusan = ?,
                    tanggal_evaluasi = NOW()
                WHERE id_pengajuan = ?
            ");
            $up_h->execute([$fuzzy['skor_defuzzifikasi'], $fuzzy['status_keputusan'], $id_pengajuan]);

            $pdo->commit();

            header("Location: admin.php?msg=edit_sukses");
            exit;
        } catch (Exception $e) {
            if ($pdo->inTransaction()) {
                $pdo->rollBack();
            }
            $pesan_error = "Gagal menyimpan perubahan: " . $e->getMessage();
        }
    }
}
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Edit Data Pengajuan Bansos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f7f7f7;
            margin: 20px auto;
            max-width: 650px;
            color: #333;
        }
        .box {
            background: #fff;
            border: 1px solid #ccc;
            padding: 20px;
            border-radius: 4px;
        }
        .form-group {
            margin-bottom: 12px;
        }
        .form-group label {
            display: block;
            font-weight: bold;
            margin-bottom: 3px;
            font-size: 13px;
        }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 7px;
            box-sizing: border-box;
            border: 1px solid #ccc;
            border-radius: 3px;
        }
        .btn-simpan {
            background-color: #2980b9;
            color: white;
            padding: 8px 15px;
            border: none;
            cursor: pointer;
            font-weight: bold;
            border-radius: 3px;
        }
        .btn-batal {
            background-color: #7f8c8d;
            color: white;
            padding: 8px 15px;
            text-decoration: none;
            font-size: 13px;
            border-radius: 3px;
        }
        .alert-error {
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #f5c6cb;
            border-radius: 3px;
        }
    </style>
</head>
<body>

<div class="box">
    <h3 style="margin-top:0;">Edit Data Pemohon & 5 Kriteria Bansos</h3>
    <p style="font-size:12px; color:#666; margin-top:0;">Nilai Skor Z dan status kelayakan akan otomatis dihitung ulang setelah data disimpan.</p>

    <?php if (!empty($pesan_error)): ?>
        <div class="alert-error"><?= htmlspecialchars($pesan_error) ?></div>
    <?php endif; ?>

    <form method="POST" action="edit.php?id=<?= $id_pengajuan ?>">
        <div class="form-group">
            <label>NIK (Tidak dapat diubah):</label>
            <input type="text" value="<?= htmlspecialchars($data['nik']) ?>" disabled style="background:#eee;">
        </div>

        <div class="form-group">
            <label>Nama Lengkap Pemohon:</label>
            <input type="text" name="nama_lengkap" value="<?= htmlspecialchars($data['nama_lengkap']) ?>" required>
        </div>

        <div class="form-group">
            <label>Alamat Lengkap:</label>
            <textarea name="alamat" rows="2" required><?= htmlspecialchars($data['alamat']) ?></textarea>
        </div>

        <div class="form-group">
            <label>1. Penghasilan Perbulan (Rp):</label>
            <input type="number" step="any" name="penghasilan_perbulan" value="<?= (float)$data['penghasilan_perbulan'] ?>" required>
            <small style="color:#666;">Batas: Rendah (&le; Rp 1.000.000 / Layak), Sedang (Rp 1.000.000 - Rp 2.000.000 / Menengah), Tinggi (&ge; Rp 4.000.000 / Tidak Layak)</small>
        </div>

        <div class="form-group">
            <label>2. Jumlah Anak (Orang):</label>
            <input type="number" name="jumlah_anak" min="0" value="<?= (int)$data['jumlah_anak'] ?>" required>
            <small style="color:#666;">Batas: Sedikit (&le; 2 anak), Sedang (3 - 5 anak), Banyak (&gt; 5 anak)</small>
        </div>

        <div class="form-group">
            <label>3. Ukuran Rumah (m²):</label>
            <input type="number" step="any" name="ukuran_rumah" min="1" value="<?= (float)$data['ukuran_rumah'] ?>" required>
            <small style="color:#666;">Batas: Kecil (1 - 10 m² / Layak), Sedang (10 - 20 m² / Menengah), Besar (20 - 50 m² / Tidak Layak)</small>
        </div>

        <div class="form-group">
            <label>4. Usia Pemohon (Tahun):</label>
            <input type="number" name="usia" min="17" value="<?= (int)$data['usia'] ?>" required>
            <small style="color:#666;">Batas: Muda (&le; 35 th), Paruh Baya (30 - 55 th), Lansia (&ge; 50 th)</small>
        </div>

        <div class="form-group">
            <label>5. Jumlah Tanggungan (Orang):</label>
            <input type="number" name="jumlah_tanggungan" min="0" value="<?= (int)$data['jumlah_tanggungan'] ?>" required>
            <small style="color:#666;">Batas: Sedikit (&le; 2 org), Sedang (3 - 5 org), Banyak (&gt; 5 org)</small>
        </div>

        <div style="margin-top:15px;">
            <button type="submit" class="btn-simpan">Simpan & Hitung Ulang Fuzzy</button>
            <a href="admin.php" class="btn-batal">Batal</a>
        </div>
    </form>
</div>

</body>
</html>
