# Sales_AI_Agent_backendbackend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPIアプリケーション
│   ├── config.py            # 設定管理
│   ├── models/              # Pydanticモデル
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── api/                 # APIエンドポイント
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── dependencies.py
│   ├── services/            # ビジネスロジック
│   │   ├── __init__.py
│   │   ├── company_service.py
│   │   ├── gemini_service.py
│   │   └── solution_service.py
│   ├── utils/               # ユーティリティ
│   │   ├── __init__.py
│   │   └── web_scraper.py
│   └── data/               # データファイル
│       ├── company_codes.py
│       ├── solutions.json
│       └── prompts/
│           ├── prompt.txt
│           ├── hypothesis_prompt.txt
│           ├── hearing_prompt.txt
│           └── solution_matching_prompt.txt
├── requirements.txt
├── .env
└── run.py                  # アプリケーション起動用


