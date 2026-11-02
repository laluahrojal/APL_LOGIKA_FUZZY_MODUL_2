"""
main.py
Titik Masuk Utama (Main Entry Point) SPK Bantuan Sosial - Fuzzy Mamdani
100% MURNI PYTHON - TANPA HTML, TANPA WEB BROWSER!

Cara Menjalankan:
1. Mode Tampilan Desktop (GUI):
   python main.py

2. Mode Terminal Interaktif (CLI):
   python main.py --cli
"""

import sys

def run_gui():
    try:
        import gui_app
        gui_app.main()
    except Exception as e:
        print(f"[!] Gagal membuka antarmuka GUI: {e}")
        print("[*] Beralih otomatis ke mode Terminal (CLI)...")
        run_cli()

def run_cli():
    import cli
    cli.main()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['--cli', '-c', 'cli']:
        run_cli()
    else:
        run_gui()
