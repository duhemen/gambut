<!-- ========================================================= -->
<!--                    BANNER HEADER                          -->
<!-- ========================================================= -->
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d6efd,50:10b981,100:2ecc71&height=200&section=header&text=GAMBUTFR&fontSize=80&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Peat%20Fire%20Risk%20Monitoring%20Platform&descAlignY=58&descSize=18" width="100%" />

<!-- ========================================================= -->
<!--                      BADGES                               -->
<!-- ========================================================= -->

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://pypi.org/project/PyQt6/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.10-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![NASA](https://img.shields.io/badge/NASA-FIRMS-0B3D91?style=for-the-badge&logo=nasa&logoColor=white)](https://firms.modaps.eosdis.nasa.gov/)
[![Cloudflare](https://img.shields.io/badge/Cloudflare-Tunnel-F38020?style=for-the-badge&logo=cloudflare&logoColor=white)](https://www.cloudflare.com/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](#-lisensi)

[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=for-the-badge)]()
[![Architecture](https://img.shields.io/badge/Architecture-Hybrid%20Decentralized-0d6efd?style=flat-square)](#-arsitektur-sistem)
[![REST API](https://img.shields.io/badge/API-REST%20%2F%20JSON-orange?style=flat-square)](http://gambutfr.osvpn.id/docs)
[![Auth](https://img.shields.io/badge/Auth-JWT%20Bearer-9b59b6?style=flat-square)](#-api-endpoints)
[![PWA](https://img.shields.io/badge/PWA-Mobile%20Ready-5A0FC8?style=flat-square)](https://gambutfr.osvpn.id/dashboard)
[![Made in](https://img.shields.io/badge/Made%20in-Indonesia%20%F0%9F%87%AE%F0%9F%87%A9-red?style=flat-square)](#-kredit)

</div>

---

<!-- ========================================================= -->
<!--                  TABLE OF CONTENTS                        -->
<!-- ========================================================= -->

## 📖 Daftar Isi

<details open>
<summary>Klik untuk buka / tutup</summary>

- [🌟 Tentang Proyek](#-tentang-proyek)
- [🎯 Fitur Utama](#-fitur-utama)
- [✨ Showcase](#-showcase)
- [🏗️ Arsitektur Sistem](#️-arsitektur-sistem)
- [📂 Struktur Folder](#-struktur-folder)
- [🛠️ Persyaratan Sistem](#️-persyaratan-sistem)
- [🚀 Panduan Instalasi](#-panduan-instalasi)
- [▶️ Cara Menjalankan](#️-cara-menjalankan)
- [📚 Panduan Penggunaan](#-panduan-penggunaan)
- [🔌 API Endpoints](#-api-endpoints)
- [🧪 Testing & Debugging](#-testing--debugging)
- [🚢 Deployment](#-deployment)
- [🗺️ Roadmap](#️-roadmap)
- [🤝 Kontribusi](#-kontribusi)
- [📜 Lisensi](#-lisensi)
- [🙏 Kredit](#-kredit)

</details>

---

<!-- ========================================================= -->
<!--                  TENTANG PROYEK                           -->
<!-- ========================================================= -->

## 🌟 Tentang Proyek

**GambutFR** adalah platform **monitoring & prediksi risiko kebakaran lahan gambut tropis** yang menggabungkan **data satelit real-time**, **machine learning**, dan **arsitektur hybrid decentralized** — dirancang untuk **petugas lapangan** yang butuh alat canggih tanpa ribet.

Sistem ini dibangun untuk **Indonesia**, dengan dukungan **multi-region**, **alert Telegram otomatis**, dan **deployment hybrid** yang bisa diakses dari **mana saja, kapan saja** — bahkan dari pelosok hutan gambut.

### 🌱 Yang Membuat GambutFR Berbeda

- **Hybrid Decentralized** — server lokal tetap jalan offline, tapi bisa diakses dari seluruh dunia via Cloudflare Tunnel.
- **Multi-Region Native** — petugas di Kalimantan, Sumatera, dan Papua input data mereka sendiri. Dashboard menampilkan **peta risiko per wilayah**.
- **Real-Time Satellite** — integrasi langsung dengan **NASA FIRMS** untuk deteksi hotspot. Auto-fetch tiap 6 jam.
- **AI Ensemble** — kombinasi **ARIMA + LSTM + GRU** untuk prediksi yang lebih akurat, dengan **confidence interval 95%**.
- **Auto Alert** — Telegram bot kirim notifikasi **spesifik region** saat status BAHAYA/SIAGA terdeteksi.
- **PWA Mobile** — install di HP seperti app native. Buka dari mana saja.

> 💡 Terinspirasi dari riset akademik tentang prediksi risiko kebakaran gambut, GambutFR hadir sebagai **implementasi praktis** yang siap dipakai petugas lapangan di seluruh Indonesia.

---

<!-- ========================================================= -->
<!--                  FITUR UTAMA                              -->
<!-- ========================================================= -->

## 🎯 Fitur Utama

<table>
<tr>
<td width="50%">

### 🛰️ **Real-Time Satellite**
- Integrasi **NASA FIRMS** (VIIRS + MODIS)
- Auto-fetch **3 region** tiap 6 jam
- Konversi hotspot → parameter gambut
- Filter confidence level
- Snapshot per-region tersimpan

### 🤖 **AI & Machine Learning**
- **Ensemble forecast** (ARIMA + LSTM + GRU)
- **Confidence Interval 95%** via bootstrap
- **Time-Series K-Fold** cross-validation
- **Anomaly detection** (Z-score + IQR + Isolation Forest)
- **PFVI** dengan Nelder-Mead optimization

### 📱 **Multi-Platform Access**
- **Desktop App** (PyQt6) — admin & analis
- **Web Dashboard** (PWA) — akses dari HP
- **REST API** — integrasi pihak ketiga
- **Mobile-Ready** — install seperti app native

</td>
<td width="50%">

### 📢 **Alert & Notification**
- **Telegram Bot** otomatis
- **Region-specific** — sebut nama wilayah
- **Cooldown** anti-spam (5 menit)
- **Broadcast** ke semua region sekaligus
- **HTML formatting** rapi

### 🔐 **Security & Multi-User**
- **JWT Authentication** stateless
- **Role-Based Access** (admin / petugas)
- **Bcrypt** password hashing
- **Session management** di client
- **CORS** configurable

### ☁️ **Hybrid Deployment**
- Server lokal (offline-first)
- **Cloudflare Tunnel** gratis HTTPS
- **PWA manifest** install di HP
- **Auto-redirect** root → dashboard
- **Multi-device** akses bersamaan

</td>
</tr>
</table>

---

<!-- ========================================================= -->
<!--                  SHOWCASE                                 -->
<!-- ========================================================= -->

## ✨ Showcase

### 🌐 **Live Demo — Buka dari Mana Saja**

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   🔥  https://gambutfr.osvpn.id/dashboard                   │
│                                                             │
│   • Dari laptop di kantor posko                             │
│   • Dari HP di tengah hutan Kalimantan                      │
│   • Dari tablet di kapal penelitian                         │
│   • Dari warnet di pelosok Papua                            │
│                                                             │
│   Semuanya akses DASHBOARD yang SAMA.                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 🗺️ **Multi-Region Monitoring**

Satu dashboard, semua wilayah terpantau. Setiap region punya **skor PFVI sendiri**:

```
┌──────────────────────────────────────────────────────────────┐
│  🗺️  RINGKASAN PER-REGION                                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  🌴 KALIMANTAN         🦜 PAPUA           🌳 SUMATERA        │
│  ━━━━━━━━━━━━━━         ━━━━━━━━━━         ━━━━━━━━━━━━      │
│  Hotspot: 9,375         Hotspot: 3,961      Hotspot: 2,553   │
│  PFVI   : 76.0          PFVI   : 59.6       PFVI   : 54.0    │
│  Status : 🔴 BAHAYA     Status : 🟡 SIAGA    Status : 🟡 SIAGA │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

### 📢 **Auto Telegram Alert — Spesifik Region**

Setiap kali satelit mendeteksi hotspot di level BAHAYA, bot Telegram langsung kirim **pesan terformat** ke grup petugas:

```
┌──────────────────────────────────────────────────────────┐
│  🔴 PEATFR ALERT — KALIMANTAN                            │
│  Status: BAHAYA                                          │
│                                                          │
│  Skor Kerawanan: 81.4/100                                │
│  Region: KALIMANTAN                                      │
│                                                          │
│  Data Pengukuran:                                        │
│    • Muka Air (WT): -24.9 cm                             │
│    • Kelembapan Tanah: 38.1 %                            │
│    • Curah Hujan: 10.1 mm                                │
│    • Suhu: 36.0 °C                                       │
│    • Tanggal: 2026-09-19                                 │
│                                                          │
│  🕐 2026-09-19 20:30:21 WIB                              │
│                                                          │
│  🔗 Buka Dashboard                                       │
└──────────────────────────────────────────────────────────┘
```

---

### ⏰ **Auto-Fetch Scheduler**

Server Anda **bekerja sendiri** — fetch satelit tiap 6 jam, alert otomatis, dashboard ter-update:

```
┌────────────────────────────────────────────────────────────┐
│  ⏰ SCHEDULER OTOMATIS                                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Status       : 🟢 RUNNING                                 │
│  Interval     : 6 jam                                      │
│  Total Runs   : 12 kali (sejak server nyala)               │
│  Errors       : 0                                          │
│                                                            │
│  Terakhir Jalan : 2026-09-19 20:55:45                      │
│  Berikutnya     : 2026-09-20 02:55:45                      │
│                                                            │
│  Region Aktif  : kalimantan, sumatera, papua               │
│                                                            │
│  Hasil Terakhir:                                           │
│    • kalimantan: 2,892 hotspot                             │
│    • sumatera:     322 hotspot                             │
│    • papua:        751 hotspot                             │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

### 🔍 **Anomaly Detection**

Sistem otomatis **menandai outlier** menggunakan **3 metode voting** — akurasi lebih tinggi dari metode tunggal:

```
┌──────────────────────────────────────────────────────────────┐
│  🔍 DETEKSI ANOMALI                                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Total Data   : 17 baris                                     │
│  Anomali      : 1 baris                                      │
│  Data Normal  : 16 baris                                     │
│  Rasio        : 5.9 %                                        │
│                                                              │
│  ┌────────────┬───────────┬─────┬─────┬─────┬────────────┐  │
│  │ Tanggal    │ WT        │ SM  │ RF  │ T°  │ Alasan     │  │
│  ├────────────┼───────────┼─────┼─────┼─────┼────────────┤  │
│  │ 2026-09-10 │ -5.00     │ 55  │12.5 │28.5 │ Z+IQR+IF   │  │
│  └────────────┴───────────┴─────┴─────┴─────┴────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 **AI Forecasting (Ensemble)**

Prediksi muka air tanah dengan **3 model AI digabung**, plus **confidence interval 95%**:

```
┌─────────────────────────────────────────────────────────────┐
│  🧠 FORECAST MUKA AIR TANAH (7 HARI)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Model          : ENSEMBLE (ARIMA + LSTM + GRU)             │
│  Weights        : ARIMA 0.28, LSTM 0.35, GRU 0.37           │
│                                                             │
│  Hari  Prediksi   CI Bawah   CI Atas                        │
│  ────  ─────────  ─────────  ───────                        │
│   1    -10.5 cm   -11.2 cm   -9.8 cm                        │
│   2    -10.8 cm   -11.9 cm   -9.7 cm                        │
│   3    -11.2 cm   -12.4 cm   -10.0 cm                       │
│   4    -11.5 cm   -13.0 cm   -10.0 cm                       │
│   5    -11.9 cm   -13.6 cm   -10.2 cm                       │
│   6    -12.2 cm   -14.1 cm   -10.3 cm                       │
│   7    -12.6 cm   -14.8 cm   -10.4 cm                       │
│                                                             │
│  Akurasi (train/test split 80/20):                          │
│    MSE : 0.8234   RMSE : 0.9074   MAE : 0.7231              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 📱 **PWA — Install di HP**

Buka `https://gambutfr.osvpn.id/dashboard` di HP → **"Add to Home Screen"** → selesai. Icon 🔥 muncul di home screen, aplikasi jalan fullscreen seperti app native:

```
┌─────────────────────────────────┐
│                                 │
│   📱 Home Screen HP Anda        │
│                                 │
│   ┌───┐  ┌───┐  ┌───┐  ┌───┐   │
│   │📞 │  │📷 │  │💬 │  │🔥 │   │
│   └───┘  └───┘  └───┘  └───┘   │
│  Telepon  Kamera  Chat  PeatFR  │
│                                 │
│   ← Klik icon 🔥               │
│      → Buka fullscreen          │
│      → Seperti app native       │
│                                 │
└─────────────────────────────────┘
```

---

### 🔐 **Multi-User dengan JWT**

Setiap petugas login dengan akun sendiri. Admin kelola user, petugas akses terbatas:

```
┌──────────────────────────────────────────────────────┐
│  👥 MANAJEMEN USER                                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Username     Role      Full Name       Status      │
│  ─────────    ─────     ──────────      ─────────   │
│  admin        admin     Administrator   🟢 Active   │
│  budi_riau    petugas   Budi Santoso    🟢 Active   │
│  siti_kalteng petugas   Siti Nurhaliza  🟢 Active   │
│  ahmad_papua  petugas   Ahmad Yusuf     🟢 Active   │
│                                                      │
│  Setiap user punya token JWT sendiri.                │
│  Setiap aksi ter-audit di log server.                │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

### 🚀 **Deploy Hybrid — Local + Cloud**

Server lokal tetap aman di kantor, tapi bisa diakses dari internet:

```
                     🌐 INTERNET
                          │
                          ▼
            ┌─────────────────────────┐
            │  ☁️ CLOUDFLARE EDGE     │
            │  • HTTPS gratis         │
            │  • DDoS protection      │
            │  • Global CDN           │
            └────────────┬────────────┘
                         │ Tunnel (encrypted)
                         ▼
            ┌─────────────────────────┐
            │  💻 LAPTOP ANDA         │
            │  D:\gambut\             │
            │  • FastAPI :8000        │
            │  • CSV database         │
            │  • NASA scheduler       │
            │  • Telegram bot         │
            └─────────────────────────┘
                         ▲
                         │ LAN
                         │
            ┌────────────┴────────────┐
            │  👥 MULTI-CLIENT        │
            │  • Desktop PyQt6        │
            │  • HP Petugas (PWA)     │
            │  • Browser admin        │
            └─────────────────────────┘
```

---

### 🎨 **Aurora Dark Theme**

UI dengan efek **Aurora gradient**, **glassmorphism cards**, dan **neon accents** — profesional tapi tetap elegan:

```
┌─────────────────────────────────────────────────────┐
│  🔥  GAMBUTFR                🔴 BAHAYA              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐      │
│  │ 17     │ │-22.5cm │ │ 36.5°C │ │  91    │      │
│  │ TOTAL  │ │   WT   │ │  SUHU  │ │  PFVI  │      │
│  └────────┘ └────────┘ └────────┘ └────────┘      │
│                                                     │
│  • Background: Deep navy + aurora glow              │
│  • Card: Semi-transparent glassmorphism             │
│  • Accent: Emerald / amber / crimson                │
│  • Font: Inter / Segoe UI                           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

<!-- ========================================================= -->
<!--                  ARSITEKTUR SISTEM                        -->
<!-- ========================================================= -->

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                     🌐 INTERNET GLOBAL                      │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
     ┌────────────┐   ┌────────────┐  ┌────────────┐
     │  📱 HP     │   │  💻 Laptop │  │  🖥️ Server │
     │  Petugas   │   │  Rekan     │  │  Posko     │
     │  (PWA)     │   │  (Browser) │  │  (Web)     │
     └─────┬──────┘   └─────┬──────┘  └─────┬──────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                            ▼ HTTPS
              ┌──────────────────────────────┐
              │   ☁️ CLOUDFLARE EDGE         │
              │   • SSL/TLS                  │
              │   • DDoS Protection          │
              │   • Web Application Firewall │
              └──────────────┬───────────────┘
                             │
                             │ Tunnel (encrypted)
                             │
                             ▼
    ┌──────────────────────────────────────────────────┐
    │         💻 LOKAL SERVER (D:\gambut)              │
    ├──────────────────────────────────────────────────┤
    │                                                  │
    │  ┌────────────────────────────────────────────┐  │
    │  │  FastAPI Backend (:8000)                   │  │
    │  │  ┌──────────────┐  ┌──────────────────┐   │  │
    │  │  │ Auth Layer   │  │ Scheduler Layer  │   │  │
    │  │  │ • JWT verify │  │ • Auto-fetch 6h  │   │  │
    │  │  │ • RBAC       │  │ • NASA FIRMS     │   │  │
    │  │  └──────────────┘  └──────────────────┘   │  │
    │  │  ┌──────────────┐  ┌──────────────────┐   │  │
    │  │  │ AI Engine    │  │ Alert Engine     │   │  │
    │  │  │ • Ensemble   │  │ • Telegram Bot   │   │  │
    │  │  │ • Anomaly    │  │ • Region-aware   │   │  │
    │  │  │ • PFVI       │  │ • Cooldown       │   │  │
    │  │  └──────────────┘  └──────────────────┘   │  │
    │  └────────────────────────────────────────────┘  │
    │                                                  │
    │  ┌────────────────────────────────────────────┐  │
    │  │  Storage Layer                             │  │
    │  │  • database_gambut.csv  (data observasi)   │  │
    │  │  • users.csv            (auth bcrypt)      │  │
    │  │  • regional_latest.json (snapshot region)  │  │
    │  │  • pfvi_params.json     (cached weights)   │  │
    │  │  • alert_config.json    (telegram config)  │  │
    │  └────────────────────────────────────────────┘  │
    │                                                  │
    │  ┌────────────────────────────────────────────┐  │
    │  │  Data Sources                              │  │
    │  │  • 🛰️ NASA FIRMS (satellite hotspot)       │  │
    │  │  • ✍️ Manual input (petugas lapangan)      │  │
    │  │  • 📁 Upload CSV/Excel                     │  │
    │  └────────────────────────────────────────────┘  │
    │                                                  │
    └──────────────────────────────────────────────────┘
                             ▲
                             │
                             │ LAN (opsional)
                             │
              ┌──────────────┴───────────────┐
              │                              │
              ▼                              ▼
      ┌──────────────┐               ┌──────────────┐
      │ 💻 Desktop 1 │               │ 💻 Desktop 2 │
      │ PyQt6 Client │               │ PyQt6 Client │
      │ (admin)      │               │ (petugas)    │
      └──────────────┘               └──────────────┘
```

### 🎯 Prinsip Desain

| Prinsip | Implementasi |
|---|---|
| **Local-First** | Server jalan di komputer lokal, data tetap aman |
| **Cloud-Access** | Via Cloudflare Tunnel, bisa diakses dari mana saja |
| **Offline-Ready** | Tidak butuh internet untuk operasi dasar |
| **Multi-Region** | Setiap wilayah punya data & skor terpisah |
| **Multi-User** | JWT + RBAC, setiap user punya akun sendiri |
| **Autonomous** | Scheduler otomatis fetch + alert |
| **Progressive** | PWA installable di HP tanpa Play Store |

---

<!-- ========================================================= -->
<!--                  STRUKTUR FOLDER                          -->
<!-- ========================================================= -->

## 📂 Struktur Folder

```
gambut/
│
├── 📄 run_hybrid_server.py         # ⭐ Entry point: server + tunnel
├── 📄 README.md                    # Dokumentasi ini
├── 📄 LICENSE                      # Lisensi MIT
├── 📄 .gitignore                   # Git ignore rules
├── 📄 .env.example                 # Template konfigurasi
├── 📄 environment.yml              # Anaconda environment
├── 📄 requirements-server.txt      # Deps server
├── 📄 requirements-client.txt      # Deps client
├── 📄 requirements-dev.txt         # Deps testing
├── 📄 pytest.ini                   # Config pytest
├── 📄 struktur.md                  # Dokumentasi struktur
│
├── 📁 client/                      # ⭐ DESKTOP APP (PyQt6)
│   ├── __init__.py
│   ├── main.py                     # Entry point desktop
│   ├── config.py                   # Config URL & timeout
│   │
│   ├── 📁 api/                     # HTTP Client
│   │   ├── __init__.py
│   │   └── client.py               # Singleton PeatFireClient
│   │
│   ├── 📁 core/                    # Business logic client
│   │   ├── __init__.py
│   │   ├── forecasting.py
│   │   ├── imputation.py
│   │   └── index_calc.py
│   │
│   ├── 📁 gui/                     # GUI Layer
│   │   ├── __init__.py
│   │   ├── theme.py                # 🎨 Tema Aurora Dark
│   │   ├── widgets.py              # Reusable components
│   │   ├── main_window.py          # Window utama + sidebar
│   │   ├── login_dialog.py         # Dialog login
│   │   └── 📁 tabs/
│   │       ├── __init__.py
│   │       ├── tab_dashboard.py    # 📊 Dashboard
│   │       ├── tab_manual.py       # ✍️ Input manual (region-aware)
│   │       ├── tab_upload.py       # 📁 Upload file (region-aware)
│   │       ├── tab_anomaly.py      # 🔍 Deteksi anomali
│   │       ├── tab_scheduler.py    # ⏰ Kontrol scheduler
│   │       ├── tab_setting.py      # ⚙️ Pengaturan (admin-only)
│   │       └── tab_placeholder.py  # Placeholder
│   │
│   ├── 📁 utils/                   # Helper
│   │   ├── __init__.py
│   │   └── data_processor.py
│   │
│   └── 📁 data/                    # Data lokal client
│       └── template_input.xlsx     # Template upload
│
├── 📁 server/                      # ⭐ BACKEND (FastAPI)
│   ├── __init__.py
│   ├── main.py                     # Entry point FastAPI
│   ├── models.py                   # Pydantic schemas
│   ├── database.py                 # Layer akses CSV
│   │
│   ├── 📁 auth/                    # 🔐 Autentikasi
│   │   ├── __init__.py
│   │   ├── password.py             # Hash & verify bcrypt
│   │   ├── jwt_handler.py          # Generate & verify JWT
│   │   └── dependencies.py         # get_current_user, require_role
│   │
│   ├── 📁 api/                     # REST endpoints
│   │   ├── __init__.py
│   │   ├── routes.py               # 30+ endpoints
│   │   └── web.py                  # Serve dashboard HTML
│   │
│   ├── 📁 core/                    # ⭐ AI ENGINE
│   │   ├── __init__.py
│   │   ├── imputation.py           # KNN / Spline / Linear / Loess
│   │   ├── forecasting.py          # ARIMA + Box-Cox
│   │   ├── deep_learning.py        # LSTM / GRU (PyTorch)
│   │   ├── ensemble.py             # Ensemble + CI + CV
│   │   ├── index_calc.py           # PFVI Nelder-Mead
│   │   ├── anomaly.py              # Z-score + IQR + IF
│   │   ├── satellite.py            # NASA FIRMS integration
│   │   ├── scheduler.py            # Auto-fetch scheduler
│   │   ├── alert.py                # Telegram notifications
│   │   ├── pfvi_cache.py           # Cached PFVI params
│   │   └── autopeatfr.py           # All-in-one pipeline
│   │
│   ├── 📁 templates/               # Web dashboard
│   │   ├── dashboard.html          # Main dashboard
│   │   ├── manifest.json           # PWA manifest
│   │   └── sw.js                   # Service worker
│   │
│   ├── 📁 static/                  # Static assets
│   │   └── 📁 icons/
│   │       ├── icon-192.png
│   │       └── icon-512.png
│   │
│   └── 📁 data/                    # 💾 Storage (JANGAN DI-COMMIT!)
│       ├── database_gambut.csv     # Data observasi
│       ├── sample_satellite.csv    # Sample (boleh di-commit)
│       ├── users.csv               # 🔐 User (auto-generated)
│       ├── config.json             # (auto-generated)
│       ├── alert_config.json       # 🔐 Telegram config
│       ├── pfvi_params.json        # Cached params
│       └── regional_latest.json    # Snapshot region
│
├── 📁 docs/                        # 📚 Documentation
│   ├── 📁 cloudflared/
│   │   └── config.yml.example      # Template tunnel config
│   └── 📁 screenshots/             # Screenshot assets
│
├── 📁 tests/                       # 🧪 Unit tests
│   ├── __init__.py
│   ├── test_pfvi.py
│   ├── test_imputation.py
│   └── test_anomaly.py
│
└── 📁 scripts/                     # 🛠️ Utility scripts
    └── migrate_add_region.py       # Database migration
```

---

<!-- ========================================================= -->
<!--                  PERSYARATAN SISTEM                       -->
<!-- ========================================================= -->

## 🛠️ Persyaratan Sistem

| Komponen | Minimum | Rekomendasi |
|----------|---------|-------------|
| **OS** | Windows 10 / Ubuntu 20.04 / macOS 11 | Windows 11 / Ubuntu 22.04 |
| **Python** | 3.11 | 3.11.x (tested) |
| **RAM** | 4 GB | 8 GB+ (untuk LSTM/GRU) |
| **Storage** | 2 GB | 5 GB (dengan PyTorch + TensorFlow) |
| **Anaconda** | Miniconda | Anaconda Full Distribution |
| **Jaringan** | LAN lokal | Internet (untuk satelit & tunnel) |
| **Cloudflare Account** | Gratis | Gratis (Free plan) |
| **NASA FIRMS API Key** | Gratis | Gratis |
| **Telegram Bot** | Gratis | Gratis |

---

<!-- ========================================================= -->
<!--                  PANDUAN INSTALASI                        -->
<!-- ========================================================= -->

## 🚀 Panduan Instalasi

### Tahap 1 — Clone Repository

```bash
git clone https://github.com/duhemen/gambut.git
cd gambut
```

### Tahap 2 — Setup Anaconda Environment

Buka **Anaconda Prompt**:

```bash
# Buat environment dari file
conda env create -f environment.yml

# Aktifkan
conda activate peatfr_env

# Verifikasi
python --version
# Output: Python 3.11.x
```

### Tahap 3 — Install Deep Learning Backend (Opsional)

Untuk fitur LSTM/GRU asli:

```bash
# Opsi A: PyTorch (ringan ~200 MB) — REKOMENDASI
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Opsi B: TensorFlow (berat ~600 MB)
pip install tensorflow-cpu
```

Cek backend terdeteksi:

```bash
python -c "from server.core.deep_learning import get_backend_info; import json; print(json.dumps(get_backend_info(), indent=2))"
```

### Tahap 4 — Setup Konfigurasi `.env`

```bash
# Copy template
cp .env.example .env

# Edit dengan text editor
notepad .env  # Windows
nano .env     # Linux/Mac
```

**Isi field wajib:**

```env
# Generate secret key (jalankan: python -c "import secrets; print(secrets.token_urlsafe(48))")
PEATFR_SECRET_KEY=<paste-hasil-generate>

# NASA FIRMS (daftar gratis: https://firms.modaps.eosdis.nasa.gov/api/map_key/)
NASA_FIRMS_API_KEY=<paste-api-key-anda>

# Telegram (lihat panduan di bawah)
TELEGRAM_BOT_TOKEN=<paste-bot-token>
TELEGRAM_CHAT_IDS=<paste-chat-id>
```

### Tahap 5 — Dapatkan API Keys

<details>
<summary><b>🔑 Cara Dapat NASA FIRMS API Key (Gratis, 5 menit)</b></summary>

1. Buka https://firms.modaps.eosdis.nasa.gov/api/map_key/
2. Isi email Anda
3. Cek inbox → dapat **MAP_KEY** (32 karakter hex)
4. Paste ke `.env`

</details>

<details>
<summary><b>🔑 Cara Dapat Telegram Bot Token (Gratis, 3 menit)</b></summary>

1. Buka Telegram → chat **@BotFather**
2. Ketik `/newbot`
3. Beri nama bot (mis. `PeatFR Alert Bot`)
4. Beri username (mis. `peatfr_alert_bot`)
5. Copy **BOT_TOKEN**
6. Chat **@userinfobot** → klik START → dapat **CHAT_ID**
7. Paste keduanya ke `.env`

</details>

---

<!-- ========================================================= -->
<!--                  CARA MENJALANKAN                         -->
<!-- ========================================================= -->

## ▶️ Cara Menjalankan

### 🚀 Opsi 1: Hybrid Mode (Server + Cloudflare Tunnel)

Cara paling powerful — server lokal + akses global:

```bash
# Terminal 1 — jalankan server + tunnel
python run_hybrid_server.py
```

**Log sukses:**
```
✅ [ENV] Loaded from: D:\gambut\.env
✅ [JWT] PEATFR_SECRET_KEY loaded (64 chars).
✅ [DL] Backend: PyTorch 2.10.0
✅ [SERVER] Database, satellite, users siap.
✅ [SCHEDULER] Aktif — interval 6 jam
☁️ [TUNNEL] Cloudflare Tunnel started
```

### 🖥️ Opsi 2: Server Only (Local)

```bash
# Terminal 1 — server
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

### 💻 Jalankan Desktop Client

```bash
# Terminal 2 — client
python -m client.main
```

**Login default:**
- Username: `admin`
- Password: `admin123`

> ⚠️ **Ganti password default** setelah login pertama!

### 🌐 Akses Web Dashboard

- **Lokal**: http://localhost:8000/dashboard
- **Cloudflare**: https://gambutfr.osvpn.id/dashboard

### 📱 Install PWA di HP

1. Buka `https://gambutfr.osvpn.id/dashboard` di Chrome/Safari HP
2. Menu → **"Add to Home Screen"**
3. Icon 🔥 muncul → buka seperti app native

---

<!-- ========================================================= -->
<!--                  PANDUAN PENGGUNAAN                       -->
<!-- ========================================================= -->

## 📚 Panduan Penggunaan

### 1. 🔐 Login Screen

Dialog login dengan tema **Aurora Dark**, gradient header, dan feedback visual.

- ✅ JWT authentication
- ✅ Password ter-hash bcrypt
- ✅ Session auto-attach ke setiap request
- ✅ Role-based UI (tab Setting hanya untuk admin)

### 2. 📊 Dashboard

Pusat komando dengan:
- **KPI Cards**: Total observasi, WT terkini, Suhu, PFVI
- **Tabel Data Petugas**: Per-region feed terbaru
- **Kartu Regional**: Ringkasan per region (Kalimantan, Sumatera, Papua)
- **Chart Tren WT** (line chart interaktif)
- **Diagram Pie** distribusi status
- **Tombol Sync Satelit** & **Broadcast Alert**

### 3. ✍️ Input Manual (Region-Aware)

Form input dengan **dropdown region**:
- Pilih region: `kalimantan` / `sumatera` / `papua` / dll
- Isi 4 parameter: WT, SM, RF, Temp
- Preview PFVI real-time
- Klik Simpan → auto-alert kalau BAHAYA/SIAGA

### 4. 📁 Upload Data (Region-Aware)

Bulk import dengan **selector region**:
- Pilih region tujuan
- Drag & drop file CSV/Excel
- Auto-validasi kolom
- Preview data sebelum simpan

### 5. 🔍 Anomali Detection

Deteksi outlier dengan **ensemble voting**:
- Total data & rasio anomali
- Tabel detail anomali (tanggal, WT, votes, alasan)
- Klik **"Deteksi Sekarang"** untuk refresh

### 6. ⏰ Scheduler

Kontrol auto-fetch satelit:
- **Status**: RUNNING / STOPPED
- **Interval**: 1-72 jam (configurable)
- **Total runs** & errors
- Tombol: Start / Stop / **Trigger Sekarang**

### 7. ⚙️ Pengaturan (Admin Only)

- URL Server configuration
- API Satelit credentials
- Tema aplikasi (Dark / Light)

---

<!-- ========================================================= -->
<!--                  API ENDPOINTS                            -->
<!-- ========================================================= -->

## 🔌 API Endpoints

**Swagger UI**: http://localhost:8000/docs

### 🔐 Authentication

| Method | Endpoint | Fungsi | Auth |
|--------|----------|--------|------|
| `POST` | `/api/v1/auth/register` | Daftar user baru | Admin |
| `POST` | `/api/v1/auth/login` | Login → JWT token | Public |
| `GET` | `/api/v1/auth/me` | Info user login | Bearer |
| `GET` | `/api/v1/auth/users` | Daftar user | Admin |

### 📊 Data & Analytics

| Method | Endpoint | Fungsi | Auth |
|--------|----------|--------|------|
| `GET` | `/api/v1/data` | Data historis | Bearer |
| `POST` | `/api/v1/data` | Input manual | Bearer |
| `POST` | `/api/v1/data/upload` | Upload CSV/Excel | Bearer |
| `GET` | `/api/v1/data/public` | Public data feed | Public |

### 🛰️ Satellite

| Method | Endpoint | Fungsi | Auth |
|--------|----------|--------|------|
| `POST` | `/api/v1/satellite/fetch` | Fetch NASA FIRMS | Admin |
| `GET` | `/api/v1/satellite/regions` | List region | Bearer |
| `GET` | `/api/v1/satellite/regional-summary` | Ringkasan per region | Public |

### 🧠 AI & Forecasting

| Method | Endpoint | Fungsi | Auth |
|--------|----------|--------|------|
| `POST` | `/api/v1/forecast` | Forecast WT | Bearer |
| `POST` | `/api/v1/forecast/ensemble` | Ensemble + CI | Bearer |
| `POST` | `/api/v1/forecast/cross-validate` | K-Fold CV | Bearer |
| `POST` | `/api/v1/index` | Hitung PFVI | Bearer |
| `POST` | `/api/v1/anomaly/detect` | Deteksi anomali | Bearer |
| `POST` | `/api/v1/autopeatfr` | All-in-one pipeline | Bearer |

### 📢 Alert

| Method | Endpoint | Fungsi | Auth |
|--------|----------|--------|------|
| `GET` | `/api/v1/alert/status` | Status alert | Bearer |
| `POST` | `/api/v1/alert/config` | Update config | Admin |
| `POST` | `/api/v1/alert/test` | Test kirim | Admin |
| `POST` | `/api/v1/alert/broadcast-public` | Broadcast semua region | Public |

### ⏰ Scheduler

| Method | Endpoint | Fungsi | Auth |
|--------|----------|--------|------|
| `GET` | `/api/v1/scheduler/status` | Status scheduler | Bearer |
| `POST` | `/api/v1/scheduler/start` | Start scheduler | Admin |
| `POST` | `/api/v1/scheduler/stop` | Stop scheduler | Admin |
| `POST` | `/api/v1/scheduler/trigger` | Trigger manual | Admin |

---

<!-- ========================================================= -->
<!--                  TESTING & DEBUGGING                      -->
<!-- ========================================================= -->

## 🧪 Testing & Debugging

### Run Unit Tests

```bash
# Semua test
pytest

# Dengan coverage
pytest --cov=server --cov=client --cov-report=term-missing

# Test spesifik
pytest tests/test_pfvi.py -v
```

### Test API Manual

```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Cek data (dengan token)
curl http://localhost:8000/api/v1/data \
  -H "Authorization: Bearer <TOKEN>"
```

### Reset Database

```bash
# Windows
Remove-Item server\data\users.csv

# Linux/Mac
rm server/data/users.csv
# Restart server → admin auto-generated
```

---

<!-- ========================================================= -->
<!--                  DEPLOYMENT                               -->
<!-- ========================================================= -->

## 🚢 Deployment

### ☁️ Cloudflare Tunnel Setup

<details>
<summary><b>Klik untuk expand — Setup Cloudflare Tunnel (Free)</b></summary>

#### 1. Prasyarat
- Domain (mis. `gambutfr.osvpn.id`)
- Akun Cloudflare (gratis)

#### 2. Install Cloudflared

```bash
# Windows
winget install Cloudflare.cloudflared

# Linux
sudo apt install cloudflared

# macOS
brew install cloudflared
```

#### 3. Login & Buat Tunnel

```bash
cloudflared tunnel login
cloudflared tunnel create gambut-server
```

Catat **UUID** yang muncul.

#### 4. Configure Public Hostname

Buka **Cloudflare Zero Trust Dashboard**:
- `https://one.dash.cloudflare.com/`
- Networks → Tunnels → pilih tunnel Anda
- Tab **Public Hostname** → **Add a public hostname**
- Isi:
  - Subdomain: `gambutfr`
  - Domain: `osvpn.id`
  - Service Type: `HTTP`
  - Service URL: `localhost:8000`
- **Save**

#### 5. Jalankan

```bash
python run_hybrid_server.py
```

#### 6. Akses

```
https://gambutfr.osvpn.id/dashboard
```

</details>

### 🐳 Docker (Rencana)

Roadmap: Dockerfile + docker-compose untuk deployment containerized.

---

<!-- ========================================================= -->
<!--                  ROADMAP                                  -->
<!-- ========================================================= -->

## 🗺️ Roadmap

- [x] ✅ **v1.0** — Client-server dasar (PyQt6 + FastAPI)
- [x] ✅ **v1.5** — JWT Authentication + RBAC
- [x] ✅ **v2.0** — Security & Multi-User
  - [x] Login dialog + show/hide password
  - [x] Role-based access (admin / petugas)
  - [x] Admin panel user management
- [x] ✅ **v3.0** — Satellite & AI Integration
  - [x] NASA FIRMS integration
  - [x] Auto-fetch scheduler
  - [x] Multi-region support
  - [x] Ensemble forecasting (ARIMA + LSTM + GRU)
  - [x] Confidence Interval 95%
  - [x] Time-series cross-validation
  - [x] Anomaly detection (Z+IQR+IF)
  - [x] PFVI Nelder-Mead optimization
  - [x] Telegram alert system
  - [x] Web Dashboard (PWA)
  - [x] Cloudflare Tunnel deployment

- [ ] 🔄 **v3.1** — Enhancement (in progress)
  - [x] Region-specific alerts
  - [x] Broadcast alert system
  - [ ] Interactive map (Leaflet / Mapbox)
  - [ ] Chart export (PNG/PDF)
  - [ ] Email notification
  - [ ] PostgreSQL migration
  - [ ] Docker support

- [ ] ⏳ **v4.0** — Advanced Features
  - [ ] Real-time WebSocket push
  - [ ] Mobile native app (Flutter)
  - [ ] Multi-language support
  - [ ] Advanced ML (Transformer)
  - [ ] Load balancing
  - [ ] Redis caching
  - [ ] CI/CD pipeline

- [ ] 🔮 **v5.0** — Vision
  - [ ] IoT sensor integration
  - [ ] Drone imagery analysis
  - [ ] Public API for researchers
  - [ ] Integration with BMKG & BNPB
  - [ ] National-scale deployment

---

<!-- ========================================================= -->
<!--                  KONTRIBUSI                               -->
<!-- ========================================================= -->

## 🤝 Kontribusi

Kami menerima kontribusi dalam bentuk apapun!

**Alur kontribusi:**
1. Fork repository
2. Buat branch: `git checkout -b feature/FiturKeren`
3. Commit: `git commit -m "Add: FiturKeren"`
4. Push: `git push origin feature/FiturKeren`
5. Buka Pull Request

**Konvensi Commit:**
- `Add:` fitur baru
- `Fix:` bug fix
- `Docs:` dokumentasi
- `Refactor:` perbaikan kode
- `Test:` testing
- `Security:` perbaikan keamanan
- `Perf:` performance improvement

---

<!-- ========================================================= -->
<!--                  LISENSI                                  -->
<!-- ========================================================= -->

## 📜 Lisensi

**MIT License** — bebas dipakai, dimodifikasi, dan didistribusikan, asal sertakan atribusi.

Lihat [LICENSE](LICENSE) untuk detail.

---

<!-- ========================================================= -->
<!--                  KREDIT                                   -->
<!-- ========================================================= -->

## 🙏 Kredit

### 🎓 Inspirasi Ilmiah

Proyek ini terinspirasi dari riset dan pengembangan metodologi **prediksi risiko kebakaran gambut tropis** yang menggunakan pendekatan:

- **Stochastic methods** — ARIMA + Box-Cox transformation
- **Machine learning** — LSTM & GRU neural networks
- **Optimization** — Nelder-Mead untuk kalibrasi indeks kerawanan

Terima kasih kepada para peneliti yang telah membuka jalan di bidang ini. 🌱

### 🔧 Library & Framework

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) — REST API framework
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
- [Pydantic](https://docs.pydantic.dev/) — Data validation
- [python-jose](https://github.com/mpdavis/python-jose) — JWT
- [passlib](https://passlib.readthedocs.io/) + [bcrypt](https://github.com/pyca/bcrypt/) — Password hashing
- [APScheduler](https://apscheduler.readthedocs.io/) — Task scheduling

**Data Science & ML:**
- [pandas](https://pandas.pydata.org/) — Data manipulation
- [numpy](https://numpy.org/) — Numerical computing
- [scikit-learn](https://scikit-learn.org/) — ML algorithms
- [statsmodels](https://www.statsmodels.org/) — Statistical models
- [pmdarima](https://github.com/alkaline-ml/pmdarima) — Auto-ARIMA
- [scipy](https://scipy.org/) — Scientific computing
- [PyTorch](https://pytorch.org/) — Deep learning
- [TensorFlow](https://tensorflow.org/) — Deep learning (alternatif)
- [matplotlib](https://matplotlib.org/) — Plotting

**Frontend & UI:**
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — Desktop GUI
- [Chart.js](https://www.chartjs.org/) — Interactive charts
- [Tailwind-inspired CSS](https://tailwindcss.com/) — Styling

**Integrasi:**
- [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/) — Satellite data
- [Cloudflare Tunnel](https://www.cloudflare.com/products/tunnel/) — Secure tunneling
- [Telegram Bot API](https://core.telegram.org/bots/api) — Notifications

### 🌟 Made in Indonesia

**Dibuat dengan ❤️ untuk konservasi lahan gambut tropis Indonesia** 🇮🇩

---

<!-- ========================================================= -->
<!--                  FOOTER                                  -->
<!-- ========================================================= -->

<div align="center">

### 🌱 "Deteksi dini, lahan gambut aman, Indonesia bebas kabut asap!" 🇮🇩

**GambutFR © 2026** — Open Source under MIT License

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2ecc71,50:10b981,100:0d6efd&height=100&section=footer" width="100%" />

</div>

---
