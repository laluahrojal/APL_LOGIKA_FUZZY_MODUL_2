<?php
/**
 * logout.php
 * Skrip Logout Sederhana
 */

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

$_SESSION = [];
session_unset();
session_destroy();

header("Location: login.php?msg=logout_sukses");
exit;
