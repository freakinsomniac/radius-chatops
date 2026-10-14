# Radius Discord Bot (Radius-ChatOps)

Bot Discord ChatOps untuk mempermudah administrasi dan operasional server **FreeRADIUS** dan **daloRADIUS** secara real-time langsung melalui Discord slash commands (`/`).

Bot ini dibangun secara asynchronous menggunakan **Python**, library **disnake**, dan koneksi pool **aiomysql** ke database MariaDB/MySQL RADIUS. Dilengkapi dengan **autocomplete dinamis**, **color-coded embeds**, validasi data terstruktur, serta error handling yang aman.

---

## 📐 Arsitektur Sistem

```text
               ┌───────────────────────────────┐
               │    Administrator / Operator   │
               └──────────────┬────────────────┘
                              │ Slash Command (/)
                              ▼
               ┌───────────────────────────────┐
               │    Discord Gateway / Bot      │
               │        (disnake async)        │
               └──────────────┬────────────────┘
                              │ Asynchronous Connection Pool
                              ▼
               ┌───────────────────────────────┐
               │   MariaDB / MySQL Database    │
               │           (radius)            │
               └──────┬─────────────────┬──────┘
                      │                 │
                      ▼                 ▼
          ┌──────────────────────┐  ┌───────────────────────┐
          │  FreeRADIUS Daemon   │  │   daloRADIUS Web UI   │
          │ (Auth / Accounting)  │  │  (Management Portal)  │
          └──────────────────────┘  └───────────────────────┘
```

---

## 🚀 Fitur & Daftar Slash Command

Bot terbagi ke dalam modular Cogs yang rapi dan terorganisir:

### 1. 👤 User Management (`cogs/user_commands.py`)

| Command | Parameter | Deskripsi |
| :--- | :--- | :--- |
| `/users` | - | Menampilkan daftar seluruh username RADIUS (otomatis dipaginasi per 50 user per embed). |
| `/adduser` | `username`, `password`, `[group]` | Mendaftarkan user baru (`radcheck`) dengan kata sandi cleartext, dan opsional langsung memasukkan ke profile/group (`radusergroup`). |
| `/deluser` | `username` | Menghapus user dari database (`radcheck` dan relasi di `radusergroup`). Mendukung autocomplete username. |
| `/changepass` | `username`, `new_password` | Mengubah password (`Cleartext-Password`) untuk user tertentu. |

---

### 2. 👥 Group & Profile Management (`cogs/group_commands.py`)

| Command | Parameter | Deskripsi |
| :--- | :--- | :--- |
| `/creategroup` | `groupname`, `[rate_limit]`, `[session_timeout]`, `[simultaneous_use]` | Membuat profil/grup baru dengan atribut standar (misal Mikrotik Rate Limit, Session Timeout). |
| `/deletegroup` | `groupname` | Menghapus grup sepenuhnya dari database (`radgroupreply`, `radgroupcheck`, dan mapping di `radusergroup`). |
| `/setprofile` | `username`, `groupname` | Menetapkan atau mengganti profil/grup RADIUS untuk seorang user (`radusergroup`). |
| `/removeprofile`| `username` | Melepas profil/grup dari seorang user (menjadikan user tanpa grup). |
| `/groupinfo` | `groupname` | Melihat informasi detail profil grup (daftar reply attributes, check/NAS attributes, dan jumlah user anggota). |
| `/groupadd` | `groupname`, `attribute`, `op`, `[value]` | Menambahkan atribut reply kustom ke grup di tabel `radgroupreply`. |
| `/groupremove` | `groupname`, `[attribute]` | Menghapus atribut reply tertentu dari grup, atau menghapus seluruh reply grup jika atribut dikosongkan. |
| `/groupnasadd` | `groupname`, `nas_ip` | Menambahkan restriksi IP router NAS yang diizinkan untuk seluruh user dalam grup (`radgroupcheck`). |
| `/groupnasremove` | `groupname`, `nas_ip` | Menghapus restriksi IP router NAS dari grup (`radgroupcheck`). |

---

### 3. 🌐 NAS Device Management (`cogs/nas_commands.py`)

