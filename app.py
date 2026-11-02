"""
app.py
Aplikasi Web Sistem Pendukung Keputusan (SPK) Bantuan Sosial
Metode: Fuzzy Mamdani (Python 3 + Flask + SQLite)
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import db_manager
from fuzzy_mamdani import FuzzyMamdani

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Inisialisasi evaluator Fuzzy
evaluator = FuzzyMamdani()


@app.route('/', methods=['GET', 'POST'])
def index():
    """Halaman Form Input Pengunjung & Hasil Keputusan Fuzzy Mamdani."""
    hasil = None
    form_data = None

    if request.method == 'POST':
        nik = request.form.get('nik', '').strip()
        nama_lengkap = request.form.get('nama_lengkap', '').strip()
        alamat = request.form.get('alamat', '').strip()
        penghasilan = request.form.get('penghasilan_perbulan', '').strip()
        jumlah_anak = request.form.get('jumlah_anak', '').strip()
        ukuran_rumah = request.form.get('ukuran_rumah', '').strip()
        usia = request.form.get('usia', '').strip()
        jumlah_tanggungan = request.form.get('jumlah_tanggungan', '').strip()

        form_data = {
            'nik': nik,
            'nama_lengkap': nama_lengkap,
            'alamat': alamat,
            'penghasilan_perbulan': penghasilan,
            'jumlah_anak': jumlah_anak,
            'ukuran_rumah': ukuran_rumah,
            'usia': usia,
            'jumlah_tanggungan': jumlah_tanggungan
        }

        # Validasi kelengkapan form
        if not all([nik, nama_lengkap, alamat, penghasilan != '', jumlah_anak != '',
                    ukuran_rumah != '', usia != '', jumlah_tanggungan != '']):
            flash('Harap lengkapi semua isian formulir!', 'danger')
        else:
            try:
                inputs_fuzzy = {
                    'penghasilan_perbulan': float(penghasilan),
                    'jumlah_anak': int(jumlah_anak),
                    'ukuran_rumah': float(ukuran_rumah),
                    'usia': int(usia),
                    'jumlah_tanggungan': int(jumlah_tanggungan)
                }

                # Evaluasi Fuzzy Mamdani
                hasil = evaluator.evaluate(inputs_fuzzy)

                # Simpan ke Database SQLite
                db_manager.simpan_pengajuan(
                    nik=nik,
                    nama_lengkap=nama_lengkap,
                    alamat=alamat,
                    penghasilan=inputs_fuzzy['penghasilan_perbulan'],
                    anak=inputs_fuzzy['jumlah_anak'],
                    rumah=inputs_fuzzy['ukuran_rumah'],
                    usia=inputs_fuzzy['usia'],
                    tanggungan=inputs_fuzzy['jumlah_tanggungan'],
                    skor_z=hasil['skor_defuzzifikasi'],
                    status_keputusan=hasil['status_keputusan']
                )

                flash('Data pemohon berhasil disimpan dan dinilai!', 'success')
            except Exception as e:
                flash(f'Terjadi kesalahan saat memproses data: {str(e)}', 'danger')

    return render_template('index.html', hasil=hasil, form_data=form_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Halaman Login Administrator."""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        admin = db_manager.verify_admin(username, password)
        if admin:
            session['admin_logged_in'] = True
            session['admin_id'] = admin['id_admin']
            session['admin_user'] = admin['username']
            session['admin_nama'] = admin['nama_petugas']
            flash('Login berhasil! Selamat datang di Panel Administrator.', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Username atau password salah! Gunakan akun default: admin / admin123', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout Administrator."""
    session.clear()
    flash('Anda telah berhasil keluar (logout).', 'success')
    return redirect(url_for('login'))


@app.route('/admin')
def admin():
    """Halaman Dashboard Administrator: Grafik Statistik & Kelola Data."""
    if not session.get('admin_logged_in'):
        flash('Silakan login terlebih dahulu untuk mengakses panel admin.', 'danger')
        return redirect(url_for('login'))

    pengajuan_list = db_manager.get_all_pengajuan()
    stats = db_manager.get_statistics()
    return render_template('admin.html', pengajuan_list=pengajuan_list, stats=stats)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """Halaman Edit Data Pemohon & Hitung Ulang Fuzzy."""
    if not session.get('admin_logged_in'):
        flash('Silakan login terlebih dahulu.', 'danger')
        return redirect(url_for('login'))

    pengajuan = db_manager.get_pengajuan_by_id(id)
    if not pengajuan:
        flash('Data pengajuan tidak ditemukan!', 'danger')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        nama_lengkap = request.form.get('nama_lengkap', '').strip()
        alamat = request.form.get('alamat', '').strip()
        penghasilan = float(request.form.get('penghasilan_perbulan', 0))
        anak = int(request.form.get('jumlah_anak', 0))
        rumah = float(request.form.get('ukuran_rumah', 0))
        usia = int(request.form.get('usia', 0))
        tanggungan = int(request.form.get('jumlah_tanggungan', 0))

        if not nama_lengkap or not alamat:
            flash('Nama lengkap dan alamat wajib diisi!', 'danger')
        else:
            # Hitung ulang Fuzzy Mamdani dengan kriteria baru
            inputs_fuzzy = {
                'penghasilan_perbulan': penghasilan,
                'jumlah_anak': anak,
                'ukuran_rumah': rumah,
                'usia': usia,
                'jumlah_tanggungan': tanggungan
            }
            hasil = evaluator.evaluate(inputs_fuzzy)

            # Update database
            success = db_manager.update_pengajuan(
                id_pengajuan=id,
                nama_lengkap=nama_lengkap,
                alamat=alamat,
                penghasilan=penghasilan,
                anak=anak,
                rumah=rumah,
                usia=usia,
                tanggungan=tanggungan,
                skor_z=hasil['skor_defuzzifikasi'],
                status_keputusan=hasil['status_keputusan']
            )

            if success:
                flash('Data berhasil diubah dan nilai Fuzzy telah dihitung ulang!', 'success')
                return redirect(url_for('admin'))
            else:
                flash('Gagal memperbarui data pengajuan.', 'danger')

    return render_template('edit.html', pengajuan=pengajuan)


@app.route('/hapus/<int:id>')
def hapus(id):
    """Menghapus Data Pengajuan Bansos."""
    if not session.get('admin_logged_in'):
        flash('Silakan login terlebih dahulu.', 'danger')
        return redirect(url_for('login'))

    success = db_manager.delete_pengajuan(id)
    if success:
        flash('Data pengajuan berhasil dihapus dari sistem.', 'success')
    else:
        flash('Gagal menghapus data pengajuan.', 'danger')

    return redirect(url_for('admin'))


@app.route('/api/evaluasi', methods=['POST'])
def api_evaluasi():
    """API Endpoint JSON untuk mengevaluasi data secara langsung."""
    data = request.get_json() or {}
    try:
        inputs = {
            'penghasilan_perbulan': float(data.get('penghasilan_perbulan', 0)),
            'jumlah_anak': int(data.get('jumlah_anak', 0)),
            'ukuran_rumah': float(data.get('ukuran_rumah', 0)),
            'usia': int(data.get('usia', 0)),
            'jumlah_tanggungan': int(data.get('jumlah_tanggungan', 0))
        }
        hasil = evaluator.evaluate(inputs)
        return jsonify({
            'status': 'success',
            'data': hasil
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


if __name__ == '__main__':
    print("=" * 60)
    print("  SPK BANTUAN SOSIAL - FUZZY MAMDANI (PYTHON 3)")
    print("=" * 60)
    print("  Buka browser dan akses:")
    print("  http://127.0.0.1:5000")
    print("=" * 60)
    print("  Login Admin : admin / admin123")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
