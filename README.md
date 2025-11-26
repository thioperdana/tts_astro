# TTS Astro
**Teka-Teki Silang Nama Bintang**

TTS Astro adalah aplikasi permainan teka-teki silang (crossword) edukatif yang dirancang untuk mengenalkan nama-nama bintang dan konstelasi kepada anak-anak Indonesia. Aplikasi ini menyajikan cara yang menyenangkan untuk belajar astronomi melalui permainan kata.

## Fitur Utama

- **Database Bintang Luas**: Memuat 350+ nama bintang dari berbagai konstelasi dengan deskripsi yang edukatif, sederhana, dan mudah dipahami.
- **100% Bahasa Indonesia**: Antarmuka dan petunjuk permainan sepenuhnya dalam Bahasa Indonesia, ramah untuk anak-anak.
- **Generator Puzzle Otomatis**: Setiap permainan baru menghasilkan susunan teka-teki silang yang unik dan berbeda.
- **Sistem Penilaian**: Fitur scoring dan leaderboard untuk menyimpan skor tertinggi.
- **Simpan & Muat**: Fitur untuk menyimpan progres permainan dan melanjutkannya di lain waktu.
- **Tampilan Menarik**: Desain antarmuka bertema luar angkasa (dark mode) yang elegan dan responsif.
- **Navigasi Mudah**: Mendukung input keyboard dan navigasi panah yang intuitif.

## Persyaratan Sistem

- Python 3.12 atau lebih tinggi
- uv (Python package manager)

## Instalasi

### 1. Instalasi uv (jika belum terinstal)

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone atau Download Repository

Clone repository ini atau download sebagai ZIP dan ekstrak:
```bash
git clone <repository-url>
cd tts_astro
```

### 3. Instalasi Dependensi

uv akan secara otomatis membuat virtual environment dan menginstal semua dependensi yang diperlukan saat pertama kali menjalankan aplikasi.

### 4. Inisialisasi Database

Jalankan script scraper untuk mengisi database dengan data bintang:
```bash
uv run python scraper.py
```

Output yang diharapkan:
```
Reading nama_bintang.txt...
Found 350 stars from file.
Cleared existing data.
Database populated.
```

## Cara Menjalankan Aplikasi

### 1. Jalankan Server Development

```bash
uv run uvicorn main:app --reload --port 8000
```

Server akan berjalan di `http://localhost:8000`

### 2. Akses Aplikasi

Buka browser dan kunjungi:
```
http://localhost:8000
```

## Cara Bermain

1. Klik tombol **"Permainan Baru"** untuk memulai.
2. Lihat daftar petunjuk di sebelah kanan (Mendatar & Menurun).
3. Klik pada petunjuk atau kotak di grid untuk mulai mengetik.
4. Jawab teka-teki dengan nama bintang yang sesuai dengan petunjuk "Bintang di [Konstelasi]".
5. Klik **"Nilai"** untuk menghitung skor Anda.
6. Masukkan nama Anda untuk menyimpan ke leaderboard.
7. Gunakan tombol **"Simpan Permainan"** jika ingin beristirahat dan melanjutkannya nanti.

## Teknologi yang Digunakan

- **Backend**: Python, FastAPI, SQLModel (SQLite)
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (Vanilla)
- **Package Manager**: uv
- **Server**: Uvicorn

## Struktur Proyek

```
tts_astro/
├── data/
│   └── astro.db           # Database SQLite (menyimpan data bintang & game)
├── static/
│   ├── style.css          # Styling aplikasi (tema luar angkasa)
│   └── app.js             # Logika permainan (frontend)
├── templates/
│   └── index.html         # Halaman utama aplikasi
├── main.py                # Aplikasi utama FastAPI & API Endpoints
├── models.py              # Definisi model database (Star, Game)
├── generator.py           # Algoritma pembuat teka-teki silang
├── scraper.py             # Script untuk memproses data bintang
├── clean_stars.py         # Script untuk membersihkan data bintang
├── analyze_data.py        # Script untuk verifikasi data bintang
├── nama_bintang.txt       # Data nama bintang (sudah dibersihkan)
└── pyproject.toml         # Konfigurasi proyek & dependensi
```

## Mengelola Data Bintang

### Membersihkan Data (Opsional)

Jika Anda ingin mengupdate atau membersihkan data bintang mentah:

```bash
# Jalankan script pembersih
uv run python clean_stars.py

# Salin hasil ke file utama
cp nama_bintang_clean.txt nama_bintang.txt  # Linux/macOS
Copy-Item nama_bintang_clean.txt nama_bintang.txt  # Windows PowerShell

# Update database
uv run python scraper.py
```

### Verifikasi Data

Untuk melihat sample data yang telah diproses:

```bash
uv run python analyze_data.py
```

## Troubleshooting

### Database Error
Jika terjadi error terkait database, hapus file `data/astro.db` dan jalankan ulang scraper:
```bash
rm data/astro.db  # Linux/macOS
Remove-Item data/astro.db  # Windows PowerShell
uv run python scraper.py
```

### Port Sudah Digunakan
Jika port 8000 sudah digunakan, gunakan port lain:
```bash
uv run uvicorn main:app --reload --port 8001
```

## Kredit & Data

Data nama bintang diambil dari IAU (International Astronomical Union) dan berbagai referensi astronomi terpercaya. Deskripsi telah disederhanakan dan diterjemahkan agar mudah dipahami oleh pengguna awam dan anak-anak Indonesia.

---
Dibuat untuk edukasi astronomi Indonesia.
