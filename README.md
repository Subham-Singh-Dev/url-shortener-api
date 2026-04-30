**# SwiftURL — URL Shortener API**



**A production-grade URL shortening service built with Django REST Framework.**



**\*\*Live Demo:\*\* https://url-shortener-api.onrender.com**



**## Tech Stack**

**Django · DRF · PostgreSQL · Whitenoise · Railway/Render · pytest**



**## API Endpoints**

**| Method | Endpoint | Description |**

**|---|---|---|**

**| POST | /api/shorten/ | Shorten a URL |**

**| GET | /api/urls/ | List recent URLs |**

**| GET | /{short\_code}/ | Redirect to original |**

**| GET | /api/stats/{code}/ | Click analytics |**



**## Run Locally**

**```bash**

**git clone https://github.com/Subham-Singh-Dev/url-shortener-api**

**cd url-shortener-api**

**python -m venv venv \&\& venv\\Scripts\\activate**

**pip install -r requirements.txt**

**python manage.py migrate**

**python manage.py runserver**

**```**



**## Test Coverage**

**```bash**

**pytest shortener/test\_api.py -v**

**```**

**10 tests — shorten, redirect, click tracking, analytics, edge cases.**

