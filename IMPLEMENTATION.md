# IMPLEMENTATION.md

Fullstack template ni production-ready holatga keltirish uchun to'liq rejasi.  
Har bir bo'lim **nima bor → nima qilish kerak → qanday ulangan** shaklida yozilgan.

---

## 1. BACKEND — Buglar va yetishmayotgan qismlar

### 1.1 Models.py — Typo xato (kritik)

`apps/users/models.py` da 71–72-satrlarda `fileds` (noto'g'ri) o'rniga `fields` bo'lishi kerak.  
Bu migration yaratishni sindiradi.

```python
# NOTO'G'RI (hozir)
models.Index(fileds=["telegram_id"]),
models.Index(fileds=["username"]),

# TO'G'RI
models.Index(fields=["telegram_id"]),
models.Index(fields=["username"]),
```

### 1.2 entrypoint.sh — Bo'sh fayl (kritik)

`backend/entrypoint.sh` bo'sh. Docker'da backend ishlamaydi.

```bash
#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"
```

### 1.3 Root docker-compose.yml — Bo'sh (kritik)

`docker-compose.yml` (root) bo'sh. Barcha servislarni birga ishlatish uchun to'ldirilishi kerak:

```yaml
services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  backend:
    build: ./backend
    restart: unless-stopped
    env_file: .env
    depends_on:
      - db
      - redis
    volumes:
      - ./backend/static:/app/static
      - ./backend/media:/app/media
      - ./backend/logs:/app/logs

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "8001:80"
    depends_on:
      - backend
    volumes:
      - ./backend/nginx/default.conf:/etc/nginx/conf.d/default.conf
      - ./backend/static:/app/static
      - ./backend/media:/app/media

  bot:
    build: ./bot
    restart: unless-stopped
    env_file: ./bot/.env
    depends_on:
      - backend
    volumes:
      - ./bot/logs:/app/logs

volumes:
  postgres_data:
```

### 1.4 Backend requirements.txt — yetishmayotgan paketlar

Quyidagi paketlar kerak bo'ladi lekin mavjud emas:
- `django-redis` — `CACHES` konfiguratsiyada ishlatilgan lekin o'rnatilmagan
- `gunicorn` — Dockerfile'da CMD da ishlatilgan lekin requirements'da yo'q
- `pydantic-settings` — bot uchun (bot alohida requirements kerak)

### 1.5 Bot `app/routers.py` — Mavjud emas (kritik)

`bot/app/main.py` da `from app.routers import setup_routers` importi bor, lekin fayl yo'q.  
Bot hozir umuman ishlamaydi.

---

## 2. BOT — To'liq implementatsiya

Bot backend API bilan `aiohttp` orqali gaplashadi. Bot o'z SQLite bazasini faqat Telegram-specific ma'lumotlar uchun ishlatadi (masalan: til, menyu holati). Asosiy user ma'lumotlari backendda.

### 2.1 Bot fayl strukturasi (kerak bo'ladiganlari)

```
bot/app/
├── routers.py              # setup_routers() — barcha routerlarni birlashtiradi
├── routers/
│   ├── __init__.py
│   ├── start.py            # /start handler
│   └── admin.py            # admin buyruqlar
├── api/
│   ├── __init__.py
│   └── client.py           # Backend API client (aiohttp)
├── db/
│   ├── database.py         # aiosqlite connection (bot-specific state)
│   ├── queries.py          # bot DB so'rovlari
│   └── helper.py           # DB helper utilities
├── filters/
│   └── is_admin.py         # IsAdmin filter (settings.admins ga asoslanadi)
├── keyboards/
│   ├── admin_kb.py         # Admin reply/inline keyboards
│   └── user_kb.py          # User keyboards
├── states/
│   ├── __init__.py
│   └── registration.py     # FSM states (agar kerak bo'lsa)
├── middlewares/
│   ├── __init__.py
│   └── api_session.py      # aiohttp session ni har bir handlerga inject qilish
└── utils/
    └── storage_holder.py   # MemoryStorage yoki RedisStorage uchun holder
```

### 2.2 Backend API Client (`bot/app/api/client.py`)

Bot backend bilan qanday gaplashadi:

