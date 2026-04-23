# Fullstack Template

Django + Vue 3 + aiogram 3 asosida qurilgan production-ready fullstack template.  
Backend barcha servislar uchun asosiy ma'lumotlar manbai bo'lib xizmat qiladi.

---

## Tarkib

| Servis | Texnologiya | Maqsad |
|---|---|---|
| **Backend** | Django 6, DRF, PostgreSQL, Redis | REST API, JWT autentifikatsiya, biznes mantiq |
| **Frontend** | Vue 3, Vite, Tailwind CSS | Web interfeys, backend API ga ulangan SPA |
| **Bot** | aiogram 3, aiosqlite | Telegram bot, backend orqali user boshqaruvi |

---

## Arxitektura

```
┌─────────────────────────────────────────────────────────┐
│                      Foydalanuvchi                       │
└──────┬──────────────────────────────────┬───────────────┘
       │ Browser                          │ Telegram
       ▼                                  ▼
┌─────────────┐                   ┌───────────────┐
│  Frontend   │                   │      Bot      │
│  Vue 3 SPA  │                   │  aiogram 3    │
│ :5173 (dev) │                   │  polling      │
└──────┬──────┘                   └───────┬───────┘
       │ HTTP/JSON                        │ HTTP/JSON
       │ Bearer JWT                       │ X-Bot-Secret
       ▼                                  ▼
┌──────────────────────────────────────────────────────┐
│                      Backend                          │
│              Django 6 + DRF  :8000                    │
│                                                       │
│  /api/auth/         — JWT autentifikatsiya            │
│  /api/users/        — User CRUD (admin)               │
│  /api/users/me/     — Profil                          │
│  /api/users/        — Telegram ulash/uzish            │
│    by-telegram/     — Bot: user ma'lumotlari          │
│  /api/health/       — Holat tekshiruvi                │
│  /api/swagger/      — API dokumentatsiya              │
└────────────┬──────────────────────────┬──────────────┘
             │                          │
             ▼                          ▼
      ┌─────────────┐          ┌──────────────────┐
      │ PostgreSQL  │          │      Redis        │
      │   :5432     │          │      :6379        │
      │ Asosiy baza │          │  OTP cache        │
      └─────────────┘          │  JWT blacklist    │
                               │  bot:notify ch.   │
                               └────────┬──────────┘
                                        │ pub/sub
                                        ▼
                               ┌──────────────────┐
                               │       Bot        │
                               │  Redis subscriber│
                               │  → Telegram msg  │
                               └──────────────────┘
```

### Servislar o'zaro bog'lanishi

**Frontend → Backend**
- Barcha so'rovlar `VITE_API_URL/api/...` ga ketadi
- `Authorization: Bearer <access_token>` header bilan
- Token muddati tugaganda axios interceptor avtomatik refresh qiladi

**Bot → Backend**
- `GET /api/users/by-telegram/<id>/` — `X-Bot-Secret` header bilan foydalanuvchi ma'lumotlarini oladi
- Backend bot uchun alohida `IsBotService` permission sinfiga ega

**Backend → Bot (notification)**
- Backend `notify_user(telegram_id, message)` funksiyasini chaqiradi
- Bu Redis `bot:notify` kanaliga publish qiladi
- Bot Redis subscriber orqali xabarni qabul qilib Telegram'ga yuboradi

**Frontend ↔ Bot**
- Foydalanuvchi frontend `ProfileView` sahifasida Telegram ID kiritib akkauntini ulaydi
- `POST /api/users/link-telegram/` → `CustomUser.telegram_id` maydoniga yoziladi
- Shundan keyin bot `/start` da foydalanuvchini backenddan topadi

---

## Loyiha strukturasi

