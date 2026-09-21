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
[![Leaflet](https://img.shields.io/badge/Leaflet-Maps-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](#-lisensi)

[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=for-the-badge)]()
[![Architecture](https://img.shields.io/badge/Architecture-Hybrid%20Decentralized-0d6efd?style=flat-square)](#-arsitektur-sistem)
[![REST API](https://img.shields.io/badge/API-REST%20%2F%20JSON-orange?style=flat-square)](http://cloudflare.tunel.anda/docs)
[![Auth](https://img.shields.io/badge/Auth-JWT%20Bearer-9b59b6?style=flat-square)](#-api-endpoints)
[![PWA](https://img.shields.io/badge/PWA-Mobile%20Ready-5A0FC8?style=flat-square)](https://cloudflare.tunel.anda/dashboard)
[![Wilayah](https://img.shields.io/badge/Wilayah-91.599%20records-success?style=flat-square)](#-peta-choropleth)
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

Sistem ini dibangun untuk **Indonesia**, dengan dukungan **multi-region**, **drill-down wilayah sampai desa**, **peta choropleth interaktif**, **alert Telegram otomatis**, dan **deployment hybrid** yang bisa diakses dari **mana saja, kapan saja** — bahkan dari pelosok hutan gambut.

### 🌱 Yang Membuat GambutFR Berbeda

- 🛰️ **Real-Time Satellite** — integrasi langsung dengan **NASA FIRMS** untuk deteksi hotspot, auto-fetch tiap 6 jam
- 🗺️ **Peta Choropleth Interaktif** — visualisasi PFVI per kabupaten, klik marker untuk drill-down
- 🎯 **Cascade PFVI** — Region → Provinsi → Kabupaten → Kecamatan → Desa
- 📊 **91.599 Records Wilayah** — data Kemendagri 2025 terlengkap di Indonesia
- 🤖 **AI Ensemble** — kombinasi **ARIMA + LSTM + GRU** dengan **confidence interval 95%**
- 📢 **Region-Specific Alert** — Telegram bot kirim notifikasi spesifik wilayah
- 📱 **PWA Mobile** — install di HP seperti app native
- ☁️ **Hybrid Decentralized** — server lokal offline-first, akses global via Cloudflare Tunnel
- 📈 **Export Excel & PDF** — laporan siap kirim ke stakeholder
- 📝 **Audit Log** — semua aktivitas ter-trace
- 👤 **Petugas Wilayah Assignment** — setiap petugas punya wilayah tugas sendiri

> 💡 Terinspirasi dari riset akademik tentang prediksi risiko kebakaran gambut, GambutFR hadir sebagai **implementasi praktis** yang siap dipakai petugas lapangan di seluruh Indonesia.

---

<!-- ========================================================= -->
<!--                  FITUR UTAMA                              -->
<!-- ========================================================= -->

## 🎯 Fitur Utama

<table>
<tr>
<td width="50%">

### 🛰️ Real-Time Satellite
- Integrasi **NASA FIRMS** (VIIRS + MODIS)
- Auto-fetch **3 region** tiap 6 jam
- Konversi hotspot → parameter gambut
- Filter confidence level
- Snapshot per-region tersimpan

### 🗺️ Peta Choropleth Interaktif
- **Leaflet.js** + **Esri Dark Gray** tiles
- Marker per kabupaten dengan warna PFVI
- Klik marker → popup detail wilayah
- Legend: 🟢 Aman 🟡 Siaga 🔴 Bahaya

### 🎯 Cascade PFVI (5 Level)
- Region → Provinsi → Kabupaten → Kecamatan → Desa
- **Inherit cascade** — wilayah tanpa data inherit dari parent
- Klik kabupaten → expand kecamatan → expand desa
- Kode BPS lengkap per wilayah

### 🤖 AI & Machine Learning
- **Ensemble forecast** (ARIMA + LSTM + GRU)
- **Confidence Interval 95%** via bootstrap
- **Time-Series K-Fold** cross-validation
- **Anomaly detection** (Z-score + IQR + Isolation Forest)
- **PFVI** dengan Nelder-Mead optimization

</td>
<td width="50%">

### 📱 Multi-Platform Access
- **Desktop App** (PyQt6) — admin & analis
- **Web Dashboard** (PWA) — akses dari HP
- **REST API** (FastAPI) — 40+ endpoint
- **Mobile-Ready** — install seperti app native

### 📢 Alert & Notification
- **Telegram Bot** otomatis
- **Region-specific** — sebut nama wilayah
- **Broadcast** ke semua region sekaligus
- **Cooldown** anti-spam (5 menit)

### 🔐 Security & Multi-User
- **JWT Authentication** stateless
- **Role-Based Access** (admin / petugas)
- **Bcrypt** password hashing
- **Petugas wilayah assignment**
- **Audit log** semua aktivitas

### 📊 Export & Report
- **Excel** dengan conditional formatting
- **HTML/PDF** untuk print
- Auto-color berdasarkan PFVI status
- Include wilayah lengkap

### ☁️ Hybrid Deployment
- Server lokal (offline-first)
- **Cloudflare Tunnel** gratis HTTPS
- **PWA manifest** install di HP
- **Multi-device** akses bersamaan

</td>
</tr>
</table>

---

<!-- ========================================================= -->
<!--                  SHOWCASE                                 -->
<!-- ========================================================= -->

## ✨ Showcase

### 🌐 Live Demo — Buka dari Mana Saja

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   🔥  https://cloudflare.tunel.anda/dashboard                   │
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

### 🗺️ Peta Choropleth Interaktif

Visualisasi PFVI per kabupaten langsung di atas peta Indonesia:

```
┌────────────────────────────────────────────────────────────┐
│  🗺️  PETA RISIKO KEBAKARAN GAMBUT                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│   Legend: ● Aman (0-39)  ● Siaga (40-64)  ● Bahaya (65+) │
│                                                            │
│   [Peta Indonesia dengan marker per kabupaten]            │
│                                                            │
│   • 🌴 Kalimantan: marker padat 🔴 BAHAYA                 │
│   • 🌳 Sumatera: campuran 🟡🟢🟡                           │
│   • 🦜 Papua: 🟡 SIAGA mayoritas                          │
│                                                            │
│   Klik marker → popup detail wilayah                      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

### 🎯 Drill-Down Wilayah (Sampai Desa)

Dari overview region → sampai detail desa dengan PFVI:

```
┌──────────────────────────────────────────────────────────────┐
│  🌴 KALIMANTAN                                       [X]     │
│  Drill-down wilayah administrasi (Kemendagri 2025)           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Provinsi: 5 │ Kabupaten: 56 │ Kecamatan: 626 │ Desa: 7.179 │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  PFVI REGION INDUK: 83.9/100         🔴 BAHAYA     │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ▼ 📍 Kalimantan Tengah  [3/14 AKTUAL]                      │
│    ┌────────────────────┬───┬────┬───┬──────┬────────┐      │
│    │ Kabupaten/Kota     │Kec│Des │Dat│ PFVI │ Status │      │
│    ├────────────────────┼───┼────┼───┼──────┼────────┤      │
│    │▾ Kota Palangka Raya│ 5 │ 30 │ 3 │ 74.2 │🔴BAHAYA│      │
│    │  ┌──────────────────────────────────────────┐   │      │
│    │  │ KECAMATAN (5)                             │   │      │
│    │  │▸ Pahandut   │6 des│ 2 │74.2*│🔴BAHAYA    │   │      │
│    │  │  ┌──────────────────────────────────────┐ │   │      │
│    │  │  │ DESA/KELURAHAN (6)                   │ │   │      │
│    │  │  │ • Pahandut    50* 🟡 SIAGA          │ │   │      │
│    │  │  │ • Panarung    50* 🟡 SIAGA          │ │   │      │
│    │  │  │ • Langkai     50* 🟡 SIAGA          │ │   │      │
│    │  │  └──────────────────────────────────────┘ │   │      │
│    │  └──────────────────────────────────────────┘   │      │
│    └────────────────────┴───┴────┴───┴──────┴────────┘      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

### 📢 Auto Telegram Alert — Spesifik Region

Setiap kali satelit mendeteksi hotspot di level BAHAYA:

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
│  🔗 Buka Dashboard                                       │
└──────────────────────────────────────────────────────────┘
```

---

### ⏰ Auto-Fetch Scheduler

Server bekerja sendiri — fetch satelit tiap 6 jam:

```
┌────────────────────────────────────────────────────────────┐
│  ⏰ SCHEDULER OTOMATIS                                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Status       : 🟢 RUNNING                                 │
│  Interval     : 6 jam                                      │
│  Total Runs   : 12 kali                                    │
│  Errors       : 0                                          │
│                                                            │
│  Terakhir Jalan : 2026-09-21 14:06:13                      │
│  Berikutnya     : 2026-09-21 20:06:13                      │
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

### 🧠 AI Ensemble Forecasting

Prediksi muka air tanah dengan 3 model AI + CI 95%:

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

### 📊 Export Excel & PDF

Laporan siap kirim dengan warna otomatis berdasarkan status:

```
📄 Laporan_Gambut_Kalimantan_2026-09-21.xlsx

┌──────────────────────────────────────────────────────────────┐
│ Laporan Data Gambut                                          │
│ Generated: 21 September 2026 15:28 WIB                       │
├───┬─────────┬───────┬─────┬────┬────┬────┬────┬────┬────┬────┤
│ # │Tanggal  │Region │Prov │Kab │Kec │Desa│ WT │ SM │PFVI│St  │
├───┼─────────┼───────┼─────┼────┼────┼────┼────┼────┼────┼────┤
│ 1 │2026-09-21│kalim  │...  │... │... │... │-24 │39  │80.7│🔴  │
│ 2 │2026-09-21│papua  │...  │... │... │... │-22 │42  │68  │🔴  │
│ 3 │2026-09-21│suma   │...  │... │... │... │-17 │51  │33  │🟢  │
└───┴─────────┴───────┴─────┴────┴────┴────┴────┴────┴────┴────┘
```

---

### 🔐 Multi-User dengan Wilayah Assignment

Setiap petugas punya wilayah tugas sendiri:

```
┌──────────────────────────────────────────────────────┐
│  👥 MANAJEMEN USER                                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Username     Role      Wilayah         Status      │
│  ─────────    ─────     ──────────      ─────────   │
│  admin        admin     -               🟢 Active   │
│  budi_riau    petugas   Pekanbaru       🟢 Active   │
│  siti_kalteng petugas   Kalteng         🟢 Active   │
│  ahmad_papua  petugas   Jayapura        🟢 Active   │
│                                                      │
│  Setiap aksi ter-audit di log server.                │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

### 📱 PWA — Install di HP

Buka di HP → "Add to Home Screen" → icon 🔥 muncul:

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

### 🎨 Aurora Dark Theme

UI dengan efek **Aurora gradient** + **glassmorphism cards**:

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
    │         💻 LOKAL SERVER                          │
    ├──────────────────────────────────────────────────┤
    │                                                  │
    │  ┌────────────────────────────────────────────┐  │
    │  │  FastAPI Backend (:8000) — 40+ endpoints   │  │
    │  │  ┌──────────────┐  ┌──────────────────┐   │  │
    │  │  │ Auth Layer   │  │ Scheduler Layer  │   │  │
    │  │  │ • JWT verify │  │ • Auto-fetch 6h  │   │  │
    │  │  │ • RBAC       │  │ • NASA FIRMS     │   │  │
    │  │  │ • Wilayah    │  │ • Alert          │   │  │
    │  │  └──────────────┘  └──────────────────┘   │  │
    │  │  ┌──────────────┐  ┌──────────────────┐   │  │
    │  │  │ AI Engine    │  │ Audit & Export   │   │  │
    │  │  │ • Ensemble   │  │ • Activity log   │   │  │
    │  │  │ • Anomaly    │  │ • Excel + PDF    │   │  │
    │  │  │ • PFVI       │  │ • Telegram Bot   │   │  │
    │  │  └──────────────┘  └──────────────────┘   │  │
    │  └────────────────────────────────────────────┘  │
    │                                                  │
    │  ┌────────────────────────────────────────────┐  │
    │  │  Storage Layer                             │  │
    │  │  • database_gambut.csv  (observasi)        │  │
    │  │  • wilayah.db (SQLite, 91.599 records)     │  │
    │  │  • users.csv, audit_log.jsonl              │  │
    │  │  • regional_latest.json, pfvi_params.json  │  │
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
| **Multi-User** | JWT + RBAC + wilayah assignment |
| **Autonomous** | Scheduler otomatis fetch + alert |
| **Progressive** | PWA installable di HP tanpa Play Store |
| **Traceable** | Audit log setiap aktivitas |

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
│
├── 📁 client/                      # ⭐ DESKTOP APP (PyQt6)
│   ├── main.py                     # Entry point desktop
│   ├── config.py                   # Config URL & timeout
│   ├── 📁 api/client.py            # HTTP Client
│   ├── 📁 core/                    # Business logic
│   ├── 📁 gui/
│   │   ├── theme.py                # 🎨 Tema Aurora Dark
│   │   ├── widgets/                # KpiCard, RegionSelector
│   │   ├── main_window.py
│   │   ├── login_dialog.py
│   │   └── 📁 tabs/                # 6 tab lengkap
│   │       ├── tab_dashboard.py
│   │       ├── tab_manual.py       # Region-aware
│   │       ├── tab_upload.py       # Region-aware
│   │       ├── tab_anomaly.py
│   │       ├── tab_scheduler.py
│   │       └── tab_setting.py
│   └── 📁 utils/
│
├── 📁 server/                      # ⭐ BACKEND (FastAPI)
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── 📁 auth/                    # JWT + RBAC
│   ├── 📁 api/
│   │   ├── routes.py               # 40+ endpoints
│   │   └── web.py                  # Serve dashboard HTML
│   ├── 📁 core/                    # ⭐ AI ENGINE
│   │   ├── imputation.py           # KNN / Spline / Linear / Loess
│   │   ├── forecasting.py          # ARIMA + Box-Cox
│   │   ├── deep_learning.py        # LSTM / GRU (PyTorch)
│   │   ├── ensemble.py             # Ensemble + CI + CV
│   │   ├── index_calc.py           # PFVI Nelder-Mead
│   │   ├── anomaly.py              # Z-score + IQR + IF
│   │   ├── satellite.py            # NASA FIRMS integration
│   │   ├── scheduler.py            # Auto-fetch scheduler
│   │   ├── alert.py                # Telegram notifications
│   │   ├── audit.py                # Activity log
│   │   ├── export.py               # Excel + HTML export
│   │   ├── regions.py              # Wilayah helper (SQLite)
│   │   ├── pfvi_cache.py           # Cached PFVI params
│   │   └── autopeatfr.py           # All-in-one pipeline
│   ├── 📁 templates/               # Web dashboard + PWA
│   │   ├── dashboard.html
│   │   ├── manifest.json
│   │   └── sw.js
│   ├── 📁 static/
│   │   ├── 📁 geo/                 # GeoJSON peta
│   │   └── 📁 icons/               # PWA icons
│   └── 📁 data/                    # 💾 Storage (gitignored)
│       ├── regions.json            # Template wilayah
│       ├── sample_satellite.csv    # Sample
│       └── wilayah.db              # SQLite (91.599 records)
│
├── 📁 docs/                        # 📚 Documentation
│   ├── 📁 cloudflared/
│   └── 📁 screenshots/
│
├── 📁 tests/                       # 🧪 Unit tests
│
└── 📁 scripts/                     # 🛠️ Utility scripts
    ├── download_wilayah.py
    ├── build_wilayah_db.py
    └── migrate_add_region.py
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
| **Storage** | 2 GB | 5 GB (dengan PyTorch) |
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

### Tahap 5 — Setup Wilayah Database (SQLite)

```bash
# Download wilayah.sql dari cahyadsn (Kemendagri 2025)
python scripts/download_wilayah.py

# Build SQLite database (~15 MB, 91.599 records)
python scripts/build_wilayah_db.py
```

### Tahap 6 — Dapatkan API Keys

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
- **Cloudflare**: https://cloudflare.tunel.anda/dashboard

### 📱 Install PWA di HP

1. Buka `https://cloudflare.tunel.anda/dashboard` di Chrome/Safari HP
2. Menu → **"Add to Home Screen"**
3. Icon 🔥 muncul → buka seperti app native

---

<!-- ========================================================= -->
<!--                  PANDUAN PENGGUNAAN                       -->
<!-- ========================================================= -->

## 📚 Panduan Penggunaan

### 1. 🔐 Login Screen
- JWT authentication
- Password ter-hash bcrypt
- Role-based UI (tab Setting hanya untuk admin)

### 2. 📊 Dashboard
- **KPI Cards**: Total observasi, WT, Suhu, PFVI
- **Tabel Data Petugas**: Per-region feed
- **Kartu Regional**: Ringkasan per region (klik → drill-down)
- **Peta Choropleth**: Marker PFVI per kabupaten
- **Chart Tren WT** + **Diagram Pie**
- **Tombol Sync Satelit** & **Broadcast Alert**
- **Export Excel/PDF**

### 3. 🗺️ Peta Choropleth
- Klik marker → popup detail wilayah
- Klik kartu region → modal drill-down
- Klik kabupaten → expand kecamatan
- Klik kecamatan → expand desa

### 4. ✍️ Input Manual (Region-Aware)
- Cascading dropdown: Region → Provinsi → Kabupaten → Kecamatan → Desa
- Isi WT, SM, RF, Temp
- Preview PFVI real-time
- Auto-alert saat BAHAYA/SIAGA

### 5. 📁 Upload Data (Region-Aware)
- Cascading dropdown lokasi
- Drag & drop CSV/Excel
- Auto-validasi kolom

### 6. 🔍 Anomaly Detection
- Ensemble voting (Z-score + IQR + IF)
- Deteksi outlier otomatis
- Detail alasan per data

### 7. ⏰ Scheduler
- Status RUNNING/STOPPED
- Interval configurable
- Trigger manual

### 8. ⚙️ Pengaturan (Admin Only)
- URL Server
- API Satelit
- Tema aplikasi

---

<!-- ========================================================= -->
<!--                  API ENDPOINTS                            -->
<!-- ========================================================= -->

## 🔌 API Endpoints

**Swagger UI**: http://localhost:8000/docs

### 🔐 Authentication
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| `POST` | `/api/v1/auth/register` | Daftar user baru (admin) |
| `POST` | `/api/v1/auth/login` | Login → JWT token |
| `GET` | `/api/v1/auth/me` | Info user login |
| `GET` | `/api/v1/auth/users` | Daftar user (admin) |

### 📊 Data & Analytics
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| `GET` | `/api/v1/data` | Data historis |
| `POST` | `/api/v1/data` | Input manual |
| `POST` | `/api/v1/data/upload` | Upload CSV/Excel |
| `GET` | `/api/v1/data/public` | Public data feed |

### 🛰️ Satellite
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| `POST` | `/api/v1/satellite/fetch` | Fetch NASA FIRMS |
| `GET` | `/api/v1/satellite/regional-summary` | Ringkasan per region |

### 🗺️ Wilayah & Peta
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| `GET` | `/api/v1/regions/tree` | Struktur region |
| `GET` | `/api/v1/wilayah/provinces` | List provinsi |
| `GET` | `/api/v1/wilayah/{prov}/regencies` | List kabupaten |
| `GET` | `/api/v1/wilayah/regency/{kode}/districts-detail` | Kecamatan + PFVI |
| `GET` | `/api/v1/wilayah/district/{kode}/villages-detail` | Desa + PFVI |
| `GET` | `/api/v1/wilayah/stats/{region}` | Statistik + drill-down |
| `GET` | `/api/v1/map/data` | Data untuk choropleth |

### 🧠 AI & Forecasting
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| `POST` | `/api/v1/forecast` | Forecast WT |
| `POST` | `/api/v1/forecast/ensemble` | Ensemble + CI |
| `POST` | `/api/v1/forecast/cross-validate` | K-Fold CV |
| `POST` | `/api/v1/index` | Hitung PFVI |
| `POST` | `/api/v1/anomaly/detect` | Deteksi anomali |
| `POST` | `/api/v1/autopeatfr` | All-in-one pipeline |

### 📢 Alert
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| `GET` | `/api/v1/alert/status` | Status alert |
| `POST` | `/api/v1/alert/config` | Update config |
| `POST` | `/api/v1/alert/broadcast-public` | Broadcast semua region |

### ⏰ Scheduler
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| `GET` | `/api/v1/scheduler/status` | Status scheduler |
| `POST` | `/api/v1/scheduler/start` | Start scheduler |
| `POST` | `/api/v1/scheduler/stop` | Stop scheduler |
| `POST` | `/api/v1/scheduler/trigger` | Trigger manual |

### 📊 Export & Audit
| Method | Endpoint | Fungsi |
|--------|----------|--------|
| `GET` | `/api/v1/export/excel` | Download Excel |
| `GET` | `/api/v1/export/html` | Download PDF (via HTML) |
| `GET` | `/api/v1/audit/recent` | Audit log terbaru |
| `GET` | `/api/v1/audit/stats` | Statistik audit |

---

<!-- ========================================================= -->
<!--                  TESTING & DEBUGGING                      -->
<!-- ========================================================= -->

## 🧪 Testing & Debugging

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
- Domain (mis. `cloudflare.tunel.anda`)
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
https://cloudflare.tunel.anda/dashboard
```

</details>

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
- [x] ✅ **v3.1** — Advanced Features
  - [x] Region-specific alerts
  - [x] Broadcast alert system
  - [x] Interactive choropleth map (Leaflet.js)
  - [x] Drill-down wilayah sampai level desa (91.599 records)
  - [x] Export Excel + PDF
  - [x] Petugas wilayah assignment
  - [x] Audit log semua aktivitas
  - [x] Cascade PFVI (Region → Provinsi → Kab → Kec → Desa)
- [ ] ⏳ **v4.0** — Future Enhancement (Vision)
  - [ ] Real-time WebSocket push
  - [ ] Mobile native app (Flutter/React Native)
  - [ ] Timeline slider untuk evolusi PFVI
  - [ ] Email report otomatis harian
  - [ ] PostgreSQL migration untuk scale up
  - [ ] Docker support untuk deployment
  - [ ] Advanced ML (Transformer models)
  - [ ] Layer NASA FIRMS hotspot di peta
  - [ ] IoT sensor integration
  - [ ] Drone imagery analysis
  - [ ] Integration dengan BMKG & BNPB
  - [ ] Public API untuk peneliti
  - [ ] CI/CD pipeline (GitHub Actions)
  - [ ] Multi-language support (ID / EN)

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

### 📊 Data Sumber

- **Wilayah Indonesia**: [cahyadsn/wilayah](https://github.com/cahyadsn/wilayah) — sesuai **Kepmendagri No 300.2.2-2430 Tahun 2025**
  - 38 Provinsi, 514 Kabupaten/Kota, 7.285 Kecamatan, 83.762 Desa/Kelurahan
- **Satelit**: [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/) (Fire Information for Resource Management System)
- **Tiles Peta**: [Esri World Dark Gray](https://www.esri.com/)

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
- [matplotlib](https://matplotlib.org/) — Plotting

**Frontend & UI:**
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — Desktop GUI
- [Chart.js](https://www.chartjs.org/) — Interactive charts
- [Leaflet.js](https://leafletjs.com/) — Interactive maps

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
