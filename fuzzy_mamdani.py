"""
fuzzy_mamdani.py
Sistem Pendukung Keputusan (SPK) Bantuan Sosial menggunakan Metode Fuzzy Mamdani
Fungsi Keanggotaan: Trapesium
Defuzzifikasi: Centroid (Center of Gravity)
Output: Hanya LAYAK atau TIDAK LAYAK
"""

from typing import Dict, List, Any


def trapesium(x: float, a: float, b: float, c: float, d: float) -> float:
    """
    Fungsi Keanggotaan Kurva Trapesium.
    Mendukung bahu kiri (a == b) dan bahu kanan (c == d).
    """
    x = float(x)
    a, b, c, d = float(a), float(b), float(c), float(d)

    # Bahu Kiri: datar di sisi kiri (misal: Rendah / Kecil)
    if a == b:
        if x <= c:
            return 1.0
        elif c < x < d:
            return (d - x) / (d - c) if d != c else 0.0
        else:
            return 0.0

    # Bahu Kanan: datar di sisi kanan (misal: Tinggi / Besar)
    if c == d:
        if x <= a:
            return 0.0
        elif a < x < b:
            return (x - a) / (b - a) if b != a else 1.0
        else:
            return 1.0

    # Trapesium Standar (a < b <= c < d)
    if x <= a or x >= d:
        return 0.0
    elif a < x < b:
        return (x - a) / (b - a)
    elif b <= x <= c:
        return 1.0
    elif c < x < d:
        return (d - x) / (d - c)
    return 0.0


# Parameter Default Sesuai database.sql
DEFAULT_PARAMETERS = {
    'penghasilan': {
        'Rendah': (0, 0, 1000000, 2000000),
        'Sedang': (1000000, 1500000, 2000000, 4000000),
        'Tinggi': (2000000, 4000000, 10000000, 10000000),
    },
    'ukuran_rumah': {
        'Kecil': (0, 0, 10, 15),
        'Sedang': (8, 12, 18, 22),
        'Besar': (18, 25, 50, 500),
    },
    'jumlah_anak': {
        'Sedikit': (0, 0, 2, 3),
        'Sedang': (2, 3, 4, 5),
        'Banyak': (4, 5, 20, 20),
    },
    'usia': {
        'Muda': (0, 0, 25, 35),
        'Paruh_Baya': (25, 35, 50, 55),
        'Lanjut_Usia': (45, 55, 100, 100),
    },
    'jumlah_tanggungan': {
        'Sedikit': (0, 0, 2, 3),
        'Sedang': (2, 3, 4, 5),
        'Banyak': (4, 5, 20, 20),
    },
    'kelayakan': {
        'Tidak_Layak': (0, 0, 40, 60),
        'Layak': (40, 60, 100, 100),
    }
}