| Command | Parameter | Deskripsi |
| :--- | :--- | :--- |
| `/naslist` | `[limit]` | Menampilkan daftar semua perangkat router / NAS yang terdaftar di tabel `nas`. |
| `/viewnas` | `nasip` | Melihat detail konfigurasi NAS (IP/Host, shortname, secret, type, description). |
| `/addnas` | `nas_ip_host`, `nas_secret`, `nas_type`, `nas_shortname`, `[description]` | Menambahkan router/NAS baru ke tabel `nas`. Pilihan tipe: `mikrotik`, `cisco`, `chillispot`, atau `other`. |
| `/editnas` | `nasip`, `[nas_secret]`, `[nas_type]`, `[nas_shortname]`, `[description]` | Mengubah data konfigurasi router/NAS yang sudah terdaftar. |
| `/delnas` | `nasip` | Menghapus router/NAS dari tabel `nas`. |
| `/nasusers` | `nasip`, `[limit]` | Melihat daftar user yang sedang aktif terhubung pada router NAS tertentu berdasarkan data akuntansi (`radacct`). |
| `/addnasip` | `username`, `nas_ip` | Mengizinkan user tertentu untuk login ke router NAS spesifik (disimpan di `radcheck` sebagai `NAS-IP-Address`). |
| `/removenasip` | `username`, `nas_ip` | Menghapus izin router NAS spesifik dari user individual. |
| `/listnasip` | `username` | Menampilkan seluruh router NAS yang diizinkan untuk user individual. |

---

### 4. 📊 Statistics & Accounting (`cogs/stats_commands.py`)

| Command | Parameter | Deskripsi |
| :--- | :--- | :--- |
| `/userstats` | `username` | Menampilkan statistik sesi user dari `radacct` (total sesi, total download/upload dalam MB, dan waktu login terakhir). |
| `/lastlogin` | `username` | Menampilkan histori waktu login terakhir user. |
| `/activecount`| - | Menghitung total sesi yang sedang online/aktif saat ini (`radacct` di mana `acctstoptime IS NULL`). |

---

### 5. 🔍 Attribute Inspection (`cogs/attribute_commands.py`)

| Command | Parameter | Deskripsi |
| :--- | :--- | :--- |
| `/checkattributes` | `username` | Memeriksa seluruh atribut yang aktif pada seorang user, menggabungkan atribut personal (`radcheck`) dan atribut turunan grup (`radgroupcheck`), lengkap dengan resolusi nama NAS. |

---

### 6. ⚙️ Bot Administration & Utility (`cogs/admin_commands.py` & `main.py`)

| Command | Parameter | Deskripsi |
| :--- | :--- | :--- |
| `/reload` | `[cog]` | Melakukan hot-reload modul cog tanpa perlu mematikan bot (*Khusus Owner Bot / `OWNER_ID`*). |
| `/restart` | - | Merestart proses bot secara penuh (*Khusus Owner Bot / `OWNER_ID`*). |
| `/ping` | - | Menguji respon bot Discord ("Pong! 🏓"). |

---

## 🎨 User Experience & Interface

1. **Autocomplete Cerdas**:
   - `username`: Mengambil saran langsung dari database user aktif.
   - `groupname`: Mengambil saran nama profil/grup yang tersedia.
   - `nas_ip`: Menampilkan daftar IP router/NAS lengkap dengan shortname deskriptif.
   - `attribute` & `operator`: Menampilkan daftar atribut standar FreeRADIUS/Mikrotik (`Mikrotik-Rate-Limit`, `Session-Timeout`, dll) dan operator (`:=`, `==`, `+=`, dll).
2. **Color-Coded Embeds**:
   - 🟢 **Hijau (Success)**: Operasi berhasil dieksekusi.
   - 🔴 **Merah (Error)**: Terjadi kesalahan input atau database.
   - 🔵 **Biru (Info)**: Informasi query, status, atau statistik.
   - 🟠 **Oranye (Warning)**: Peringatan, data tidak ditemukan, atau status penting.

---

## 🗄️ Tabel Database yang Digunakan

Bot membaca dan memanipulasi skema tabel standar FreeRADIUS / daloRADIUS:

