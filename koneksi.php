<?php
/**
 * koneksi.php - Koneksi Database MySQL (WampServer)
 * Sistem Pendukung Keputusan Bansos Fuzzy Mamdani
 */

$db_host = '127.0.0.1';
$db_name = 'db_bansos_fuzzy';
$db_user = 'root';
$db_pass = '';

$candidate_ports = ['3306', '3308', '3307'];
$pdo = null;
$db_error = null;

foreach ($candidate_ports as $port) {
    try {
        $pdo = new PDO("mysql:host={$db_host};port={$port};dbname={$db_name};charset=utf8mb4", $db_user, $db_pass, [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,
        ]);
        break;
    } catch (PDOException $e) {
        $db_error = $e->getMessage();
    }
}

function formatRupiah($angka) {
    return 'Rp ' . number_format($angka, 0, ',', '.');
}

function getStatusBadge($status) {
    return ($status === 'Layak') 
        ? '<span style="color:#27ae60; font-weight:bold;">LAYAK</span>' 
        : '<span style="color:#c0392b; font-weight:bold;">TIDAK LAYAK</span>';
}