# 15 Rule Base Default
DEFAULT_RULES = [
    {'kode': 'R1',  'penghasilan': 'Rendah', 'jumlah_anak': 'Banyak',  'ukuran_rumah': 'Kecil',  'usia': 'Lanjut_Usia', 'jumlah_tanggungan': 'Banyak',  'output': 'Layak'},
    {'kode': 'R2',  'penghasilan': 'Rendah', 'jumlah_anak': 'Banyak',  'ukuran_rumah': 'Kecil',  'usia': 'Paruh_Baya',  'jumlah_tanggungan': 'Banyak',  'output': 'Layak'},
    {'kode': 'R3',  'penghasilan': 'Rendah', 'jumlah_anak': 'Sedang',  'ukuran_rumah': 'Kecil',  'usia': 'Lanjut_Usia', 'jumlah_tanggungan': 'Sedang',  'output': 'Layak'},
    {'kode': 'R4',  'penghasilan': 'Rendah', 'jumlah_anak': 'Sedikit', 'ukuran_rumah': 'Kecil',  'usia': 'Muda',        'jumlah_tanggungan': 'Sedikit', 'output': 'Layak'},
    {'kode': 'R5',  'penghasilan': 'Rendah', 'jumlah_anak': 'Sedang',  'ukuran_rumah': 'Sedang', 'usia': 'Paruh_Baya',  'jumlah_tanggungan': 'Sedang',  'output': 'Layak'},
    {'kode': 'R6',  'penghasilan': 'Sedang', 'jumlah_anak': 'Banyak',  'ukuran_rumah': 'Kecil',  'usia': 'Lanjut_Usia', 'jumlah_tanggungan': 'Banyak',  'output': 'Layak'},
    {'kode': 'R7',  'penghasilan': 'Sedang', 'jumlah_anak': 'Sedang',  'ukuran_rumah': 'Sedang', 'usia': 'Paruh_Baya',  'jumlah_tanggungan': 'Sedang',  'output': 'Layak'},
    {'kode': 'R8',  'penghasilan': 'Sedang', 'jumlah_anak': 'Sedikit', 'ukuran_rumah': 'Sedang', 'usia': 'Paruh_Baya',  'jumlah_tanggungan': 'Sedikit', 'output': 'Tidak_Layak'},
    {'kode': 'R9',  'penghasilan': 'Sedang', 'jumlah_anak': 'Banyak',  'ukuran_rumah': 'Besar',  'usia': 'Paruh_Baya',  'jumlah_tanggungan': 'Sedang',  'output': 'Layak'},
    {'kode': 'R10', 'penghasilan': 'Sedang', 'jumlah_anak': 'Sedikit', 'ukuran_rumah': 'Besar',  'usia': 'Muda',        'jumlah_tanggungan': 'Sedikit', 'output': 'Tidak_Layak'},
    {'kode': 'R11', 'penghasilan': 'Tinggi', 'jumlah_anak': 'Sedikit', 'ukuran_rumah': 'Besar',  'usia': 'Muda',        'jumlah_tanggungan': 'Sedikit', 'output': 'Tidak_Layak'},
    {'kode': 'R12', 'penghasilan': 'Tinggi', 'jumlah_anak': 'Sedang',  'ukuran_rumah': 'Besar',  'usia': 'Paruh_Baya',  'jumlah_tanggungan': 'Sedikit', 'output': 'Tidak_Layak'},
    {'kode': 'R13', 'penghasilan': 'Tinggi', 'jumlah_anak': 'Banyak',  'ukuran_rumah': 'Sedang', 'usia': 'Lanjut_Usia', 'jumlah_tanggungan': 'Banyak',  'output': 'Tidak_Layak'},
    {'kode': 'R14', 'penghasilan': 'Tinggi', 'jumlah_anak': 'Sedikit', 'ukuran_rumah': 'Sedang', 'usia': 'Lanjut_Usia', 'jumlah_tanggungan': 'Sedang',  'output': 'Tidak_Layak'},
    {'kode': 'R15', 'penghasilan': 'Rendah', 'jumlah_anak': 'Sedikit', 'ukuran_rumah': 'Sedang', 'usia': 'Muda',        'jumlah_tanggungan': 'Sedikit', 'output': 'Layak'},
]


