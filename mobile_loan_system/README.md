# Mobile Purchase & Loan (EMI) Management System

A Django + Django REST Framework project for a mobile phone shop that:
- Purchases mobile phones into stock (with IMEI tracking, supplier, cost/selling price)
- Manages customers (KYC info, blacklist flag)
- Gives phones to customers **on loan (EMI)** instead of a straight cash sale
- Auto-generates the EMI schedule (reducing-balance interest formula)
- Lets staff record EMI payments and auto-closes a loan once fully paid

Includes a working server-rendered frontend (HTML + vanilla JS calling the DRF API)
so the whole thing runs out of the box with no separate frontend build step.

---

## 1. Project Structure

```
mobile_loan_system/
├── manage.py
├── requirements.txt
├── config/              # Project settings, root urls, wsgi/asgi
├── customers/           # Customer model + API (KYC, blacklist)
├── inventory/           # Supplier + MobilePhone models + API (stock/purchasing)
├── loans/                # Loan + EMIPayment models + API (the core EMI logic)
│   └── utils.py          # EMI calculation & schedule builder (pure functions)
├── frontend/             # Server-rendered UI that consumes the DRF API
│   ├── templates/frontend/
│   └── static/frontend/{css,js}
└── templates/base.html   # shared layout (nav, CSRF helper)
```

## 2. Setup

```bash
cd mobile_loan_system
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser   # create your staff login

python manage.py runserver
```

Visit:
- **Frontend app:** http://127.0.0.1:8000/ (log in with the superuser you created)
- **Django admin:** http://127.0.0.1:8000/admin/
- **Browsable API:** http://127.0.0.1:8000/api/customers/ , `/api/inventory/phones/`, `/api/loans/`

## 3. Core Business Flow

1. **Purchase a phone into stock** — `Inventory` page → fills `MobilePhone` with IMEI,
   cost price, selling price. Status starts as `AVAILABLE`.
2. **Add a customer** — `Customers` page → captures KYC (ID proof) info.
3. **Give a phone on loan** — `Loans` page → pick customer + an available phone,
   set down payment, annual interest rate, and tenure (months).
   - The system calculates `loan_amount = total_amount - down_payment`
   - Computes `monthly_emi` using the standard reducing-balance formula
   - Auto-generates the full month-by-month `EMIPayment` schedule
   - Flips the phone's `stock_status` to `ON_LOAN`
4. **Record payments** — open a loan's detail page and record a payment.
   It's applied to the earliest pending installment. Once every installment
   is `PAID`, the loan auto-closes (`status=CLOSED`) and the phone's status
   becomes `SOLD`.

## 4. Key API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/api/customers/` | List / create customers |
| GET/PATCH | `/api/customers/{id}/` | View / update (e.g. blacklist) a customer |
| GET/POST | `/api/inventory/phones/` | List / purchase phones into stock |
| GET/POST | `/api/inventory/suppliers/` | List / create suppliers |
| GET/POST | `/api/loans/` | List / create loans |
| GET | `/api/loans/{id}/schedule/` | Full loan + EMI schedule |
| POST | `/api/loans/{id}/pay-installment/` | Record a payment `{"amount": "1500.00"}` |
| GET | `/api/loans/installments/` | Global read-only list of all installments (for due/overdue reports) |

All API endpoints require authentication (session login via the frontend, or
Django admin session, or HTTP Basic Auth for scripting/Postman).

## 5. Notable Design Decisions

- **One phone → one loan** (`OneToOneField`): once a specific IMEI is loaned
  out it can't be loaned to two people.
- **EMI math lives in `loans/utils.py`** as pure functions, kept separate
  from the model so it's easy to unit test independently.
- **SQLite by default** for zero-config local running; swap `DATABASES` in
  `config/settings.py` for Postgres/MySQL in production.
- **Frontend has no build step** — plain HTML/CSS/JS served by Django's
  static files, calling the DRF API with `fetch()` + session/CSRF auth.
  This keeps the whole project runnable with a single `runserver` command.

## 6. Extending for Production

- Swap `SECRET_KEY` and set `DEBUG = False`, configure `ALLOWED_HOSTS`
- Move to Postgres, add `django-environ` for env-based config
- Add a Celery task to auto-flag overdue installments (`due_date < today`)
- Add role-based permissions (e.g. only managers can blacklist customers)
- Add a receipt/PDF generator for each EMI payment