```
fullstack-template/
├── backend/                  Django + DRF
│   ├── apps/users/           Yagona app (kengaytirish mumkin)
│   │   ├── models.py         CustomUser modeli
│   │   ├── views.py          Barcha API viewlar
│   │   ├── serializers.py    DRF serializers
│   │   ├── permissions.py    IsRoleAllowed, IsBotService, ...
│   │   ├── utils.py          OTP, email yuborish
│   │   └── notifier.py       Redis pub/sub publisher
│   ├── config/
│   │   ├── settings.py       Django konfiguratsiya
│   │   └── urls.py           URL routing
│   ├── nginx/                Nginx konfiguratsiya
│   ├── requirements.txt
│   └── Dockerfile
│
├── bot/                      aiogram 3 Telegram bot
│   └── app/
│       ├── main.py           Entry point (polling + Redis subscriber)
│       ├── config.py         pydantic-settings
│       ├── routers/          Handler routerlar
│       │   ├── start.py      /start buyruq
│       │   └── admin.py      Admin buyruqlar
│       ├── api/client.py     BackendClient (aiohttp)
│       ├── db/               aiosqlite (bot-specific state)
│       ├── filters/          IsAdmin filter
│       ├── keyboards/        Reply/inline keyboards
│       ├── middlewares/      ApiSessionMiddleware
│       └── states/           FSM state guruhlari
│
├── frontend/                 Vue 3 + Vite + Tailwind
│   └── src/
│       ├── api/              axios instance + auth/users API
│       ├── stores/auth.js    Pinia auth store
│       ├── router/           Vue Router + guards
│       └── views/
│           ├── auth/         Login, Register (3 qadam), ForgotPassword
│           ├── admin/        UserList, UserDetail
│           ├── DashboardView.vue
│           └── ProfileView.vue
│
└── docker-compose.yml        Barcha servislar
```

---

## Mahalliy ishga tushirish

### Talablar