```python
import aiohttp
from app.config import settings

class BackendClient:
    """Backend REST API bilan ishlash uchun client."""
    
    BASE_URL = settings.backend_url  # .env dan olinadi
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> dict | None:
        """Telegram ID orqali backend'dan user ma'lumotlarini olish."""
        async with self.session.get(
            f"{self.BASE_URL}/api/users/by-telegram/{telegram_id}/",
            headers={"X-Bot-Secret": settings.bot_secret}
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            return None
    
    async def link_telegram(self, user_id: int, telegram_id: int, token: str) -> bool:
        """Telegram accountni backend user ga ulash."""
        async with self.session.post(
            f"{self.BASE_URL}/api/users/link-telegram/",
            json={"telegram_id": telegram_id},
            headers={"Authorization": f"Bearer {token}"}
        ) as resp:
            return resp.status == 200
    
    async def health(self) -> bool:
        """Backend health check."""
        try:
            async with self.session.get(f"{self.BASE_URL}/api/health/") as resp:
                return resp.status == 200
        except Exception:
            return False
```

### 2.3 Config ga qo'shilishi kerak bo'lgan o'zgaruvchilar

`bot/app/config.py` ga qo'shish:
```python
backend_url: str = Field(default="http://backend:8000", alias="BACKEND_URL")
bot_secret: str = Field(alias="BOT_SECRET")  # backend bilan autentifikatsiya uchun
```

`bot/.env.example` ga qo'shish:
```
BACKEND_URL=http://backend:8000
BOT_SECRET=some-shared-secret
```

### 2.4 aiohttp session middleware (`bot/app/middlewares/api_session.py`)

Har bir handler uchun session inject:
```python
from aiogram import BaseMiddleware
import aiohttp

class ApiSessionMiddleware(BaseMiddleware):
    def __init__(self):
        self.session: aiohttp.ClientSession | None = None
    
    async def __call__(self, handler, event, data):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        data["api_session"] = self.session
        return await handler(event, data)
```

### 2.5 IsAdmin filter (`bot/app/filters/is_admin.py`)

```python
from aiogram.filters import BaseFilter
from aiogram.types import Message
from app.config import settings

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in settings.admins
```

### 2.6 Routers (`bot/app/routers.py`)

```python
from aiogram import Router
from app.routers.start import router as start_router
from app.routers.admin import router as admin_router

def setup_routers() -> Router:
    main_router = Router()
    main_router.include_router(start_router)
    main_router.include_router(admin_router)
    return main_router
```

### 2.7 Bot requirements.txt (alohida fayl kerak)

`bot/requirements.txt`:
```
aiogram==3.27.0
aiohttp==3.13.5
aiofiles==25.1.0
pydantic-settings==2.9.1
pydantic==2.12.5
tzdata==2026.1
```

### 2.8 Backend tomonida bot uchun endpoint'lar

Backendga qo'shilishi kerak:
- `GET /api/users/by-telegram/<telegram_id>/` — bot user ma'lumotlarini oladi (X-Bot-Secret header)
- `POST /api/users/link-telegram/` — authenticated user o'z telegram_id'sini ulaydi
- `POST /api/bot/notify/<user_id>/` — backend bot orqali user ga xabar jo'natadi (webhook style yoki polling orqali)

Backend tomonida `X-Bot-Secret` ni tekshiruvchi permission:
```python
# apps/users/permissions.py ga qo'shish
class IsBotService(BasePermission):
    def has_permission(self, request, view):
        secret = request.headers.get("X-Bot-Secret")
        return secret == settings.BOT_SECRET  # django settings dan
```

---

## 3. FRONTEND — To'liq implementatsiya (Vue.js)

### 3.1 Scaffold

```bash
npm create vue@latest frontend
# Options: Vue Router: Yes, Pinia: Yes, Vitest: Yes, ESLint: Yes, Prettier: Yes
cd frontend
npm install axios
npm install @vueuse/core  # composable utilities
```

### 3.2 Fayl strukturasi

```
frontend/
├── src/
│   ├── api/
│   │   ├── index.js        # axios instance (interceptors)
│   │   ├── auth.js         # auth API calls
│   │   └── users.js        # users API calls
│   ├── stores/
│   │   ├── auth.js         # Pinia: token, user, isAuthenticated
│   │   └── ui.js           # Pinia: loading, notifications
│   ├── router/
│   │   └── index.js        # Vue Router + navigation guards
│   ├── views/
│   │   ├── auth/
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue      # 3-step registration
│   │   │   └── ForgotPasswordView.vue
│   │   ├── profile/
│   │   │   └── ProfileView.vue
│   │   ├── admin/
│   │   │   ├── UserListView.vue
│   │   │   └── UserDetailView.vue
│   │   └── HomeView.vue
│   ├── components/
│   │   ├── AppHeader.vue
│   │   ├── AppNotification.vue
│   │   └── auth/
│   │       └── RegisterStepper.vue   # 3-step registration wizard
│   └── main.js
├── .env
├── .env.example
├── Dockerfile
├── nginx.conf                # frontend nginx (SPA fallback)
└── package.json
```

