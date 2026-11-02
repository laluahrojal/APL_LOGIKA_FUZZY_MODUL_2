"""
cli.py
Antarmuka Terminal (CLI) Interaktif SPK Bansos Fuzzy Mamdani (Python 3)
Hanya menggunakan modul bawaan Python (Standard Library), tanpa perlu library eksternal.
"""

import sys
from fuzzy_mamdani import FuzzyMamdani
import db_manager


def format_rupiah(angka: float) -> str:
    return f"Rp {int(angka):,}".replace(',', '.')


def menu_evaluasi(evaluator: FuzzyMamdani):
    print("\n" + "=" * 55)
    print("   INPUT DATA PENGAJUAN BANTUAN SOSIAL")
    print("=" * 55)

    try:
        nik = input("1. NIK (16 digit)                 : ").strip()
        nama = input("2. Nama Lengkap                   : ").strip()
        alamat = input("3. Alamat Lengkap                 : ").strip()
        penghasilan = float(input("4. Penghasilan Perbulan (Rp)      : ").strip())
        anak = int(input("5. Jumlah Anak (Orang)            : ").strip())
        rumah = float(input("6. Ukuran Rumah (m²)              : ").strip())
        usia = int(input("7. Usia Pemohon (Tahun)           : ").strip())
        tanggungan = int(input("8. Jumlah Tanggungan (Orang)      : ").strip())
    except ValueError:
        print("\n[!] Input tidak valid! Harap masukkan angka untuk kriteria.")
        return

    inputs = {
        'penghasilan_perbulan': penghasilan,
        'jumlah_anak': anak,
        'ukuran_rumah': rumah,
        'usia': usia,
        'jumlah_tanggungan': tanggungan
    }

    hasil = evaluator.evaluate(inputs)

    # Simpan ke database
    id_p = db_manager.simpan_pengajuan(
        nik=nik,
        nama_lengkap=nama,
        alamat=alamat,
        penghasilan=penghasilan,
        anak=anak,
        rumah=rumah,
        usia=usia,
        tanggungan=tanggungan,
        skor_z=hasil['skor_defuzzifikasi'],
        status_keputusan=hasil['status_keputusan']
    )

    print("\n" + "=" * 55)
    print("   HASIL KEPUTUSAN KELAYAKAN BANSOS (FUZZY MAMDANI)")
    print("=" * 55)
    print(f"ID Pengajuan        : #{id_p}")
    print(f"Nama Pemohon        : {nama} (NIK: {nik})")
    print(f"Alamat              : {alamat}")
    print(f"Penghasilan         : {format_rupiah(penghasilan)}")
    print(f"Jumlah Anak         : {anak} orang")
    print(f"Ukuran Rumah        : {rumah} m²")
    print(f"Usia Pemohon        : {usia} tahun")
    print(f"Jumlah Tanggungan   : {tanggungan} orang")
    print("-" * 55)
    print(f"Skor Defuzzifikasi  : {hasil['skor_defuzzifikasi']} / 100")
    if hasil['status_keputusan'] == 'Layak':
        print("Status Keputusan    : [ LAYAK MENERIMA BANTUAN SOSIAL ]")
    else:
        print("Status Keputusan    : [ TIDAK LAYAK ]")
    print("-" * 55)
    print("Daftar Rule Base yang Aktif (Alpha > 0):")
    if hasil['active_rules']:
        for r in hasil['active_rules']:
            print(f"  * {r['kode_rule']}: Alpha = {r['alpha']} -> {r['keputusan_output']}")
    else:
        print("  (Tidak ada rule aktif)")
    print("-" * 55)
    print(f"Agregasi Max Layak       : {hasil['agregasi']['Layak']}")
    print(f"Agregasi Max Tidak Layak : {hasil['agregasi']['Tidak_Layak']}")
    print("=" * 55)


def menu_lihat_data():
    pengajuan_list = db_manager.get_all_pengajuan()
    print("\n" + "=" * 80)
    print("   DAFTAR PENGAJUAN BANTUAN SOSIAL DALAM DATABASE")
    print("=" * 80)

    if not pengajuan_list:
        print("  Belum ada data pengajuan tersimpan.")
    else:
        print(f"{'No':<4} {'NIK':<18} {'Nama':<22} {'Gaji':<14} {'Skor Z':<8} {'Keputusan':<12}")
        print("-" * 80)
        for i, row in enumerate(pengajuan_list, 1):
            gaji_str = format_rupiah(row['penghasilan_perbulan'])
            z_str = f"{row['skor_defuzzifikasi']:.2f}" if row['skor_defuzzifikasi'] else "-"
            print(f"{i:<4} {row['nik']:<18} {row['nama_lengkap'][:20]:<22} {gaji_str:<14} {z_str:<8} {row['status_keputusan']:<12}")
    print("=" * 80)


def menu_statistik():
    stats = db_manager.get_statistics()
    total = stats['total']
    print("\n" + "=" * 55)
    print(f"   STATISTIK DATA PENGAJUAN BANSOS (TOTAL: {total})")
    print("=" * 55)
    print(f"Layak Menerima Bansos : {stats['keputusan']['Layak']} orang")
    print(f"Tidak Layak           : {stats['keputusan']['Tidak_Layak']} orang")
    print("-" * 55)
    print("Penghasilan:")
    for k, v in stats['penghasilan'].items():
        print(f"  - {k:<10}: {v} orang")
    print("Jumlah Anak:")
    for k, v in stats['anak'].items():
        print(f"  - {k:<10}: {v} orang")
    print("Ukuran Rumah:")
    for k, v in stats['rumah'].items():
        print(f"  - {k:<10}: {v} orang")
    print("Usia Pemohon:")
    for k, v in stats['usia'].items():
        print(f"  - {k:<10}: {v} orang")
    print("Jumlah Tanggungan:")
    for k, v in stats['tanggungan'].items():
        print(f"  - {k:<10}: {v} orang")
    print("=" * 55)


def main():
    evaluator = FuzzyMamdani()

    while True:
        print("\n" + "#" * 55)
        print("   SISTEM PENDUKUNG KEPUTUSAN BANSOS (FUZZY MAMDANI)")
        print("   Versi Python 3 (CLI Terminal)")
        print("#" * 55)
        print("1. Hitung Kelayakan Bansos (Input Pemohon Baru)")
        print("2. Lihat Seluruh Data Pengajuan")
        print("3. Lihat Statistik & Distribusi")
        print("4. Keluar")
        print("-" * 55)

        pilihan = input("Pilih menu (1-4): ").strip()
        if pilihan == '1':
            menu_evaluasi(evaluator)
        elif pilihan == '2':
            menu_lihat_data()
        elif pilihan == '3':
            menu_statistik()
        elif pilihan == '4':
            print("\nTerima kasih telah menggunakan sistem SPK Bansos.")
            sys.exit(0)
        else:
            print("[!] Pilihan tidak tersedia, silakan pilih 1 - 4.")


if __name__ == '__main__':
    main()
