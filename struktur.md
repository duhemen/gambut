D:\gambut\
│
├── .env
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── environment.yml
├── requirements.txt              ← (bisa jadi pointer ke server+client)
├── requirements-server.txt
├── requirements-client.txt
├── run_hybrid_server.py
├── struktur.md
│
├── server/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt_handler.py
│   │   ├── dependencies.py
│   │   └── password.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── forecasting.py
│   │   ├── imputation.py
│   │   └── index_calc.py
│   └── data/
│       ├── database_gambut.csv
│       ├── sample_satellite.csv
│       ├── users.csv
│       └── config.json
│
├── client/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py                 ← (buat baru)
│   ├── api/
│   │   ├── __init__.py
│   │   └── client.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── forecasting.py
│   │   ├── imputation.py
│   │   └── index_calc.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── login_dialog.py
│   │   ├── main_window.py
│   │   └── tabs/
│   │       ├── __init__.py
│   │       ├── tab_dashboard.py
│   │       ├── tab_default.py
│   │       ├── tab_manual.py
│   │       ├── tab_setting.py
│   │       └── tab_upload.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── data_processor.py
│   └── data/
│       ├── config.json
│       ├── sample_satellite.csv
│       └── template_input.xlsx
│
└── docs/
    ├── cloudflared/
    │   └── config.yml.example
    └── unggah_berkas_excel_csv.png