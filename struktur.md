peatfr-pyqt/
├── main.py                      # Client entry point
├── requirements-client.txt
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── client.py            # HTTP client
│   ├── utils/
│   │   ├── __init__.py
│   │   └── data_processor.py    # (REFACTORED - via API)
│   └── gui/
│       ├── __init__.py
│       ├── main_window.py
│       └── tabs/
│           ├── __init__.py
│           ├── tab_dashboard.py
│           ├── tab_default.py
│           ├── tab_manual.py
│           ├── tab_setting.py
│           └── tab_upload.py
│
└── server/                      # ⚙️ SERVER (BARU)
    ├── __init__.py
    ├── main.py                  # FastAPI entry
    ├── database.py              # Data layer
    ├── models.py                # Pydantic models
    ├── requirements-server.txt
    ├── api/
    │   ├── __init__.py
    │   └── routes.py
    ├── core/
    │   ├── __init__.py
    │   ├── imputation.py
    │   ├── forecasting.py
    │   └── index_calc.py
    └── data/
        ├── database_gambut.csv
        ├── sample_satellite.csv
        └── config.json