class FuzzyMamdani:
    def __init__(self, parameters: Dict = None, rules: List[Dict] = None):
        self.parameters = parameters or DEFAULT_PARAMETERS
        self.rules = rules or DEFAULT_RULES

    def fuzzifikasi_variabel(self, nama_variabel: str, nilai: float) -> Dict[str, float]:
        """Menghitung derajat keanggotaan (mu) untuk suatu variabel."""
        hasil = {}
        if nama_variabel in self.parameters:
            for kategori, (a, b, c, d) in self.parameters[nama_variabel].items():
                hasil[kategori] = round(trapesium(nilai, a, b, c, d), 4)
        return hasil

    def evaluate(self, inputs: Dict[str, float]) -> Dict[str, Any]:
        """
        Menjalankan proses inferensi Fuzzy Mamdani lengkap:
        1. Fuzzifikasi
        2. Evaluasi Rule (Operator MIN)
        3. Agregasi Implikasi (Operator MAX)
        4. Defuzzifikasi Centroid
        """
        penghasilan = float(inputs.get('penghasilan_perbulan', 0))
        jumlah_anak = float(inputs.get('jumlah_anak', 0))
        ukuran_rumah = float(inputs.get('ukuran_rumah', 0))
        usia = float(inputs.get('usia', 0))
        jumlah_tanggungan = float(inputs.get('jumlah_tanggungan', 0))

        # 1. Fuzzifikasi setiap variabel
        mu_penghasilan = self.fuzzifikasi_variabel('penghasilan', penghasilan)
        mu_anak = self.fuzzifikasi_variabel('jumlah_anak', jumlah_anak)
        mu_rumah = self.fuzzifikasi_variabel('ukuran_rumah', ukuran_rumah)
        mu_usia = self.fuzzifikasi_variabel('usia', usia)
        mu_tanggungan = self.fuzzifikasi_variabel('jumlah_tanggungan', jumlah_tanggungan)

        fuzzifikasi_detail = {
            'penghasilan': mu_penghasilan,
            'jumlah_anak': mu_anak,
            'ukuran_rumah': mu_rumah,
            'usia': mu_usia,
            'jumlah_tanggungan': mu_tanggungan,
        }

        # 2. Evaluasi 15 Rule Base (MIN)
        active_rules = []
        all_rules_eval = []
        agregasi = {'Tidak_Layak': 0.0, 'Layak': 0.0}

        for rule in self.rules:
            kode = rule['kode']
            val_penghasilan = mu_penghasilan.get(rule['penghasilan'], 0.0)
            val_anak = mu_anak.get(rule['jumlah_anak'], 0.0)
            val_rumah = mu_rumah.get(rule['ukuran_rumah'], 0.0)
            val_usia = mu_usia.get(rule['usia'], 0.0)
            val_tanggungan = mu_tanggungan.get(rule['jumlah_tanggungan'], 0.0)

            # Implikasi Mamdani: operator AND menggunakan MIN
            alpha = min(val_penghasilan, val_anak, val_rumah, val_usia, val_tanggungan)
            alpha = round(alpha, 4)

            rule_info = {
                'kode_rule': kode,
                'penghasilan': {'kategori': rule['penghasilan'], 'mu': val_penghasilan},
                'jumlah_anak': {'kategori': rule['jumlah_anak'], 'mu': val_anak},
                'ukuran_rumah': {'kategori': rule['ukuran_rumah'], 'mu': val_rumah},
                'usia': {'kategori': rule['usia'], 'mu': val_usia},
                'jumlah_tanggungan': {'kategori': rule['jumlah_tanggungan'], 'mu': val_tanggungan},
                'keputusan_output': rule['output'],
                'alpha': alpha
            }

            all_rules_eval.append(rule_info)

            if alpha > 0:
                active_rules.append(rule_info)
                # 3. Agregasi MAX
                out = rule['output']
                if out in agregasi:
                    agregasi[out] = max(agregasi[out], alpha)

        # 4. Defuzzifikasi Centroid (Titik Pusat Area)
        # Domain kelayakan: [0, 100] dengan sampling langkah 0.5
        param_tl = self.parameters['kelayakan']['Tidak_Layak']
        param_l = self.parameters['kelayakan']['Layak']

        sum_numerator = 0.0
        sum_denominator = 0.0

        # Titik potong implikasi
        a_tl = agregasi['Tidak_Layak']
        a_l = agregasi['Layak']

        # Sampling nilai z dari 0 hingga 100
        z_step = 0.5
        steps = int(100 / z_step) + 1

        for i in range(steps):
            z = i * z_step
            # mu untuk Tidak_Layak
            mu_tl_z = min(a_tl, trapesium(z, *param_tl))
            # mu untuk Layak
            mu_l_z = min(a_l, trapesium(z, *param_l))
            # Komposisi agregasi (MAX)
            mu_gabungan = max(mu_tl_z, mu_l_z)

            sum_numerator += z * mu_gabungan
            sum_denominator += mu_gabungan

        if sum_denominator > 0:
            skor_defuzzifikasi = round(sum_numerator / sum_denominator, 2)
        else:
            # Jika tidak ada rule yang aktif sama sekali
            skor_defuzzifikasi = 50.0

        # Penentuan Status Keputusan
        if a_l > 0 and a_tl == 0:
            status_keputusan = 'Layak'
        elif a_tl > 0 and a_l == 0:
            status_keputusan = 'Tidak_Layak'
        elif skor_defuzzifikasi >= 50.0:
            status_keputusan = 'Layak'
        else:
            status_keputusan = 'Tidak_Layak'

        return {
            'inputs': inputs,
            'fuzzifikasi': fuzzifikasi_detail,
            'active_rules': active_rules,
            'all_rules': all_rules_eval,
            'agregasi': agregasi,
            'skor_defuzzifikasi': skor_defuzzifikasi,
            'status_keputusan': status_keputusan
        }


if __name__ == '__main__':
    # Contoh Pengujian Langsung dari Terminal
    evaluator = FuzzyMamdani()

    test_data = {
        'penghasilan_perbulan': 950000,
        'jumlah_anak': 3,
        'ukuran_rumah': 9,
        'usia': 48,
        'jumlah_tanggungan': 4
    }

    hasil = evaluator.evaluate(test_data)
    print("=" * 60)
    print("  HASIL EVALUASI SPK BANSOS FUZZY MAMDANI (PYTHON 3)")
    print("=" * 60)
    print(f"Penghasilan        : Rp {test_data['penghasilan_perbulan']:,}")
    print(f"Jumlah Anak        : {test_data['jumlah_anak']} orang")
    print(f"Ukuran Rumah       : {test_data['ukuran_rumah']} m²")
    print(f"Usia Pemohon       : {test_data['usia']} tahun")
    print(f"Jumlah Tanggungan  : {test_data['jumlah_tanggungan']} orang")
    print("-" * 60)
    print(f"Skor Defuzzifikasi : {hasil['skor_defuzzifikasi']} (Skala 0 - 100)")
    print(f"Status Keputusan   : {hasil['status_keputusan'].upper()}")
    print("-" * 60)
    print("Rule Aktif (Alpha > 0):")
    for r in hasil['active_rules']:
        print(f" * {r['kode_rule']}: Alpha = {r['alpha']} -> {r['keputusan_output']}")
    print("-" * 60)
    print(f"Agregasi Max Layak       : {hasil['agregasi']['Layak']}")
    print(f"Agregasi Max Tidak Layak : {hasil['agregasi']['Tidak_Layak']}")
    print("=" * 60)
