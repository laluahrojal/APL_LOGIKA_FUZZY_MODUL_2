<?php
/**
 * hapus.php
 * Skrip Menghapus Data Pengajuan Bansos (Khusus Admin)
 */

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header("Location: login.php?msg=perlu_login");
    exit;
}

require_once __DIR__ . '/koneksi.php';

$id = isset($_GET['id']) ? (int)$_GET['id'] : 0;

if ($pdo && $id > 0) {
    try {
        $stmt = $pdo->prepare("DELETE FROM pengajuan_bansos WHERE id_pengajuan = ?");
        $stmt->execute([$id]);
        header("Location: admin.php?msg=deleted");
        exit;
    } catch (PDOException $e) {
        die("Gagal menghapus data: " . $e->getMessage() . " <br><a href='admin.php'>Kembali ke Panel Admin</a>");
    }
} else {
    header("Location: admin.php");
    exit;
}
