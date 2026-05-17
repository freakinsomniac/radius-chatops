# Radius Discord Bot

Bot Discord untuk membantu pengelolaan user FreeRADIUS lewat slash command. Bot ini terhubung ke MariaDB dan membaca tabel-tabel standar FreeRADIUS/daloRADIUS untuk menambah, menghapus, dan memantau user.

Dilengkapi dengan **autocomplete**, **color-coded responses**, dan **user-friendly interface** untuk pengalaman yang lebih baik.

## Gambaran Umum

Alur kerja proyek ini sederhana:

```text
User Discord
    │
    ▼
Bot Discord (Python)
    │
    ▼
MariaDB / radius
    │
    ▼
FreeRADIUS dan daloRADIUS
```

## Fitur

### User Management
- `/ping` - Cek bot aktif atau tidak
- `/users` - Lihat daftar semua user (dengan pagination)
- `/adduser` - Tambah user baru (dengan autocomplete group)
- `/deluser` - Hapus user (dengan autocomplete username)
- `/changepass` - Ubah password user (dengan autocomplete username)
- `/setprofile` - Assign profile/group ke user (dengan autocomplete)

### Monitoring & Analytics
- `/online` - Lihat user yang sedang aktif
- `/userstats` - Lihat statistik sesi user (sessions, bandwidth, last login)
- `/lastlogin` - Lihat waktu login terakhir user
- `/activecount` - Hitung total sesi aktif

### NAS Management
- `/naslist` - Lihat daftar NAS devices
- `/nasstatus` - Lihat status aktif per NAS
- `/nasusers` - Lihat user yang tersambung ke NAS tertentu

### Group Management
- `/groupadd` - Tambah reply attribute ke group (dengan autocomplete)
- `/groupremove` - Hapus attribute dari group (dengan autocomplete)

## Fitur Unggulan

### 🎨 Color-Coded Responses
Semua response menggunakan Discord Embeds dengan warna yang berbeda:
- **🟢 Green** - Operasi berhasil (add, delete, update)
- **🔴 Red** - Ada error atau operasi gagal
- **🔵 Blue** - Informasi atau query results
- **🟠 Orange** - Peringatan atau data tidak ditemukan

### 🔍 Autocomplete
Parameter yang mendukung autocomplete:
- `username` - Suggestions dari daftar user yang ada
- `groupname` - Suggestions dari daftar group yang ada
- `attribute` - Suggestions dari RADIUS attributes umum
- `operator` - Suggestions dari operator RADIUS

### 📊 Better Formatting
- Emoji di setiap response untuk visual clarity
- Markdown formatting (bold, code blocks)
- Field-based layout untuk informasi terstruktur
- Pagination otomatis untuk list yang panjang

## Teknologi

| Komponen           | Teknologi     |
| ------------------ | ------------- |
| Bahasa pemrograman | Python 3.10+  |
| Library Discord    | disnake       |
| Driver database    | aiomysql      |
| Konfigurasi env    | python-dotenv |
| Database           | MariaDB       |

## Struktur Proyek

```text
.
├── main.py                 # Main bot file dengan semua commands
├── requirements.txt        # Python dependencies
├── .env.example           # Template environment variables
├── README.md              # Dokumentasi ini
├── database/
│   └── db.py             # Database connection & helper functions
├── utils/
│   ├── __init__.py
│   ├── embeds.py         # Helper untuk color-coded embeds
│   └── autocomplete.py   # Autocomplete functions
├── cogs/
│   └── users.py          # (Optional) Cog version dari commands
└── test_db.py            # Database connection test
```

## Kebutuhan

- Python 3.10 atau lebih baru
- MariaDB yang sudah berisi skema FreeRADIUS
- Discord bot token
- `GUILD_ID` jika ingin command slash didaftarkan ke server tertentu saat pengembangan

## Instalasi

### 1. Buat virtual environment

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux:
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependency

```bash
pip install -r requirements.txt
```

### 3. Siapkan file environment

Salin `.env.example` menjadi `.env`, lalu isi nilainya.

Contoh isi `.env`:

```env
DISCORD_TOKEN=isi_token_discord_anda
GUILD_ID=123456789012345678

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=radius_bot
DB_PASSWORD=rahasia
DB_NAME=radius
```

## Menjalankan Bot

```bash
python main.py
```

## Contoh Penggunaan

### User Management
```
/adduser username:andi password:123456 group:basic
/deluser username:andi
/changepass username:andi new_password:654321
/setprofile username:andi groupname:premium
```

### Monitoring
```
/users
/online
/userstats username:andi
/lastlogin username:andi
/activecount
```

### NAS Management
```
/naslist limit:20
/nasstatus
/nasstatus nasip:192.168.1.1
/nasusers nasip:192.168.1.1 limit:50
```

### Group Management
```
/groupadd groupname:basic attribute:Session-Timeout op:= value:3600
/groupremove groupname:basic attribute:Session-Timeout
/groupremove groupname:basic
```

### Tips
- Ketika mengetik parameter, autocomplete akan menampilkan suggestions
- Semua response ditampilkan dengan warna dan emoji untuk clarity
- List yang panjang akan di-paginate otomatis

## Tabel Database yang Dipakai

| Tabel           | Fungsi                                          |
| --------------- | ----------------------------------------------- |
| `radcheck`      | Menyimpan kredensial user                       |
| `radacct`       | Menyimpan data accounting dan sesi aktif        |
| `nas`           | Menyimpan data NAS/router                       |
| `radusergroup`  | Menyimpan relasi user ke group                  |
| `radgroupreply` | Menyimpan atribut reply untuk group             |
| `userinfo`      | Dipakai untuk data profil minimal di daloRADIUS |

## Catatan Keamanan

- Jangan commit file `.env` ke repository
- Gunakan user MariaDB khusus untuk bot
- Jangan membuka MariaDB ke publik tanpa kontrol akses yang ketat
- Jika command hanya untuk server tertentu, isi `GUILD_ID` supaya pendaftaran slash command lebih cepat saat development

## Troubleshooting Singkat

- **Bot tidak muncul online** - Cek `DISCORD_TOKEN` di `.env`
- **Query database gagal** - Cek `DB_HOST`, `DB_USER`, `DB_PASSWORD`, dan `DB_NAME`
- **Slash command tidak muncul** - Pastikan `GUILD_ID` diisi dan bot diundang ke server yang benar
- **Autocomplete tidak bekerja** - Pastikan `utils/autocomplete.py` dan `utils/embeds.py` ada di folder yang benar
- **Import error** - Jalankan `pip install -r requirements.txt` untuk install semua dependencies

## Changelog

### v2.0 (Current)
- ✨ Tambah autocomplete untuk semua parameter relevan
- 🎨 Implementasi color-coded embeds (success, error, info, warning)
- 📊 Better formatting dengan emoji dan markdown
- 📄 Refactor ke utils folder untuk helper functions
- 📝 Update dokumentasi

### v1.0
- Initial release dengan 14 commands dasar