| Vosita | Versiya | Windows | macOS | Linux |
|---|---|---|---|---|
| Python | 3.12+ | [python.org](https://python.org) | `brew install python` | `apt install python3.12` |
| Node.js | 22+ | [nodejs.org](https://nodejs.org) | `brew install node` | `apt install nodejs` |
| PostgreSQL | 16+ | [postgresql.org](https://www.postgresql.org) | `brew install postgresql` | `apt install postgresql` |
| Redis | 7+ | [Redis Windows](https://github.com/tporadowski/redis/releases) | `brew install redis` | `apt install redis` |
| Git | any | [git-scm.com](https://git-scm.com) | `brew install git` | `apt install git` |

> Docker ishlatmoqchi bo'lsangiz faqat Docker Desktop kerak — [Docker bo'limi](#docker-orqali-ishga-tushirish)ga o'ting.

---

### 1. Repozitoriyni klonlash

```bash
git clone <repo-url>
cd fullstack-template
```

---

### 2. Backend sozlash

#### Python virtual muhit

**Windows (PowerShell)**
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Environment faylni tayyorlash

```bash
cp .env.example .env
```

`.env` faylni oching va to'ldiring:

```env
# Django
SECRET_KEY=         # python generate_key.py bilan yarating
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Ma'lumotlar bazasi
USE_POSTGRES=False  # SQLite uchun False, PostgreSQL uchun True

# Agar USE_POSTGRES=True bo'lsa:
DB_NAME=django_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis (lokal)
REDIS_URL=redis://localhost:6379/0

# Email (Gmail SMTP)
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Bot
BOT_SECRET=changeme-shared-secret
```

`SECRET_KEY` yaratish:
```bash
python generate_key.py
```

#### Migratsiya va server

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Backend `http://localhost:8000` da ishga tushadi.  
Swagger: `http://localhost:8000/api/swagger/`

---

### 3. Bot sozlash

Backend bilan **bir xil** virtual muhitdan foydalanish mumkin yoki alohida:

**Windows**
```powershell
cd ..\bot           # yoki bot papkasiga o'ting
pip install -r requirements.txt
```

**macOS / Linux**
```bash
cd ../bot
pip install -r requirements.txt
```

#### Environment

```bash
cp .env.example .env
```

`.env` ni to'ldiring:

```env
BOT_TOKEN=          # @BotFather dan olingan token
ADMINS=[123456789]  # Sizning Telegram user ID (JSON list format)
TIMEZONE=Asia/Tashkent

BACKEND_URL=http://localhost:8000
BOT_SECRET=changeme-shared-secret   # backend .env dagi bilan bir xil bo'lishi shart
REDIS_URL=redis://localhost:6379/0
```

> **Telegram ID ni qanday topish:** `@userinfobot` ga `/start` yuboring.

#### Botni ishga tushirish

```bash
python -m app.main
```

---

### 4. Frontend sozlash

```bash
cd frontend       # yoki fullstack-template/frontend
npm install
```

#### Environment

```bash
cp .env.example .env
```

`.env`:
```env
VITE_API_URL=http://localhost:8000/api
```

#### Dev server

```bash
npm run dev
```

Frontend `http://localhost:5173` da ochiladi.

---

### Barcha servislarni parallel ishga tushirish

Uchta terminal oching:

**Terminal 1 — Backend**
```bash
cd backend
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python manage.py runserver
```

**Terminal 2 — Bot**
```bash
cd bot
# aktivatsiya
python -m app.main
```

**Terminal 3 — Frontend**
```bash
cd frontend
npm run dev
```

---

## Docker orqali ishga tushirish

Docker Desktop o'rnatilgan bo'lsa, barcha servislarni bitta buyruq bilan ishga tushirishingiz mumkin.

### Tayyorlash

Root papkadagi `.env.example` ni ko'chirib, to'ldiring:

**Windows**
```powershell
copy .env.example .env
```

**macOS / Linux**
```bash
cp .env.example .env
```

`.env` faylning asosiy maydonlari:

```env
# Django
SECRET_KEY=            # python backend/generate_key.py
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL (Docker ichida ishlaydi)
USE_POSTGRES=True
DB_NAME=django_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis (Docker ichida ishlaydi)
REDIS_URL=redis://redis:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173

# Email
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Bot
BOT_SECRET=changeme-shared-secret
```

Bot uchun `bot/.env` ni ham to'ldiring (Docker bu faylni o'qiydi):

```env
BOT_TOKEN=your-bot-token
ADMINS=[123456789]
TIMEZONE=Asia/Tashkent
BACKEND_URL=http://backend:8000
BOT_SECRET=changeme-shared-secret
REDIS_URL=redis://redis:6379/0
```

### Ishga tushirish

Loyiha ikkita rejimda ishlaydi — `.env` dagi `USE_POSTGRES` qiymatiga qarab buyruq tanlanadi:

**SQLite (tez ishga tushirish, baza fayl sifatida)**
```bash
# .env da USE_POSTGRES=False bo'lsin
docker compose up --build
```

**PostgreSQL (production uchun tavsiya etiladi)**
```bash
# .env da USE_POSTGRES=True bo'lsin
docker compose --profile postgres up --build
```

| Servis | URL (standart portlar) |
|---|---|
| Frontend | http://localhost:5173 (`FRONTEND_PORT`) |
| Backend API (Nginx orqali) | http://localhost:8001 (`NGINX_PORT`) |
| Swagger API docs | http://localhost:8001/api/swagger/ |
| Django Admin | http://localhost:8001/admin/ |

> PostgreSQL rejimida backend db tayyor bo'lguncha kutadi. SQLite rejimida db container umuman ishga tushmaydi.

### Superuser yaratish (Docker)

```bash
docker compose exec backend python manage.py createsuperuser
```

### Faqat kerakli servisni qayta build qilish

```bash
docker compose up --build backend
docker compose up --build frontend
docker compose up --build bot
```

### Log'larni kuzatish

```bash
docker compose logs -f backend
docker compose logs -f bot
docker compose logs -f frontend
```

---

## API Endpointlar

### Autentifikatsiya

| Metod | URL | Tavsif | Auth |
|---|---|---|---|
| `POST` | `/api/auth/register/send-otp/` | Email ga OTP yuborish | — |
| `POST` | `/api/auth/register/verify/` | OTP tasdiqlash, user yaratish | — |
| `POST` | `/api/auth/register/` | Profil to'ldirish (2-qadam) | JWT |
| `POST` | `/api/auth/register/set-password/` | Parol o'rnatish (3-qadam) | JWT |
| `POST` | `/api/auth/login/` | Kirish | — |
| `POST` | `/api/auth/logout/` | Chiqish (token blacklist) | JWT |
| `POST` | `/api/auth/token/refresh/` | Access token yangilash | — |
| `POST` | `/api/auth/change-password/` | Parol o'zgartirish | JWT |
| `POST` | `/api/auth/forgot-password/` | Parolni tiklash kodi | — |
| `POST` | `/api/auth/forgot-password/verify/` | Yangi parol o'rnatish | — |

### Profil

| Metod | URL | Tavsif | Auth |
|---|---|---|---|
| `GET/PATCH` | `/api/users/me/` | O'z profili | JWT |
| `POST` | `/api/users/link-telegram/` | Telegram ulash | JWT |
| `DELETE` | `/api/users/unlink-telegram/` | Telegram uzish | JWT |

### Admin

| Metod | URL | Tavsif | Auth |
|---|---|---|---|
| `GET` | `/api/users/` | Barcha userlar | JWT + Admin |
| `GET/PATCH/DELETE` | `/api/users/<id>/` | User boshqaruvi | JWT + Admin |

### Bot (ichki)

| Metod | URL | Tavsif | Auth |
|---|---|---|---|
| `GET` | `/api/users/by-telegram/<telegram_id>/` | Telegram bo'yicha user | X-Bot-Secret |

### Tizim

| Metod | URL | Tavsif |
|---|---|---|
| `GET` | `/api/health/` | Backend holati |
| `GET` | `/api/swagger/` | Swagger UI |
| `GET` | `/api/redoc/` | ReDoc |

---

## Ro'yxatdan o'tish jarayoni (3 qadam)

```
1. Email kiriting
   → OTP (6 raqam) emailga yuboriladi (2 daqiqa muddatli)
   ↓
2. OTP tasdiqlang
   → User yaratiladi (GUEST roli, vaqtinchalik parol emailga yuboriladi)
   → JWT tokenlar qaytariladi
   ↓
3. Profil to'ldiring (ixtiyoriy)
   → username, ism, familiya, telefon, avatar
   ↓
4. Doimiy parol o'rnating
   → Rol GUEST → USER ga o'zgaradi
   → Ro'yxatdan o'tish yakunlandi
```

---

## Foydalanuvchi rollari

| Rol | Swagger tagi | Imkoniyatlar |
|---|---|---|
| `guest` | — | Faqat profil ko'rish, parol o'rnatish kutilmoqda |
| `user` | — | To'liq foydalanuvchi imkoniyatlari |
| `admin` | Users (Admin) | Barcha userlarni ko'rish va boshqarish |
| `superadmin` | Users (Admin) | admin + Django admin panel to'liq kirish |

---

## Backend → Bot: xabar yuborish

Backendning istalgan joyidan (view, signal, admin action) bot orqali foydalanuvchiga xabar yuborish:

```python
from apps.users.notifier import notify_user

notify_user(
    telegram_id="123456789",
    message="<b>Yangilik!</b>\n\nSizning so'rovingiz tasdiqlandi.",
    parse_mode="HTML",   # ixtiyoriy, standart HTML
)
```

Mexanizm: `notify_user` → Redis `bot:notify` kanaliga publish → Bot subscriber xabarni qabul qilib Telegram'ga yuboradi.

---

## Bot buyruqlari

| Buyruq | Kim uchun | Tavsif |
|---|---|---|
| `/start` | Hamma | Xush kelibsiz xabari, akkaunt bog'langanligini tekshiradi |
| `/admin` | Adminlar | Admin panel menyusi |
| `/health` | Adminlar | Backend ishlayotganligini tekshiradi |

Yangi handler qo'shish: `bot/app/routers/` papkasida yangi fayl yarating, `bot/app/routers/__init__.py` da `setup_routers()` ga qo'shing.

---

## Bir serverda bir nechta loyiha

Har bir loyiha o'zining `.env` fayliga ega bo'ladi. Faqat ikkita narsa unique bo'lishi shart:

**1. `COMPOSE_PROJECT_NAME`** — Docker container, volume, network nomlariga prefiks qo'shadi:

```
loyiha_A/.env  →  COMPOSE_PROJECT_NAME=shop
loyiha_B/.env  →  COMPOSE_PROJECT_NAME=blog
loyiha_C/.env  →  COMPOSE_PROJECT_NAME=crm
```

Bu avtomatik ravishda ajratadi:
- Volumelar: `shop_postgres_data`, `blog_postgres_data`
- Networklar: `shop_default`, `blog_default`
- Containerlar: `shop-backend-1`, `blog-backend-1`

**2. Tashqi portlar** — har bir loyiha boshqa portdan ochilishi kerak:

```
loyiha_A/.env  →  NGINX_PORT=8001   FRONTEND_PORT=5001
loyiha_B/.env  →  NGINX_PORT=8002   FRONTEND_PORT=5002
loyiha_C/.env  →  NGINX_PORT=8003   FRONTEND_PORT=5003
```

> Ichki servislar (PostgreSQL, Redis, backend gunicorn) port ochmaydi — faqat o'z Docker tarmog'ida ishlaydi. To'qnashuv bo'lmaydi.

**Tekshirish:**
```bash
# Barcha ishlab turgan portlar
docker ps --format "table {{.Names}}\t{{.Ports}}"

# Muayyan loyiha containerlari
docker compose -p shop ps
docker compose -p blog ps
```

---

## Yangi Django app qo'shish

```bash
cd backend
python manage.py startapp myapp apps/myapp
```

`config/settings.py` da `LOCAL_APPS` ga qo'shing:
```python
LOCAL_APPS = [
    "apps.users",
    "apps.myapp",   # yangi
]
```

Fayl strukturasi `apps/users/` bilan bir xil: `models.py`, `views.py`, `serializers.py`, `urls.py`, `permissions.py`.

`config/urls.py` ga URL qo'shing:
```python
path('api/', include('apps.myapp.urls')),
```

---

## Tez-tez uchraydigan muammolar

### Backend

**`django-redis` topilmadi**
```bash
pip install django-redis
```

**Migration xatosi**
```bash
python manage.py migrate --run-syncdb
```

**`Email yuborishda xatolik`**
Gmail uchun [App Password](https://myaccount.google.com/apppasswords) yarating va `EMAIL_HOST_PASSWORD` ga qo'ying. `EMAIL_HOST_USER` gmail manzilingiz bo'lishi kerak.

### Bot

**`ValidationError: ADMINS`**  
`.env` da list format ishlatish kerak: `ADMINS=[123456789]`

**`BOT_TOKEN not provided`**  
`bot/.env` dagi `BOT_TOKEN=` ni to'ldiring.

**Bot xabar olmayapti**  
`BACKEND_URL` ni tekshiring — lokal ishgatushirishda `http://localhost:8000`, Dockerda `http://backend:8000`.

### Frontend

**`Network Error` yoki `CORS`**  
`frontend/.env` dagi `VITE_API_URL` to'g'ri ekanligini tekshiring.  
Backend `.env` dagi `CORS_ALLOWED_ORIGINS` ga frontend URL qo'shilganligini tekshiring.

**`401 Unauthorized`**  
`localStorage` ni tozalang va qayta login qiling:
```javascript
localStorage.clear()
```

---

## Texnologiyalar

**Backend**
- Django 6, Django REST Framework 3.17
- SimpleJWT — JWT autentifikatsiya (access 15 daqiqa, refresh 7 kun)
- drf-spectacular — OpenAPI/Swagger dokumentatsiya
- django-redis — Redis cache (OTP, JWT blacklist)
- PostgreSQL 16 / SQLite (development)
- Gunicorn + Nginx (production)

**Bot**
- aiogram 3.27 — Telegram Bot API
- aiosqlite — bot-specific SQLite baza
- aiohttp — backend API so'rovlari
- redis-py (async) — pub/sub notification

**Frontend**
- Vue 3 (Composition API)
- Vite 8
- Pinia — state management
- Vue Router 4 — client-side routing
- Axios — HTTP client (auto token refresh)
- Tailwind CSS v4