### 3.3 Axios instance (`frontend/src/api/index.js`)

```javascript
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,  // http://localhost:8000/api
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor: har so'rovga token qo'shish
api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

// Response interceptor: 401 da token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const auth = useAuthStore()
      const ok = await auth.refreshToken()
      if (ok) {
        original.headers.Authorization = `Bearer ${auth.accessToken}`
        return api(original)
      }
      auth.logout()
    }
    return Promise.reject(error)
  }
)

export default api
```

### 3.4 Auth store (`frontend/src/stores/auth.js`)

```javascript
import { defineStore } from 'pinia'
import api from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('access') || null,
    refreshToken: localStorage.getItem('refresh') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),
  getters: {
    isAuthenticated: (s) => !!s.accessToken,
    isAdmin: (s) => ['admin', 'superadmin'].includes(s.user?.role),
  },
  actions: {
    setTokens({ access, refresh, user }) {
      this.accessToken = access
      this.refreshToken = refresh
      this.user = user
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
      localStorage.setItem('user', JSON.stringify(user))
    },
    async refreshToken() {
      try {
        const { data } = await api.post('/auth/token/refresh/', { refresh: this.refreshToken })
        this.accessToken = data.access
        localStorage.setItem('access', data.access)
        return true
      } catch {
        return false
      }
    },
    logout() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      localStorage.clear()
    },
  },
})
```

### 3.5 Router va navigation guards (`frontend/src/router/index.js`)

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', component: () => import('@/views/HomeView.vue'), meta: { requiresAuth: true } },
  { path: '/login', component: () => import('@/views/auth/LoginView.vue'), meta: { guest: true } },
  { path: '/register', component: () => import('@/views/auth/RegisterView.vue'), meta: { guest: true } },
  { path: '/forgot-password', component: () => import('@/views/auth/ForgotPasswordView.vue'), meta: { guest: true } },
  { path: '/profile', component: () => import('@/views/profile/ProfileView.vue'), meta: { requiresAuth: true } },
  {
    path: '/admin/users',
    component: () => import('@/views/admin/UserListView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) return '/login'
  if (to.meta.guest && auth.isAuthenticated) return '/'
  if (to.meta.requiresAdmin && !auth.isAdmin) return '/'
})

export default router
```

### 3.6 3-bosqichli ro'yxatdan o'tish (`RegisterView.vue`)

```
Step 1: Email kiritish → "Kod yuborish" → OTP input
Step 2: Profil (username, first_name, last_name, phone) — ixtiyoriy
Step 3: Parol o'rnatish
```

Har bir qadam so'ng JWT tokenlar saqlaniadi — keyingi step uchun authenticated request kerak.

### 3.7 Environment (`frontend/.env.example`)

```
VITE_API_URL=http://localhost:8000/api
```

### 3.8 Frontend Dockerfile

```dockerfile
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

### 3.9 Frontend Nginx config (`frontend/nginx.conf`)

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;  # SPA fallback
    }

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3.10 Root docker-compose.yml ga frontend qo'shish

```yaml
  frontend:
    build: ./frontend
    restart: unless-stopped
    ports:
      - "5173:80"
    depends_on:
      - backend
```

---

## 4. BACKEND — Bot va Frontend uchun yangi endpoint'lar

### 4.1 Bot uchun endpoint'lar (`apps/users/views.py` ga qo'shish)

**GET `/api/users/by-telegram/<telegram_id>/`**
- Permission: `IsBotService` (X-Bot-Secret header)
- Returns: `UserDetailSerializer`

**POST `/api/users/link-telegram/`**
- Permission: `IsAuthenticated`
- Body: `{ "telegram_id": "123456789" }`
- CustomUser.telegram_id ni yangilaydi

**DELETE `/api/users/unlink-telegram/`**
- Permission: `IsAuthenticated`
- telegram_id ni null qiladi

### 4.2 Settings ga qo'shish

```python
# backend/config/settings.py
BOT_SECRET = env('BOT_SECRET', default='')
```

```
# backend/.env.example
BOT_SECRET=some-shared-secret-key
```

### 4.3 Telegram ID bilan bog'liq endpoint URL

