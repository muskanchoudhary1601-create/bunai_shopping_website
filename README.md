# Bunai - Authentic Handmade Crafts & Weaves 🧵✨

> **Full-Featured E-Commerce Shopping Web Application for Handmade Goods (Python, Django, SQLite, Bootstrap 5.3)**

![Bunai Artisanal Shopping](https://img.shields.io/badge/Storefront-Django%20%7C%20SQLite%20%7C%20Bootstrap%205.3-c25e38)
![Tests](https://img.shields.io/badge/Tests-6%20Passed-16a34a)
![Python](https://img.shields.io/badge/Python-3.14-blue)

---

## 🌟 Customer Shopping Experience & Features

### 1. 🛍️ Storefront Home Page (`/`)
- **Artisan Hero Banner**: Story-driven introduction to heritage Indian craftsmanship.
- **Shop by Craft Technique**: Visual collection tiles (Handloom Sarees, Macrame Decor, Studio Ceramics, Woodcraft, Needlecraft, Knitwear).
- **Artisan Bestsellers & Featured Drops**: Handpicked crafts with discount tags (`25% OFF`), star ratings, pricing in ₹, and instant "Add to Cart" triggers.
- **Trust Badges & Promises**: 100% Handcrafted Guarantee, Direct Artisan Fair Wages, Free Express Shipping over ₹1,999, and Zero-Plastic Packaging.
- **Customer Reviews**: Testimonials and ratings from verified buyers.

### 2. 🧶 Product Catalog & Search (`/shop/`)
- **Faceted Filters**: Filter by craft category, keyword search, price range (Min/Max ₹), and in-stock only toggle.
- **Sorting Options**: Featured & Bestsellers, Price: Low to High, Price: High to Low, Highest Rated, and New Arrivals.
- **Responsive Craft Cards**: Stock availability alerts, discount calculations, and category badges.

### 3. 🔍 Craft Showcase & Details (`/shop/<slug>/`)
- **Rich Artisan Specifications**: Origin & Craft Guild, Technique, Materials, Dimensions, and Care Instructions.
- **Pricing & Savings**: Displays selling price vs. original MRP with instant savings calculation.
- **Stock Indicators**: Real-time availability (`In Stock`, `Only 2 left!`, or `Out of Stock`).
- **Interactive Reviews**: Verified customer reviews and an embedded "Write a Review" submission form.
- **Curated Recommendations**: "You May Also Cherish" related craft suggestions.

### 4. 🛒 Session-Backed Shopping Cart (`/cart/`)
- **Dynamic Cart Engine**: Seamlessly add items, adjust quantities with instant calculation, or remove items.
- **Free Shipping Progress Bar**: Visual indicator showing how much to add to unlock Free All-India Express Delivery.
- **Promo Coupon System**: Apply promo codes (e.g. `BUNAI10` for 10% off, `CRAFT200` for ₹200 off).
- **Persistent Navbar Cart Badge**: Displays live item counts across all pages.

### 5. 💳 Streamlined 2-Step Checkout (`/checkout/`)
- **Delivery Address**: Simple customer contact and shipping destination entry.
- **Payment Options**: Radio cards for UPI / Instant QR Code (Google Pay, PhonePe, Paytm), Cash on Delivery (COD), Credit/Debit Cards, and Net Banking.
- **Atomic Stock Ledger (`transaction.atomic`)**: Automatically creates Order and OrderItems while safely decrementing inventory stock.

### 6. 📦 Order Confirmation & Live Tracking (`/track-order/`)
- **Order Success Receipt**: Itemized purchase summary with delivery address, coupon discount, and tracking ID.
- **Live Order Tracker**: Visual 4-step progress stepper (`Order Placed` &rarr; `In Crafting / Packing` &rarr; `Dispatched / In Transit` &rarr; `Delivered`).

### 7. 📖 Brand Story & Philosophy (`/our-story/`)
- Celebrates master weavers and artisans, ethical fair-trade sourcing, and sustainability.

---

## 🚀 Quickstart & Local Setup

### 1. Activate Environment
```bash
# In Windows PowerShell:
.\venv\Scripts\activate
```

### 2. Run Database Migrations
```bash
python manage.py migrate
```

### 3. Populate Artisan Seed Catalog
Populate sample handloom sarees, macrame decor, studio ceramics, customer reviews, and demo trackable orders:
```bash
python manage.py seed_data
```

### 4. Run Automated Test Suite
```bash
python manage.py test
```

### 5. Start Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```

- **Shopping Storefront**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Store Catalog**: [http://127.0.0.1:8000/shop/](http://127.0.0.1:8000/shop/)
- **Track Order**: [http://127.0.0.1:8000/track-order/](http://127.0.0.1:8000/track-order/)
- **Staff Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) (`admin` / `admin123`)
