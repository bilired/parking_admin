
Hong Kong Parking Management System — 基於 Vue3 + Django + Mapbox + MySQL 構建。

## 功能特性

- **用戶登入 / 註冊** — JWT 認證，Token 自動刷新
<img width="1920" height="849" alt="image" src="https://github.com/user-attachments/assets/e3bb7de1-effa-47e7-8b1f-0ca5d559b89d" />
<img width="1920" height="845" alt="image" src="https://github.com/user-attachments/assets/8a8a0662-91e4-4386-bb04-d43cc92f672f" />

- **停車場搜索** — 按名稱、地址、地區篩選全港停車場
<img width="1920" height="848" alt="image" src="https://github.com/user-attachments/assets/4b1af1ed-e9a4-42c2-9407-171de2f32457" />

- **實時空位** — 對接香港運輸署實時数据 API
- **地圖展示** — Mapbox Dark 风格地圖，顏色標記空位狀態
  - 🟢 綠色：空位充足（≥10）
  - 🟡 黃色：空位不足（< 10）
  - 🔴 紅色：已滿
  - 🔵 藍色：無空位數據（停車場未提供實時資料）
- **收藏功能** — 收藏常用停車場，分頁集中管理
<img width="1920" height="849" alt="image" src="https://github.com/user-attachments/assets/39b102f3-97d3-471f-95c9-67d7d2edc9ce" />
<img width="1920" height="834" alt="image" src="https://github.com/user-attachments/assets/ec175e0e-4029-45d7-bd28-1c1dc9347186" />
- 駕車導航：點擊停車場卡片「導航」按鈕，自動以 GPS 當前位置為起點，目標停車場為終點規劃路線
<img width="1542" height="849" alt="image" src="https://github.com/user-attachments/assets/97d15ac6-b3ab-414a-9101-849d661ea559" />
- 路線模式：支持駕車 / 步行 / 單車切換

- 逐步指引：提供文字導航步驟及預計時間

- 地圖點選：可點擊地圖任意位置手動設置起點 / 終點

- 面板收折：導航面板可隨時展開 / 收起

- GPS 定位：一鍵定位，支持實時追蹤和方向顯示

- 底圖切換：5 種地圖風格（深色 / 淺色 / 街道 / 戶外 / 衛星）
<img width="1540" height="842" alt="image" src="https://github.com/user-attachments/assets/63b04a6d-dffd-4ecf-a12c-06ae49b9168d" />

- **Mapbox Token 後端保管** — Token 存儲在 Django 後端，不暴露於前端代碼

## 技術棧

| 端 | 技術 |
|---|---|
| 前端 | Vue 3 + TypeScript + Vite |
| UI | Element Plus |
| 狀態 | Pinia |
| 地圖 | Mapbox GL JS v3 |
| 後端 | Django 4.2 + DRF |
| 認證 | JWT (djangorestframework-simplejwt) |
| 數據庫 | MySQL 8 |
| 數據源 | 香港運輸署停車場 API |

## 項目結構

```
parking_admin/
├── backend/                  # Django 後端
│   ├── parking_backend/      # 主項目配置
│   ├── users/                # 用戶認證模塊
│   ├── carparks/             # 停車場 & 收藏模塊
│   ├── requirements.txt
│   ├── .env                  # 環境變量（不提交 git）
│   └── .env.example          # 環境變量模板
└── frontend/                 # Vue3 前端
    ├── src/
    │   ├── api/              # Axios 請求封裝
    │   ├── stores/           # Pinia 狀態管理
    │   ├── views/            # 頁面組件
    │   ├── components/       # 通用組件
    │   ├── router/           # Vue Router
    │   └── types/            # TypeScript 類型定義
    └── package.json
```

## 快速開始

### 前置條件

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Mapbox 賬號（免費註冊獲取 Token）

### 1. 配置 MySQL 數據庫

```sql
CREATE DATABASE parking_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 後端設置

```bash
cd backend

# 創建虛擬環境
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 複製並編輯環境變量
cp .env.example .env
# 編輯 .env，填入以下配置：
# SECRET_KEY=（隨機字符串，可用 python -c "import secrets; print(secrets.token_hex(32))" 生成）
# DB_PASSWORD=（你的 MySQL 密碼）
# MAPBOX_TOKEN=（你的 Mapbox public token，以 pk. 開頭）

# 執行數據庫遷移
python manage.py makemigrations
python manage.py migrate

# 創建超級管理員（可選）
python manage.py createsuperuser

# 啟動後端（默認 8000 端口）
python manage.py runserver
```

### 3. 前端設置

```bash
cd frontend

# 安裝依賴
npm install

# 啟動開發服務器（默認 5173 端口）
npm run dev
```

### 4. 訪問系統

- 前端：http://localhost:5173
- 後端 API：http://localhost:8000/api/
- Django Admin：http://localhost:8000/admin/

## API 端點

### 認證

| 方法 | 路徑 | 說明 |
|---|---|---|
| POST | `/api/auth/register/` | 用戶註冊 |
| POST | `/api/auth/login/` | 用戶登入 |
| POST | `/api/auth/logout/` | 用戶登出 |
| GET | `/api/auth/me/` | 獲取當前用戶 |
| POST | `/api/auth/token/refresh/` | 刷新 JWT Token |

### 停車場

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/api/carparks/` | 搜索停車場（?search=xxx&district=xxx）|
| GET | `/api/carparks/vacancy/` | 實時空位（?ids=TD01,TD02）|
| GET | `/api/carparks/districts/` | 獲取地區列表 |
| GET | `/api/config/mapbox-token/` | 獲取 Mapbox Token（需登入）|

### 收藏

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/api/favorites/` | 獲取收藏列表 |
| POST | `/api/favorites/add/` | 添加收藏 |
| DELETE | `/api/favorites/{carparkId}/` | 取消收藏 |

## 數據源

停車場數據來源：[香港政府數據一站通 - 停車場資料及空缺](https://data.gov.hk/tc-data/dataset/hk-dpo-datagovhk1-carpark-info-vacancy)

- 靜態資料：`https://resource.data.one.gov.hk/td/carpark/carparkDat.json`
- 實時空位：`https://resource.data.one.gov.hk/td/carpark/carparkVacancy.json`

## 獲取 Mapbox Token

1. 前往 [mapbox.com](https://www.mapbox.com) 免費註冊
2. 進入帳號 → Access Tokens
3. 複製以 `pk.` 開頭的 Default Public Token
4. 填入 `backend/.env` 的 `MAPBOX_TOKEN` 字段

## 環境變量說明

```env
SECRET_KEY=          # Django 密鑰（必填，生產環境需替換）
DEBUG=True           # 開發模式
DB_NAME=parking_db   # MySQL 數據庫名
DB_USER=root         # MySQL 用戶名
DB_PASSWORD=         # MySQL 密碼（必填）
DB_HOST=127.0.0.1    # MySQL 主機
DB_PORT=3306         # MySQL 端口
MAPBOX_TOKEN=        # Mapbox Public Token（必填）
ALLOWED_HOSTS=localhost,127.0.0.1
```