```python
# apps/users/urls.py ga qo'shish
path('users/by-telegram/<str:telegram_id>/', UserByTelegramView.as_view(), name='user-by-telegram'),
path('users/link-telegram/', LinkTelegramView.as_view(), name='link-telegram'),
path('users/unlink-telegram/', UnlinkTelegramView.as_view(), name='unlink-telegram'),
```

---

## 5. PRODUCTION — Docker Compose to'liq arxitektura

```
Internet
    │
    ▼
[Host Nginx / SSL]          ← sites-available.conf (Let's Encrypt)
    │
    ├──► :8001 ──► [Docker Nginx]
    │                   │
    │          ┌─────────┴──────────┐
    │          ▼                    ▼
    │     [Backend:8000]      [Frontend:80]
    │          │
    │    ┌─────┴─────┐
    │    ▼           ▼
    │  [DB:5432]  [Redis:6379]
    │
    └──► [Bot] ──► HTTP ──► [Backend:8000]
```

---

## 6. XULOSA — Qilinishi kerak bo'lgan ishlar ro'yxati

### Kritik (ishlamaydi)
- [ ] `models.py` — `fileds` → `fields` typo tuzatish
- [ ] `entrypoint.sh` — migrate + collectstatic + server start
- [ ] `backend/requirements.txt` — `django-redis`, `gunicorn` qo'shish
- [ ] `bot/requirements.txt` — alohida requirements fayl yaratish
- [ ] `bot/app/routers.py` — `setup_routers()` yaratish
- [ ] Root `docker-compose.yml` — barcha servislar

### Bot
- [ ] `bot/app/api/client.py` — BackendClient
- [ ] `bot/app/middlewares/api_session.py` — aiohttp session middleware
- [ ] `bot/app/routers/start.py` — /start handler
- [ ] `bot/app/routers/admin.py` — admin buyruqlar
- [ ] `bot/app/filters/is_admin.py` — IsAdmin filter
- [ ] `bot/app/keyboards/admin_kb.py` — admin keyboards
- [ ] `bot/app/keyboards/user_kb.py` — user keyboards
- [ ] `bot/config.py` — `backend_url`, `bot_secret` qo'shish
- [ ] `bot/.env.example` — yangi o'zgaruvchilar

### Backend (bot uchun)
- [ ] `IsBotService` permission
- [ ] `GET /api/users/by-telegram/<telegram_id>/`
- [ ] `POST /api/users/link-telegram/`
- [ ] `DELETE /api/users/unlink-telegram/`
- [ ] `BOT_SECRET` settings va .env.example

### Frontend
- [ ] `frontend/` scaffold (Vue 3 + Vite + Pinia + Vue Router)
- [ ] `frontend/src/api/index.js` — axios + interceptors
- [ ] `frontend/src/stores/auth.js` — Pinia auth store
- [ ] `frontend/src/router/index.js` — routes + guards
- [ ] `LoginView.vue`
- [ ] `RegisterView.vue` (3-step wizard)
- [ ] `ForgotPasswordView.vue`
- [ ] `ProfileView.vue`
- [ ] `UserListView.vue` (admin)
- [ ] `UserDetailView.vue` (admin)
- [ ] `AppHeader.vue`
- [ ] `frontend/Dockerfile`
- [ ] `frontend/nginx.conf`
- [ ] `frontend/.env.example`
- [ ] Root `docker-compose.yml` ga frontend qo'shish

### Production
- [ ] Root `.env.example` — `BOT_SECRET` qo'shish
- [ ] `backend/nginx/default.conf` — `server_name` to'g'irlash

---

## 7. MUHOKAMA KERAK BO'LGAN SAVOLLAR

Quyidagilar bo'yicha qaror kerak:

1. **Bot o'z SQLite bazasini ishlatadimy?**  
   Faqat Telegram-specific ma'lumotlar (til, onboarding holati) uchun kerakmi, yoki hamma narsa backend orqali?

2. **Frontend framework components?**  
   Tailwind CSS ishlatamizmi? Yoki boshqa UI kutubxona (PrimeVue, Vuetify)?

3. **Telegram login frontend'da?**  
   Foydalanuvchi frontend'da Telegram orqali ham login qila oladimi? (Telegram Login Widget)

4. **Bot webhook yoki polling?**  
   Development uchun polling qulay. Production uchun webhook yaxshiroq. Qaysi biri?

5. **Bot orqali notification?**  
   Backend bot orqali userlarga xabar yuboradimi? Buning uchun qanday mexanizm (Redis queue, HTTP endpoint)?
