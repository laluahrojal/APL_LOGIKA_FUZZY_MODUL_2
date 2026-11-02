"""
gui_app.py
Aplikasi Desktop GUI SPK Bantuan Sosial (Fuzzy Mamdani)
100% Murni Python (Tkinter) - Tanpa HTML, Tanpa CSS, Tanpa Web Browser!
"""

import tkinter as tk
from tkinter import ttk, messagebox
import db_manager
from fuzzy_mamdani import FuzzyMamdani


class SPKBansosGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SPK Bantuan Sosial - Fuzzy Mamdani (Python GUI)")
        self.root.geometry("980x720")
        self.root.minsize(850, 600)

        # Inisialisasi Evaluator Fuzzy Mamdani
        self.evaluator = FuzzyMamdani()

        # Konfigurasi Ttk Style
        self.setup_styles()

        # Tab Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Form Input & Hasil
        self.tab_form = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_form, text="📝 Input & Penilaian Bansos")
        self.build_tab_form()

        # Tab 2: Kelola Data Pemohon (Admin)
        self.tab_data = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_data, text="📋 Kelola Data Pemohon")
        self.build_tab_data()

        # Tab 3: Grafik & Statistik
        self.tab_stats = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_stats, text="📊 Grafik & Statistik")
        self.build_tab_stats()

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        style.configure('TNotebook.Tab', font=('Segoe UI', 10, 'bold'), padding=[12, 6])
        style.configure('Heading.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#1e3a8a')
        style.configure('SubHeading.TLabel', font=('Segoe UI', 9), foreground='#64748b')
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'), background='#2563eb', foreground='#ffffff')
        style.configure('Danger.TButton', font=('Segoe UI', 9, 'bold'), background='#dc2626', foreground='#ffffff')
        style.configure('Warning.TButton', font=('Segoe UI', 9, 'bold'), background='#d97706', foreground='#ffffff')

    # =========================================================================
    # TAB 1: FORM INPUT & HASIL EVALUASI FUZZY
    # =========================================================================
    def build_tab_form(self):
        # Frame Kontainer Kiri (Form) & Kanan (Hasil)
        container = ttk.PanedWindow(self.tab_form, orient=tk.HORIZONTAL)
        container.pack(fill=tk.BOTH, expand=True)

        # --- FRAME FORM INPUT (KIRI) ---
        frame_input = ttk.LabelFrame(container, text=" Formulir Data Calon Penerima Bansos ", padding=14)
        container.add(frame_input, weight=1)

        labels = [
            ("1. NIK (16 Digit)", "nik", "Contoh: 3201012508780002"),
            ("2. Nama Lengkap", "nama_lengkap", "Contoh: Ibu Aminah Kusuma"),
            ("3. Alamat Lengkap", "alamat", "Contoh: Kp. Babakan RT 02 / RW 01"),
            ("4. Penghasilan Perbulan (Rp)", "penghasilan", "Batas: Rendah (<=1jt), Sedang (1jt-2jt), Tinggi (>=4jt)"),
            ("5. Jumlah Anak (Orang)", "jumlah_anak", "Batas: Sedikit (<=2), Sedang (3-5), Banyak (>5)"),
            ("6. Ukuran Rumah (m²)", "ukuran_rumah", "Batas: Kecil (1-10m²), Sedang (10-20m²), Besar (20-50m²)"),
            ("7. Usia Pemohon (Tahun)", "usia", "Batas: Muda (<=35), Paruh Baya (30-55), Lansia (>=50)"),
            ("8. Jumlah Tanggungan (Orang)", "jumlah_tanggungan", "Batas: Sedikit (<=2), Sedang (3-5), Banyak (>5)")
        ]

        self.form_entries = {}
        for row_idx, (text, key, hint) in enumerate(labels):
            lbl = ttk.Label(frame_input, text=text, font=('Segoe UI', 9, 'bold'))
            lbl.grid(row=row_idx * 2, column=0, sticky='w', pady=(4, 1))

            entry = ttk.Entry(frame_input, font=('Segoe UI', 10))
            entry.grid(row=row_idx * 2 + 1, column=0, sticky='ew', pady=(0, 2))
            self.form_entries[key] = entry

        frame_input.columnconfigure(0, weight=1)

        # Tombol Proses
        btn_box = ttk.Frame(frame_input)
        btn_box.grid(row=len(labels) * 2, column=0, sticky='ew', pady=(12, 0))

        btn_proses = tk.Button(
            btn_box, text="🚀 PROSES & CEK KELAYAKAN BANSOS",
            bg="#2563eb", fg="white", font=('Segoe UI', 10, 'bold'),
            padx=10, pady=8, cursor="hand2", relief=tk.FLAT,
            command=self.proses_evaluasi
        )
        btn_proses.pack(fill=tk.X, side=tk.TOP, pady=2)

        btn_demo = ttk.Button(btn_box, text="Isi Data Contoh Demo", command=self.isi_data_demo)
        btn_demo.pack(fill=tk.X, side=tk.TOP, pady=2)

        # --- FRAME HASIL EVALUASI (KANAN) ---
        self.frame_hasil = ttk.LabelFrame(container, text=" Hasil Keputusan Kelayakan (Fuzzy Mamdani) ", padding=14)
        container.add(self.frame_hasil, weight=1)

        # Badge Keputusan
        self.lbl_status_badge = tk.Label(
            self.frame_hasil, text="SILAKAN ISI FORMULIR & KLIK PROSES",
            bg="#e2e8f0", fg="#475569", font=('Segoe UI', 12, 'bold'),
            padx=14, pady=10, relief=tk.RIDGE
        )
        self.lbl_status_badge.pack(fill=tk.X, pady=(0, 10))

        # Skor Defuzzifikasi Z
        frame_skor = ttk.Frame(self.frame_hasil)
        frame_skor.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_skor, text="Skor Defuzzifikasi (Centroid Z):", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        self.lbl_skor_z = ttk.Label(frame_skor, text="-", font=('Segoe UI', 12, 'bold'), foreground='#2563eb')
        self.lbl_skor_z.pack(side=tk.RIGHT)

        # Ringkasan Agregasi MAX
        frame_agregasi = ttk.Frame(self.frame_hasil)
        frame_agregasi.pack(fill=tk.X, pady=(0, 10))
        self.lbl_agregasi = ttk.Label(
            frame_agregasi, text="Max Alpha (Layak): -  |  Max Alpha (Tidak Layak): -",
            font=('Segoe UI', 9), foreground="#334155"
        )
        self.lbl_agregasi.pack(fill=tk.X)

        # Tabel Rule Base yang Aktif (Alpha > 0)
        ttk.Label(self.frame_hasil, text="Daftar Rule Base yang Aktif (Alpha > 0):", font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(6, 2))

        cols = ('rule', 'kondisi', 'output', 'alpha')
        self.tree_rules = ttk.Treeview(self.frame_hasil, columns=cols, show='headings', height=7)
        self.tree_rules.heading('rule', text='Rule')
        self.tree_rules.heading('kondisi', text='Kondisi (IF Antecedent)')
        self.tree_rules.heading('output', text='Output (THEN)')
        self.tree_rules.heading('alpha', text='Alpha (MIN)')

        self.tree_rules.column('rule', width=50, anchor='center')
        self.tree_rules.column('kondisi', width=220)
        self.tree_rules.column('output', width=80, anchor='center')
        self.tree_rules.column('alpha', width=80, anchor='center')

        self.tree_rules.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        # Rincian Derajat Keanggotaan (Mu)
        self.text_detail = tk.Text(self.frame_hasil, height=4, font=('Consolas', 9), bg='#f8fafc', relief=tk.SOLID, bd=1)
        self.text_detail.pack(fill=tk.X)

    def isi_data_demo(self):
        demo = {
            'nik': '3201012508780002',
            'nama_lengkap': 'Ibu Aminah Kusuma',
            'alamat': 'Kp. Babakan RT 02 / RW 01',
            'penghasilan': '950000',
            'jumlah_anak': '3',
            'ukuran_rumah': '9',
            'usia': '48',
            'jumlah_tanggungan': '4'
        }
        for k, v in demo.items():
            self.form_entries[k].delete(0, tk.END)
            self.form_entries[k].insert(0, v)

    def proses_evaluasi(self):
        # Ambil input
        data = {k: v.get().strip() for k, v in self.form_entries.items()}

        for k, v in data.items():
            if not v:
                messagebox.showwarning("Peringatan", "Harap lengkapi semua isian formulir!")
                return

        try:
            penghasilan = float(data['penghasilan'])
            anak = int(data['jumlah_anak'])
            rumah = float(data['ukuran_rumah'])
            usia = int(data['usia'])
            tanggungan = int(data['jumlah_tanggungan'])
        except ValueError:
            messagebox.showerror("Error", "Penghasilan, anak, ukuran rumah, usia, dan tanggungan harus berupa angka!")
            return

        # Hitung Fuzzy Mamdani
        inputs_fuzzy = {
            'penghasilan_perbulan': penghasilan,
            'jumlah_anak': anak,
            'ukuran_rumah': rumah,
            'usia': usia,
            'jumlah_tanggungan': tanggungan
        }
        hasil = self.evaluator.evaluate(inputs_fuzzy)

        # Simpan ke Database SQLite
        try:
            id_p = db_manager.simpan_pengajuan(
                nik=data['nik'],
                nama_lengkap=data['nama_lengkap'],
                alamat=data['alamat'],
                penghasilan=penghasilan,
                anak=anak,
                rumah=rumah,
                usia=usia,
                tanggungan=tanggungan,
                skor_z=hasil['skor_defuzzifikasi'],
                status_keputusan=hasil['status_keputusan']
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Gagal menyimpan ke database: {e}")
            return

        # Update Tampilan Hasil
        status = hasil['status_keputusan']
        skor_z = hasil['skor_defuzzifikasi']

        if status == 'Layak':
            self.lbl_status_badge.config(
                text="✅ LAYAK MENERIMA BANTUAN SOSIAL",
                bg="#15803d", fg="#ffffff"
            )
        else:
            self.lbl_status_badge.config(
                text="❌ TIDAK LAYAK MENERIMA BANSOS",
                bg="#b91c1c", fg="#ffffff"
            )

        self.lbl_skor_z.config(text=f"{skor_z:.2f} / 100")
        self.lbl_agregasi.config(
            text=f"Max Alpha (Layak): {hasil['agregasi']['Layak']:.4f}  |  Max Alpha (Tidak Layak): {hasil['agregasi']['Tidak_Layak']:.4f}"
        )

        # Isi Treeview Rule Aktif
        for item in self.tree_rules.get_children():
            self.tree_rules.delete(item)

        for r in hasil['active_rules']:
            kondisi = f"Gaji:{r['penghasilan']['kategori']}, Anak:{r['jumlah_anak']['kategori']}, Rumah:{r['ukuran_rumah']['kategori']}"
            self.tree_rules.insert('', tk.END, values=(
                r['kode_rule'], kondisi, r['keputusan_output'], f"{r['alpha']:.4f}"
            ))

        # Tampilkan rincian derajat keanggotaan
        fuz = hasil['fuzzifikasi']
        detail_str = (
            f"Derajat Keanggotaan (Mu):\n"
            f"Penghasilan: {fuz['penghasilan']} | Anak: {fuz['jumlah_anak']}\n"
            f"Rumah: {fuz['ukuran_rumah']} | Usia: {fuz['usia']} | Tanggungan: {fuz['jumlah_tanggungan']}"
        )
        self.text_detail.delete('1.0', tk.END)
        self.text_detail.insert('1.0', detail_str)

        messagebox.showinfo("Sukses", f"Data #{id_p} ({data['nama_lengkap']}) berhasil dinilai!\nStatus: {status.upper()} (Skor Z: {skor_z:.2f})")
        self.refresh_table_data()

    # =========================================================================
    # TAB 2: KELOLA DATA PEMOHON (ADMIN)
    # =========================================================================
    def build_tab_data(self):
        # Toolbar atas
        toolbar = ttk.Frame(self.tab_data)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(toolbar, text="Daftar Data Pemohon Bantuan Sosial", font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)

        btn_refresh = ttk.Button(toolbar, text="🔄 Refresh Data", command=self.refresh_table_data)
        btn_refresh.pack(side=tk.RIGHT, padx=4)

        btn_hapus = ttk.Button(toolbar, text="🗑 Hapus Terpilih", style="Danger.TButton", command=self.hapus_terpilih)
        btn_hapus.pack(side=tk.RIGHT, padx=4)

        btn_edit = ttk.Button(toolbar, text="✏️ Edit Terpilih", style="Warning.TButton", command=self.buka_dialog_edit)
        btn_edit.pack(side=tk.RIGHT, padx=4)

        # Tabel Treeview
        cols = ('id', 'nik', 'nama', 'alamat', 'gaji', 'kriteria', 'skor_z', 'status')
        self.tree_data = ttk.Treeview(self.tab_data, columns=cols, show='headings', selectmode='browse')

        self.tree_data.heading('id', text='ID')
        self.tree_data.heading('nik', text='NIK')
        self.tree_data.heading('nama', text='Nama Lengkap')
        self.tree_data.heading('alamat', text='Alamat')
        self.tree_data.heading('gaji', text='Penghasilan')
        self.tree_data.heading('kriteria', text='Anak / Rumah / Usia / Tgg')
        self.tree_data.heading('skor_z', text='Skor Z')
        self.tree_data.heading('status', text='Keputusan')

        self.tree_data.column('id', width=45, anchor='center')
        self.tree_data.column('nik', width=130)
        self.tree_data.column('nama', width=160)
        self.tree_data.column('alamat', width=180)
        self.tree_data.column('gaji', width=110, anchor='e')
        self.tree_data.column('kriteria', width=160, anchor='center')
        self.tree_data.column('skor_z', width=70, anchor='center')
        self.tree_data.column('status', width=95, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tab_data, orient=tk.VERTICAL, command=self.tree_data.yview)
        self.tree_data.configure(yscroll=scrollbar.set)

        self.tree_data.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.refresh_table_data()

    def refresh_table_data(self):
        for item in self.tree_data.get_children():
            self.tree_data.delete(item)

        rows = db_manager.get_all_pengajuan()
        for r in rows:
            gaji_str = f"Rp {int(r['penghasilan_perbulan']):,}".replace(',', '.')
            kriteria_str = f"{r['jumlah_anak']} ank | {r['ukuran_rumah']}m² | {r['usia']}th | {r['jumlah_tanggungan']}tgg"
            z_str = f"{r['skor_defuzzifikasi']:.2f}" if r['skor_defuzzifikasi'] else "-"
            self.tree_data.insert('', tk.END, values=(
                r['id_pengajuan'], r['nik'], r['nama_lengkap'], r['alamat'],
                gaji_str, kriteria_str, z_str, r['status_keputusan']
            ))

    def hapus_terpilih(self):
        selected = self.tree_data.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih data pemohon pada tabel yang ingin dihapus.")
            return

        item = self.tree_data.item(selected[0])
        id_pengajuan = int(item['values'][0])
        nama = item['values'][2]

        if messagebox.askyesno("Konfirmasi Hapus", f"Apakah Anda yakin ingin menghapus data pengajuan #{id_pengajuan} ({nama})?"):
            db_manager.delete_pengajuan(id_pengajuan)
            messagebox.showinfo("Sukses", "Data berhasil dihapus dari database.")
            self.refresh_table_data()
            self.refresh_stats_canvas()

    def buka_dialog_edit(self):
        selected = self.tree_data.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih data pemohon pada tabel yang ingin diedit.")
            return

        item = self.tree_data.item(selected[0])
        id_pengajuan = int(item['values'][0])
        data = db_manager.get_pengajuan_by_id(id_pengajuan)
        if not data:
            messagebox.showerror("Error", "Data tidak ditemukan.")
            return

        # Modal Edit Window
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Pengajuan #{id_pengajuan} - {data['nama_lengkap']}")
        dialog.geometry("450x520")
        dialog.transient(self.root)
        dialog.grab_set()

        fields = [
            ("Nama Lengkap", "nama_lengkap", data['nama_lengkap']),
            ("Alamat", "alamat", data['alamat']),
            ("Penghasilan (Rp)", "penghasilan", str(int(data['penghasilan_perbulan']))),
            ("Jumlah Anak", "jumlah_anak", str(data['jumlah_anak'])),
            ("Ukuran Rumah (m²)", "ukuran_rumah", str(data['ukuran_rumah'])),
            ("Usia Pemohon", "usia", str(data['usia'])),
            ("Jumlah Tanggungan", "jumlah_tanggungan", str(data['jumlah_tanggungan']))
        ]

        edit_entries = {}
        for idx, (lbl_text, key, val) in enumerate(fields):
            ttk.Label(dialog, text=lbl_text, font=('Segoe UI', 9, 'bold')).pack(anchor='w', padx=18, pady=(8, 2))
            ent = ttk.Entry(dialog, font=('Segoe UI', 10))
            ent.insert(0, val)
            ent.pack(fill=tk.X, padx=18, pady=(0, 4))
            edit_entries[key] = ent

        def simpan_edit():
            try:
                gaji = float(edit_entries['penghasilan'].get())
                anak = int(edit_entries['jumlah_anak'].get())
                rumah = float(edit_entries['ukuran_rumah'].get())
                usia = int(edit_entries['usia'].get())
                tgg = int(edit_entries['jumlah_tanggungan'].get())
                nama = edit_entries['nama_lengkap'].get().strip()
                alamat = edit_entries['alamat'].get().strip()

                # Hitung ulang Fuzzy Mamdani
                fuzzy_inputs = {
                    'penghasilan_perbulan': gaji,
                    'jumlah_anak': anak,
                    'ukuran_rumah': rumah,
                    'usia': usia,
                    'jumlah_tanggungan': tgg
                }
                hasil = self.evaluator.evaluate(fuzzy_inputs)

                db_manager.update_pengajuan(
                    id_pengajuan=id_pengajuan,
                    nama_lengkap=nama,
                    alamat=alamat,
                    penghasilan=gaji,
                    anak=anak,
                    rumah=rumah,
                    usia=usia,
                    tanggungan=tgg,
                    skor_z=hasil['skor_defuzzifikasi'],
                    status_keputusan=hasil['status_keputusan']
                )

                messagebox.showinfo("Sukses", f"Data #{id_pengajuan} berhasil diperbarui!\nHasil baru: {hasil['status_keputusan']} (Skor Z: {hasil['skor_defuzzifikasi']:.2f})")
                dialog.destroy()
                self.refresh_table_data()
                self.refresh_stats_canvas()
            except Exception as ex:
                messagebox.showerror("Error", f"Gagal menyimpan perubahan: {ex}")

        btn_save = tk.Button(
            dialog, text="💾 Simpan Perubahan & Hitung Ulang",
            bg="#2563eb", fg="white", font=('Segoe UI', 10, 'bold'),
            padx=10, pady=8, relief=tk.FLAT, cursor="hand2", command=simpan_edit
        )
        btn_save.pack(fill=tk.X, padx=18, pady=(16, 0))

    # =========================================================================
    # TAB 3: GRAFIK & STATISTIK (CANVAS TKINTER MURNI)
    # =========================================================================
    def build_tab_stats(self):
        toolbar = ttk.Frame(self.tab_stats)
        toolbar.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(toolbar, text="Grafik Distribusi Kriteria & Keputusan Pemohon", font=('Segoe UI', 12, 'bold')).pack(side=tk.LEFT)

        btn_refresh = ttk.Button(toolbar, text="🔄 Perbarui Grafik", command=self.refresh_stats_canvas)
        btn_refresh.pack(side=tk.RIGHT)

        # Canvas untuk menggambar grafik batang murni Python
        self.canvas = tk.Canvas(self.tab_stats, bg="#ffffff", bd=1, relief=tk.SOLID)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Configure>", lambda e: self.refresh_stats_canvas())

    def draw_chart_bar(self, x, y, width, height, title, categories, colors):
        """Menggambar kartu grafik batang di canvas Tkinter."""
        # Background kartu
        self.canvas.create_rectangle(x, y, x + width, y + height, fill="#f8fafc", outline="#e2e8f0", width=1)
        # Header Judul
        self.canvas.create_text(x + 12, y + 16, text=title, font=('Segoe UI', 10, 'bold'), fill="#1e293b", anchor='w')

        total = sum(v for _, v in categories)
        bar_y = y + 42
        bar_spacing = 26
        max_bar_width = width - 150

        for idx, (label, val) in enumerate(categories):
            pct = (val / total * 100) if total > 0 else 0
            curr_bar_w = (pct / 100 * max_bar_width) if total > 0 else 0

            # Label teks
            self.canvas.create_text(x + 12, bar_y + 6, text=label, font=('Segoe UI', 8), fill="#334155", anchor='w')
            # Nilai & Persen
            self.canvas.create_text(x + width - 12, bar_y + 6, text=f"{val} ({pct:.0f}%)", font=('Segoe UI', 8, 'bold'), fill="#1e293b", anchor='e')

            # Bar background
            self.canvas.create_rectangle(x + 12, bar_y + 14, x + 12 + max_bar_width, bar_y + 22, fill="#e2e8f0", outline="")
            # Bar nilai
            color = colors[idx % len(colors)]
            if curr_bar_w > 0:
                self.canvas.create_rectangle(x + 12, bar_y + 14, x + 12 + curr_bar_w, bar_y + 22, fill=color, outline="")

            bar_y += bar_spacing

    def refresh_stats_canvas(self):
        self.canvas.delete("all")
        stats = db_manager.get_statistics()
        total = stats['total']

        w = self.canvas.winfo_width()
        if w < 200:
            w = 900

        # Ringkasan Total
        self.canvas.create_text(20, 20, text=f"Total Pengajuan Terdaftar: {total} Pemohon", font=('Segoe UI', 12, 'bold'), fill="#1e3a8a", anchor='w')

        # Grid 2 Kolom x 3 Baris
        card_w = (w - 60) // 2
        card_h = 145

        charts = [
            ("1. Penghasilan Perbulan", [('Rendah (<=1jt)', stats['penghasilan']['Rendah']), ('Sedang (1jt-2jt)', stats['penghasilan']['Sedang']), ('Tinggi (>=4jt)', stats['penghasilan']['Tinggi'])], ["#16a34a", "#f59e0b", "#dc2626"]),
            ("2. Jumlah Anak", [('Sedikit (<=2)', stats['anak']['Sedikit']), ('Sedang (3-5)', stats['anak']['Sedang']), ('Banyak (>5)', stats['anak']['Banyak'])], ["#2563eb", "#8b5cf6", "#ea580c"]),
            ("3. Ukuran Rumah", [('Kecil (1-10m²)', stats['rumah']['Kecil']), ('Sedang (10-20m²)', stats['rumah']['Sedang']), ('Besar (20-50m²)', stats['rumah']['Besar'])], ["#0d9488", "#eab308", "#e11d48"]),
            ("4. Usia Pemohon", [('Muda (<=35th)', stats['usia']['Muda']), ('Paruh Baya (30-55)', stats['usia']['Paruh_Baya']), ('Lansia (>=50th)', stats['usia']['Lansia'])], ["#0284c7", "#d97706", "#7c3aed"]),
            ("5. Jumlah Tanggungan", [('Sedikit (<=2)', stats['tanggungan']['Sedikit']), ('Sedang (3-5)', stats['tanggungan']['Sedang']), ('Banyak (>5)', stats['tanggungan']['Banyak'])], ["#059669", "#475569", "#b91c1c"]),
            ("6. Keputusan Kelayakan", [('Layak Menerima Bansos', stats['keputusan']['Layak']), ('Tidak Layak', stats['keputusan']['Tidak_Layak'])], ["#16a34a", "#dc2626"])
        ]

        start_y = 45
        for i, (title, cats, colors) in enumerate(charts):
            col = i % 2
            row = i // 2
            cx = 20 + col * (card_w + 20)
            cy = start_y + row * (card_h + 15)
            self.draw_chart_bar(cx, cy, card_w, card_h, title, cats, colors)


def main():
    root = tk.Tk()
    app = SPKBansosGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
