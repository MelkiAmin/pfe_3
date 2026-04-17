# 🎟️ HotelMate — Système de Réservation de Billets d'Événements

**Version:** 2.0 | **Auteur:** MEHDI SELLAMI — SOTETEL | **Date:** 2026

**Stack:** Django 4.2 + DRF · Vue 3 + Vuetify · PostgreSQL · Redis · Celery · Stripe

---

## 📋 Table des Matières

1. [Architecture](#architecture)
2. [Fonctionnalités complètes](#fonctionnalités)
3. [Installation Docker (recommandée)](#docker)
4. [Installation manuelle](#manuelle)
5. [Variables d'environnement](#envvars)
6. [Documentation API](#api)
7. [Tests](#tests)
8. [Déploiement production](#production)

---

## 🏗️ Architecture <a name="architecture"></a>

```
hotelmate/
├── backend/                     Django 4.2 + DRF
│   ├── apps/
│   │   ├── accounts/            Auth JWT, 2FA TOTP, vérif. email, reset MDP
│   │   ├── events/              CRUD événements, catégories, favoris, avis, workflow statut
│   │   ├── tickets/             Types billets, achat, QR codes, check-in
│   │   ├── payments/            Stripe, wallet, transactions, retraits, remboursements
│   │   ├── organizer/           Profil organisateur, dashboard complet
│   │   ├── notifications/       In-app, email SendGrid, SMS Twilio, rappels Celery
│   │   ├── admin_panel/         Dashboard admin, modération, analytics, rapports CSV
│   │   ├── kyc/                 Vérification KYC documents
│   │   ├── support/             Tickets support + messagerie
│   │   └── core/                Health check, newsletter
│   ├── templates/emails/        Templates HTML emails
│   ├── utils/                   Helpers, permissions
│   ├── planova/                 Settings, URLs, Celery
│   ├── tests/                   Suite de tests complète
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/                    Vue 3 + Vuetify + TypeScript
│   └── src/
│       ├── pages/               Routing file-based
│       ├── stores/              Pinia (auth, cart, catalog)
│       └── services/            Clients API axios
├── docker-compose.yml           Stack complète
└── .env.example
```

---

## ✅ Fonctionnalités complètes <a name="fonctionnalités"></a>

### Authentification & Sécurité
| Feature | Status |
|---|---|
| Inscription / Connexion JWT (access + refresh) | ✅ |
| Blacklist tokens + rotation automatique | ✅ |
| Authentification 2FA TOTP (Google Authenticator) | ✅ |
| Vérification email par OTP 6 chiffres | ✅ |
| Réinitialisation mot de passe par email | ✅ |
| CORS sécurisé (conditionnel au DEBUG) | ✅ |
| Rate limiting (100/h anonyme, 1000/h authentifié) | ✅ |
| HSTS, XSS, CSRF, Clickjacking protection | ✅ |

### Événements
| Feature | Status |
|---|---|
| CRUD complet événements (organisateurs) | ✅ |
| Filtrage avancé (catégorie, ville, type, gratuit) | ✅ |
| Recherche full-text | ✅ |
| Workflow statut : draft → published → completed / cancelled | ✅ |
| Notification automatique aux participants sur annulation | ✅ |
| Système de favoris | ✅ |
| Avis et notes (1–5 étoiles) | ✅ |
| Liste "mes événements" organisateur | ✅ |

### Billetterie
| Feature | Status |
|---|---|
| Types de billets (prix, quantité, disponibilité) | ✅ |
| Achat via Stripe Checkout (Redirect) | ✅ |
| Webhook Stripe (checkout.session.completed) | ✅ |
| QR codes générés automatiquement après paiement | ✅ |
| Check-in des billets par QR code | ✅ |
| Annulation et remboursement billets | ✅ |

### Paiements & Wallet
| Feature | Status |
|---|---|
| Stripe Checkout + Webhook + confirmation | ✅ |
| Wallet organisateur (crédité automatiquement) | ✅ |
| Historique transactions | ✅ |
| Demandes de retrait avec workflow admin | ✅ |
| Remboursements | ✅ |
| Commission plateforme configurable (défaut 90% vers organisateur) | ✅ |

### Notifications
| Feature | Status |
|---|---|
| Notifications in-app (lu/non-lu, compteur) | ✅ |
| Emails transactionnels HTML (SendGrid) | ✅ |
| Confirmation de commande par email | ✅ |
| Rappels automatiques 24h avant événement (Celery Beat) | ✅ |
| Notification annulation événement | ✅ |
| SMS via Twilio (opt-in, tâches Celery) | ✅ |

### Dashboards
| Feature | Status |
|---|---|
| Dashboard organisateur (revenus, fill rate, top 5, charts) | ✅ |
| Dashboard admin (métriques globales) | ✅ |
| Analytics par événement (timeline, par type de billet) | ✅ |
| Statistiques système étendues | ✅ |
| Export CSV rapport revenus | ✅ |

### Administration
| Feature | Status |
|---|---|
| Gestion utilisateurs (liste, recherche, suppression) | ✅ |
| Modération événements (approve/reject avec notification) | ✅ |
| Gestion et approbation des retraits | ✅ |
| Visualisation toutes les transactions | ✅ |

### KYC & Vérification
| Feature | Status |
|---|---|
| Soumission documents KYC | ✅ |
| Statut KYC (pending/approved/rejected) | ✅ |
| Workflow admin approve/reject avec raison | ✅ |

### Support
| Feature | Status |
|---|---|
| Création tickets support | ✅ |
| Messagerie ticket (user ↔ admin) | ✅ |
| Priorités (low/medium/high/urgent) | ✅ |
| Workflow statut (open/in_review/resolved/closed) | ✅ |

### DevOps
| Feature | Status |
|---|---|
| Docker Compose complet (db + redis + backend + celery + frontend) | ✅ |
| Dockerfile backend multi-stage sécurisé | ✅ |
| Variables d'environnement externalisées | ✅ |
| Celery + Celery Beat pour tâches asynchrones | ✅ |
| Swagger UI + ReDoc disponibles | ✅ |

---

## 🚀 Installation Docker <a name="docker"></a>

```bash
git clone https://github.com/MelkiAmin/pfe-2.git
cd pfe-2

# Configuration
cp .env.example .env
# Éditer .env : STRIPE_SECRET_KEY, SENDGRID_API_KEY, SECRET_KEY

# Lancer toute la stack
docker-compose up -d

# Créer le superadmin
docker-compose exec backend python manage.py createsuperuser
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000/api/ |
| Swagger UI | http://localhost:8000/api/docs/ |
| ReDoc | http://localhost:8000/api/redoc/ |
| Django Admin | http://localhost:8000/admin/ |

---

## 🛠️ Installation manuelle <a name="manuelle"></a>

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # éditer
python manage.py migrate
python manage.py runserver

# Dans un autre terminal
celery -A planova worker --loglevel=info
celery -A planova beat --loglevel=info
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local  # éditer VITE_API_BASE_URL
npm run dev
```

---

## 🔑 Variables d'environnement <a name="envvars"></a>

| Variable | Description | Défaut |
|---|---|---|
| `SECRET_KEY` | Clé secrète Django | — (obligatoire) |
| `DEBUG` | Mode debug | `True` |
| `DB_PASSWORD` | Mot de passe PostgreSQL | `hotelmate_secret` |
| `STRIPE_SECRET_KEY` | Clé secrète Stripe | — |
| `STRIPE_WEBHOOK_SECRET` | Secret webhook Stripe | — |
| `STRIPE_CURRENCY` | Devise | `eur` |
| `SENDGRID_API_KEY` | Clé API SendGrid | — |
| `TWILIO_ACCOUNT_SID` | SID Twilio (SMS optionnel) | — |
| `TWILIO_AUTH_TOKEN` | Token Twilio | — |
| `TWILIO_FROM_NUMBER` | Numéro expéditeur Twilio | — |
| `REDIS_URL` | URL Redis | `redis://localhost:6379/0` |
| `PLATFORM_COMMISSION` | Part organisateur (0.0–1.0) | `0.90` |
| `FRONTEND_URL` | URL frontend pour CORS | `http://localhost:3000` |

---

## 📖 Documentation API <a name="api"></a>

**Swagger UI :** `/api/docs/` — **ReDoc :** `/api/redoc/`

### Endpoints principaux

```
# Auth
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/logout/
GET    /api/auth/profile/
POST   /api/auth/change-password/
POST   /api/auth/email/request-verification/
POST   /api/auth/email/confirm-verification/
POST   /api/auth/password-reset/
POST   /api/auth/password-reset/confirm/
POST   /api/auth/2fa/setup/
POST   /api/auth/2fa/verify/
POST   /api/auth/2fa/disable/

# Events
GET    /api/events/
POST   /api/events/
GET    /api/events/{id}/
POST   /api/events/{id}/status/     ← publish/cancel/complete
GET    /api/events/my-events/
GET    /api/events/categories/
GET    /api/events/favorites/
GET    /api/events/reviews/

# Tickets
GET    /api/tickets/
GET    /api/tickets/types/
POST   /api/tickets/{id}/check_in/

# Payments
POST   /api/payments/checkout/
POST   /api/payments/confirm/
POST   /api/payments/webhook/stripe/
GET    /api/payments/wallet/
GET    /api/payments/transactions/
POST   /api/payments/withdrawals/
POST   /api/payments/refund/
GET    /api/payments/history/

# Organizer
GET    /api/organizer/dashboard/
GET    /api/organizer/profile/

# Notifications
GET    /api/notifications/
POST   /api/notifications/mark_all_read/
GET    /api/notifications/unread_count/

# KYC
POST   /api/kyc/submit/
GET    /api/kyc/status/

# Support
GET    /api/support/tickets/
POST   /api/support/tickets/
POST   /api/support/tickets/{id}/message/

# Admin
GET    /api/admin-panel/dashboard/
GET    /api/admin-panel/stats/
GET    /api/admin-panel/reports/revenue/
GET    /api/admin-panel/users/
GET    /api/admin-panel/events/
POST   /api/admin-panel/events/{id}/moderate/
GET    /api/admin-panel/events/{id}/analytics/data/
GET    /api/admin-panel/withdrawals/
POST   /api/admin-panel/withdrawals/{id}/action/
GET    /api/kyc/admin/
POST   /api/kyc/admin/{id}/action/
GET    /api/support/admin/tickets/
POST   /api/support/admin/tickets/{id}/reply/
```

---

## 🧪 Tests <a name="tests"></a>

```bash
cd backend
pip install pytest pytest-django
pytest tests/ -v

# Par module
pytest tests/test_auth_api.py -v
pytest tests/test_payments_api.py -v
pytest tests/test_events_api.py -v
pytest tests/test_tickets_api.py -v
pytest tests/test_wallet_api.py -v
pytest tests/test_kyc_api.py -v
pytest tests/test_support_api.py -v
pytest tests/test_notifications_api.py -v
pytest tests/test_admin_panel.py -v
pytest tests/test_email_verify.py -v
pytest tests/test_organizer_dashboard.py -v
```

**Couverture :** Auth · Paiements Stripe · Tickets · Wallet · Retraits · KYC · Support · Notifications · Admin · Dashboard organisateur · Vérification email · Reset mot de passe

---

## 🌐 Rôles utilisateurs

| Rôle | Accès |
|---|---|
| `attendee` | Parcourir, acheter billets, gérer profil, KYC, support |
| `organizer` | Tout attendee + créer/gérer événements, voir revenus wallet, demander retraits |
| `admin` | Accès complet, modération, approbation retraits/KYC, rapports |

---

## 🔐 Sécurité

- JWT avec rotation des refresh tokens et blacklist
- 2FA TOTP (compatible Google Authenticator, Authy)
- CORS conditionnel au mode DEBUG
- Rate limiting par rôle
- HSTS en production
- Headers sécurité : XSS, CSRF, Clickjacking, Content-Type
- Transactions atomiques sur les opérations critiques (paiements, check-in)
- `select_for_update()` sur les ressources concurrentes (billets, wallet)
