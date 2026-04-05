<div align="center">

# 📚 BOOKVERSE
### *Your Universe of Books*

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Razorpay](https://img.shields.io/badge/Razorpay-02042B?style=for-the-badge&logo=razorpay&logoColor=3395FF)
![Google Books](https://img.shields.io/badge/Google%20Books%20API-4285F4?style=for-the-badge&logo=google&logoColor=white)

A **premium, dark-themed editorial book store** built with Django. Browse thousands of books across every genre, manage your wishlist, and check out seamlessly with Razorpay.

</div>

---

## ✨ Features

- 🏠 **Dynamic Homepage** — 3D book carousel (trending), category slider with real covers, animated hero
- 🔍 **Smart Search** — Searches local DB + live Google Books API fallback
- 🗂️ **Category Browsing** — All major genres with sortable, paginated book grids
- 🛒 **Cart System** — AJAX-powered slide-out cart drawer with live count badge
- ❤️ **Wishlist** — Save books to a personal wishlist with one click (AJAX toggle)
- 💳 **Razorpay Payments** — Secure checkout with HMAC signature verification
- 👤 **User Accounts** — Register, login, profile settings, custom avatar upload
- 📱 **Fully Responsive** — Mobile-first design with hamburger nav for all screen sizes
- 🎨 **Editorial Design** — Dark mode, glassmorphism, custom animations, Google Fonts

---

## 🖼️ Screenshots

| Homepage | Book Detail | Wishlist |
|---|---|---|
| Dark hero + 3D carousel | Cover, details, wishlist toggle | Saved books grid |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- pip

### 1. Clone the repository

```bash
git clone https://github.com/MuhammadRoshan-S/Bookverse.git
cd Bookverse
```

### 2. Create & activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key-here

# Google Books API
GOOGLE_BOOKS_API_KEY=your-google-books-api-key

# Razorpay (use test keys for development)
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your-razorpay-secret
```

> ⚠️ **Never commit your `.env` file.** It's already in `.gitignore`.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Seed the database with books

```bash
python manage.py seed_books
```

### 7. Create a superuser (admin)

```bash
python manage.py createsuperuser
```

### 8. Run the development server

```bash
python manage.py runserver
```

Visit → **http://127.0.0.1:8000/**

---

## 🗂️ Project Structure

```
Bookverse/
├── bookverse/              # Django project config
│   ├── settings.py
│   └── urls.py
├── store/                  # Main app (books, cart, orders, wishlist)
│   ├── models.py           # Book, Category, Cart, Order, Wishlist
│   ├── views.py            # All views (home, detail, cart, wishlist, checkout)
│   ├── urls.py
│   ├── google_books.py     # Google Books API integration
│   └── context_processors.py
├── accounts/               # Auth app (register, login, profile)
│   ├── models.py           # UserProfile (avatar, bio)
│   └── views.py
├── templates/
│   ├── base.html           # Base layout (nav, cart drawer, footer)
│   └── store/              # Page templates
├── static/
│   ├── css/style.css       # All styles (dark theme + responsive)
│   ├── js/app.js           # JS (carousel, cart AJAX, wishlist toggle)
│   └── images/
├── media/                  # User uploaded avatars (gitignored)
├── .env                    # Secrets (gitignored)
├── .gitignore
├── requirements.txt
└── manage.py
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Django 5.x (Python) |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Frontend** | Vanilla HTML, CSS, JavaScript |
| **Fonts** | Syne, Space Grotesk, Space Mono (Google Fonts) |
| **Payments** | Razorpay |
| **Books Data** | Google Books API |
| **Auth** | Django built-in auth + custom UserProfile |

---

## 🔑 Key URLs

| URL | Description |
|---|---|
| `/` | Homepage (hero, trending, categories, featured) |
| `/books/` | All books (paginated) |
| `/category/<slug>/` | Browse by genre |
| `/book/<slug>/` | Book detail page |
| `/search/?q=` | Search books |
| `/wishlist/` | My wishlist |
| `/cart/` | Cart page |
| `/checkout/` | Checkout + Razorpay payment |
| `/accounts/register/` | Sign up |
| `/accounts/login/` | Sign in |
| `/accounts/profile/` | Profile settings / avatar |
| `/admin/` | Django admin panel |

---

## 💳 Payment Testing

Use Razorpay **test credentials** and the following test card:

| Field | Value |
|---|---|
| Card Number | `4111 1111 1111 1111` |
| Expiry | Any future date |
| CVV | Any 3 digits |
| OTP | `1234` |

---

## 🌐 Deployment Notes

For production:
1. Set `DEBUG = False` in `settings.py`
2. Use **gunicorn** + **nginx** or deploy to **Railway / Render / Heroku**
3. Serve static files with **WhiteNoise** or **AWS S3**
4. Switch to **PostgreSQL** as the database
5. Replace Razorpay test keys with **live keys**
6. Set a strong `SECRET_KEY`

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

1. Fork the repo
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**.

---

<div align="center">

Built with ❤️ by [MuhammadRoshan-S](https://github.com/MuhammadRoshan-S)

</div>