| Tabel | Deskripsi Penggunaan |
| :--- | :--- |
| **`radcheck`** | Menyimpan kredensial autentikasi user (`Cleartext-Password`) dan pembatasan NAS user individual. |
| **`radusergroup`** | Menyimpan mapping keanggotaan user ke profil/grup. |
| **`radgroupreply`** | Menyimpan atribut reply profil grup (misal: limit bandwidth Mikrotik, IP pool). |
| **`radgroupcheck`** | Menyimpan atribut validasi grup (misal: restriksi router NAS grup via regex). |
| **`radacct`** | Menyimpan log akuntansi sesi, durasi, total byte upload/download, dan status online. |
| **`nas`** | Menyimpan daftar server / router NAS dan secret key RADIUS-nya. |

---

## 🛠️ Persyaratan Sistem

- **Python**: 3.10 atau lebih baru (Disarankan Python 3.11+)
- **Database**: MariaDB 10.x+ atau MySQL 8.x+ dengan skema FreeRADIUS aktif
- **Discord Bot**: Token bot dari [Discord Developer Portal](https://discord.com/developers/applications)

---

## 📦 Instalasi & Menjalankan

### Cara 1: Menggunakan Virtual Environment (Lokal)

1. **Clone repositori dan masuk ke direktori proyek**:
   ```bash
   git clone <repo_url>
   cd radius-chatops
   ```

2. **Buat dan aktifkan virtual environment**:
   * **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   * **Windows**:
     ```powershell
     python -m venv venv
     venv\Scripts\activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Environment Variables**:
   Salin `.env.example` menjadi `.env`:
   ```bash
   cp .env.example .env
   ```
   Lalu sesuaikan isinya:
   ```env
   # Discord Bot Configuration
   DISCORD_TOKEN=your_bot_token_here
   GUILD_ID=123456789012345678    # Opsional: Untuk instant sync slash command di server development
   OWNER_ID=123456789012345678    # Opsional: ID Discord Owner untuk akses /reload dan /restart

   # Database Configuration (MariaDB / MySQL FreeRADIUS)
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_USER=radius_user
   DB_PASSWORD=secret_password
   DB_NAME=radius
   ```

5. **Jalankan Bot**:
   ```bash
   python main.py
   ```

---

### Cara 2: Menggunakan Docker

1. **Build Docker Image**:
   ```bash
   docker build -t radius-chatops:latest .
   ```

2. **Jalankan Container**:
   ```bash
   docker run -d \
     --name radius-bot \
     --restart unless-stopped \
     --env-file .env \
     radius-chatops:latest
   ```

3. **Melihat Log**:
   ```bash
   docker logs -f radius-bot
   ```

---

## 📁 Struktur Direktori Proyek

```text
.
├── cogs/
│   ├── __init__.py
│   ├── admin_commands.py       # Bot lifecycle & hot-reload (/reload, /restart)
│   ├── attribute_commands.py   # Pemeriksaan atribut user (/checkattributes)
│   ├── group_commands.py       # Manajemen grup & profil (/creategroup, /groupadd, dll)
│   ├── nas_commands.py         # Manajemen router & restriksi NAS (/naslist, /addnas, dll)
│   ├── stats_commands.py       # Statistik akuntansi sesi (/userstats, /activecount, dll)
│   └── user_commands.py        # Manajemen user dasar (/users, /adduser, /changepass, /deluser)
├── database/
│   ├── __init__.py
│   └── db.py                   # Async connection pool aiomysql (fetch, execute, close)
├── utils/
│   ├── __init__.py
│   ├── autocomplete.py         # Helper autocomplete dinamis untuk slash command
│   ├── embeds.py               # Template Discord Embed terstandardisasi
│   └── exceptions.py           # Custom exception handling (UserNotFound, DuplicateUser, dll)
├── .dockerignore
├── .env.example                # Template variabel lingkungan
├── .gitignore
├── Dockerfile                  # Konfigurasi container Docker berbasis python:3.11-slim
├── main.py                     # Entry point bot, event handlers, & cog loader
├── requirements.txt            # Dependensi Python (disnake, aiomysql, python-dotenv, dll)
└── test_db.py                  # Script uji koneksi database
```

---

## 🛡️ Catatan Keamanan

1. **File `.env`**: Jangan pernah mengunggah file `.env` ke Git atau repository publik.
2. **Kredensial Database**: Buat akun user database khusus dengan hak akses terbatas ke database `radius`.
3. **Admin Commands**: Perintah `/reload` dan `/restart` dilindungi oleh pemeriksaan `OWNER_ID`. Pastikan `OWNER_ID` diisi dengan ID akun Discord administrator Anda.
