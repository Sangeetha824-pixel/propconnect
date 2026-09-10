# PropConnect – Smart Property Marketplace

PropConnect is a full-stack property marketplace designed for a clear buyer and seller experience. Buyers can discover homes, save favourites, submit interest requests, and receive recommendations. Sellers can publish listings, manage their portfolio, and respond to interested buyers.

The project is intentionally interview-friendly: the core marketplace workflow is small enough to understand quickly, while the API, authentication, database schema, and recommendation logic demonstrate practical full-stack engineering.

## Technology

- Frontend: React, React Router, Vite, Lucide icons
- Backend: Python FastAPI
- Database: MySQL in production, SQLite fallback for local demos
- ORM: SQLAlchemy
- Authentication: JWT bearer tokens
- Password security: bcrypt hashing through Passlib
- API style: REST/JSON

## Features

### Authentication and roles

- User registration and login
- JWT access tokens
- Secure password hashing
- Buyer and seller role selection
- Separate buyer and seller navigation/workspaces

### Buyer experience

- Browse active properties
- Search by location
- Filter by property type
- Filter by minimum and maximum budget through the API
- Sort by price
- Open full property details
- Save or remove favourites
- Submit an “I’m interested” request
- View request history
- See recommendation matches based on activity

### Seller experience

- Add a property listing
- Edit a listing
- Delete a listing
- View active listings
- Set listing status to Active or Inactive
- View buyer interest requests
- Track request status such as New, Contacted, Accepted, and Rejected

### Recommendation system

The recommendation endpoint scores active properties using signals from:

- Previous buyer searches
- Favourite property types
- Preferred location
- Preferred budget
- Preferred property type

The current implementation is deliberately simple and explainable, which makes it suitable for an interview demonstration. It can later be replaced with a weighted ranking model or a machine-learning service without changing the frontend contract.

## Screenshots

Product screenshots are included in the [`Screenshots/`](./Screenshots) folder and are documented in numeric order:

1. [Screenshot 1](./Screenshots/1.png)
2. [Screenshot 2](./Screenshots/2.png)
3. [Screenshot 3](./Screenshots/3.png)
4. [Screenshot 4](./Screenshots/4.png)
5. [Screenshot 5](./Screenshots/5.png)
6. [Screenshot 6](./Screenshots/6.png)
7. [Screenshot 7](./Screenshots/7.png)
8. [Screenshot 8](./Screenshots/8.png)
9. [Screenshot 9](./Screenshots/9.png)
10. [Screenshot 10](./Screenshots/10.png)
11. [Screenshot 11](./Screenshots/11.png)
12. [Screenshot 12](./Screenshots/12.png)
13. [Screenshot 13](./Screenshots/13.png)
14. [Screenshot 14](./Screenshots/14.png)

## Project structure

```text
propconnect/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── .env.example
│   ├── README.md
│   └── requirements.txt
├── src/
│   ├── main.jsx
│   └── styles.css
├── .gitignore
├── index.html
├── package.json
├── package-lock.json
└── vite.config.js
```

## Prerequisites

Install the following before starting:

- Node.js 18 or newer
- Python 3.11 or newer recommended
- MySQL 8 or newer for the full database setup
- Git, if cloning from GitHub

Python 3.13 is a good choice on Windows if a dependency does not yet provide wheels for the newest Python release.

## Frontend setup

From the project root:

```powershell
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

To create a production build:

```powershell
npm run build
```

The frontend uses `http://localhost:8000/api` as the default backend URL. To change it, create a root `.env` file:

```env
VITE_API_URL=http://localhost:8000/api
```

The root `.env` file is ignored by Git.

## Backend setup

Open a second PowerShell window and enter the backend folder:

```powershell
cd "C:\Users\ELCOT\OneDrive\Documents\ChatGPT\Mini Marketplace\backend"
```

Install dependencies:

```powershell
py -m pip install --upgrade -r requirements.txt
```

Start FastAPI:

```powershell
py -m uvicorn app.main:app --reload --port 8000
```

The API is available at:

- Health check: `http://127.0.0.1:8000/`
- Swagger documentation: `http://127.0.0.1:8000/docs`
- ReDoc documentation: `http://127.0.0.1:8000/redoc`

## Environment configuration

Copy the example file:

```powershell
Copy-Item .env.example .env
```

Example backend `.env`:

```env
DATABASE_URL=mysql+pymysql://propconnect:password@localhost:3306/propconnect
JWT_SECRET=replace-this-with-a-long-random-secret
FRONTEND_ORIGIN=http://localhost:5173
```

The real `.env` file must stay local. Only `.env.example` should be committed to GitHub.

## MySQL setup

Create the database before starting the API:

