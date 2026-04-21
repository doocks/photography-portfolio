# 3D Photography Portfolio

A stunning 3D photography portfolio website built with Django and Three.js.

## Features

- 🎨 Immersive 3D gallery with floating photo frames
- 📷 3D camera model in scene
- 🖼️ Lightbox image viewer
- 📱 Fully responsive design
- 🗂️ Category filtering
- ✨ Glassmorphism UI effects
- ⚡ Fast loading with lazy loading

## Installation

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Windows: `venv\Scripts\activate`)
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Seed database: `python manage.py seed_gallery`
7. Run server: `python manage.py runserver`

## Admin Access

- URL: `/admin`
- Create superuser: `python manage.py createsuperuser`

## Technologies

- Django 4.2
- Three.js
- SQLite
- Bootstrap 5
- Font Awesome 6