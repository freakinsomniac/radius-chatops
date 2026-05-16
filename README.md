# Radius Discord Bot

Bot Discord untuk membantu pengelolaan user FreeRADIUS lewat slash command. Bot ini terhubung ke MariaDB dan membaca tabel-tabel standar FreeRADIUS/daloRADIUS untuk menambah, menghapus, dan memantau user.

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

- `/ping` untuk mengecek bot aktif atau tidak.
- `/users` untuk melihat daftar user di tabel `radcheck`.
- `/adduser` untuk menambah user baru.
- `/deluser` untuk menghapus user.
- `/changepass` untuk mengubah password user.
- `/online` untuk melihat user yang sedang aktif.
- `/userstats` untuk ringkasan sesi user.
- `/lastlogin` untuk melihat waktu login terakhir.
- `/activecount` untuk menghitung sesi aktif.
- `/naslist` untuk melihat daftar NAS.
- `/nasstatus` untuk melihat status aktif per NAS.
- `/nasusers` untuk melihat user yang sedang tersambung ke NAS tertentu.
- `/setprofile` untuk mengatur grup user.
- `/groupadd` dan `/groupremove` untuk mengelola reply group.

## Teknologi

| Komponen           | Teknologi     |
| ------------------ | ------------- |
| Bahasa pemrograman | Python        |
| Library Discord    | disnake       |
| Driver database    | aiomysql      |
| Konfigurasi env    | python-dotenv |
| Database           | MariaDB       |

## Struktur Proyek

```text
main.py
requirements.txt
.env.example
README.md
cogs/
database/
test_db.py
```

## Kebutuhan

- Python 3.10 atau lebih baru.
- MariaDB yang sudah berisi skema FreeRADIUS.
- Discord bot token.
- `GUILD_ID` jika ingin command slash didaftarkan ke server tertentu saat pengembangan.

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

- `/ping`
- `/users`
- `/adduser username:andi password:123456 group:basic`
- `/changepass username:andi new_password:654321`
- `/online`
- `/naslist limit:20`

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

- Jangan commit file `.env` ke repository.
- Gunakan user MariaDB khusus untuk bot.
- Jangan membuka MariaDB ke publik tanpa kontrol akses yang ketat.
- Jika command hanya untuk server tertentu, isi `GUILD_ID` supaya pendaftaran slash command lebih cepat saat development.

## Troubleshooting Singkat

- Jika bot tidak muncul online, cek `DISCORD_TOKEN`.
- Jika query database gagal, cek `DB_HOST`, `DB_USER`, `DB_PASSWORD`, dan `DB_NAME`.
- Jika slash command tidak muncul, pastikan `GUILD_ID` diisi dan bot diundang ke server yang benar.