```sql
CREATE DATABASE propconnect CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'propconnect'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON propconnect.* TO 'propconnect'@'localhost';
FLUSH PRIVILEGES;
```

Set the matching `DATABASE_URL` in `backend/.env`:

```env
DATABASE_URL=mysql+pymysql://propconnect:password@localhost:3306/propconnect
```

For a zero-setup demonstration, leave `DATABASE_URL` unset. The backend defaults to a local SQLite file named `propconnect.db`. The same SQLAlchemy models and table structure are used.

## Database tables

### Users

Stores account identity, role, hashed password, and optional preference fields.

### Properties

Stores seller-owned property listings including title, description, location, type, room count, price, images, status, and creation date.

### Favourites

Connects buyers to properties they have saved.

### Interests

Connects buyers to properties they are interested in and stores the seller workflow status.

### SearchHistory

Stores buyer search terms, property type, budget range, and timestamp for recommendations.

## REST API

All protected endpoints use:

```http
Authorization: Bearer <jwt-token>
```

### Authentication

```http
POST /api/auth/register
POST /api/auth/login
```

Registration body:

```json
{
  "name": "Aarav Mehta",
  "email": "buyer@propconnect.demo",
  "password": "Demo@123",
  "role": "buyer"
}
```

Valid roles are `buyer` and `seller`.

### Properties

```http
GET    /api/properties
GET    /api/properties/{id}
POST   /api/properties
PUT    /api/properties/{id}
DELETE /api/properties/{id}
```

Supported `GET /api/properties` query parameters:

```text
location
min_budget
max_budget
property_type
sort=asc|desc
```

Create/update body:

```json
{
  "title": "The Willow House",
  "description": "A light-filled family home.",
  "location": "Indiranagar, Bengaluru",
  "property_type": "Villa",
  "rooms": 4,
  "price": 28500000,
  "images": ["https://example.com/home.jpg"],
  "active": true
}
```

### Buyer actions

```http
POST /api/properties/{id}/interest
POST /api/properties/{id}/favorite
GET  /api/recommendations
```

Calling the favourite endpoint toggles the saved state. Calling the interest endpoint creates an interest record if one does not already exist.

### Seller actions

```http
GET /api/seller/interests
```

The response includes the interested buyer, property title, current status, and request date.

## Demo accounts

The frontend can open demo mode with any valid email and password when the API is unavailable. For a real backend flow, register these accounts once through the Register page:

```text
Buyer
Email: buyer@propconnect.demo
Password: Demo@123

Seller
Email: seller@propconnect.demo
Password: Demo@123
```

These accounts are not pre-seeded automatically. This keeps the repository free of default production credentials.

## Typical development workflow

Use two terminals.

Terminal 1, frontend:

```powershell
cd "C:\Users\ELCOT\OneDrive\Documents\ChatGPT\Mini Marketplace"
npm run dev
```

Terminal 2, backend:

```powershell
cd "C:\Users\ELCOT\OneDrive\Documents\ChatGPT\Mini Marketplace\backend"
py -m uvicorn app.main:app --reload --port 8000
```

Then open `http://localhost:5173`.

## GitHub publishing

From the project root:

```powershell
git add .
git commit -m "Build PropConnect smart property marketplace"
git branch -M main
git remote set-url origin https://github.com/Sangeetha824-pixel/propconnect.git
git push -u origin main
```

Do not commit `.env`, database files, `node_modules`, or `dist`. These are already excluded in `.gitignore`.

## Troubleshooting

### `cd backend` cannot find the folder

PowerShell may be starting in `C:\Windows\System32`. Use the full project path:

```powershell
cd "C:\Users\ELCOT\OneDrive\Documents\ChatGPT\Mini Marketplace\backend"
```

### `pip` or `uvicorn` is not recognized

Use the Python launcher form:

```powershell
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload --port 8000
```

### Pydantic tries to compile Rust code

Use Python 3.13 or newer FastAPI/Pydantic dependencies from the current `requirements.txt`. Python 3.13 is recommended if Python 3.14 does not have a compatible wheel for your machine yet.

### Backend returns 404 for `/`

The root endpoint is a health check. API routes are under `/api`, and interactive documentation is available at `/docs`.

### Frontend still shows demo data

Confirm that the FastAPI server is running on port 8000 and that the frontend is using:

```env
VITE_API_URL=http://localhost:8000/api
```

Restart Vite after changing environment variables.

## Future improvements

- Add a file upload service for property images
- Add pagination and server-side property cards
- Add seller notification delivery through email or WebSockets
- Add explicit interest status update endpoint
- Add database migrations with Alembic
- Add automated backend and frontend tests
- Add refresh tokens and account recovery
- Replace the explainable recommendation score with a richer ranking model
