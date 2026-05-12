# GETTING STARTED GUIDE

## 5-Minute Quick Start

### Using Docker (Recommended)

```bash
# 1. Clone repository
git clone <repo-url>
cd "QUANT TRACK"

# 2. Copy env file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Wait 30 seconds for services to initialize

# 5. Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000/api/docs
```

### Manual Setup (Development)

**Prerequisites**: Python 3.11, Node.js 18, PostgreSQL, Redis

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

---

## 📱 First Steps After Installation

### 1. Create Account

Go to `http://localhost:3000/register`:
- Email: `trader@example.com`
- Name: `Test Trader`
- Password: `SecurePassword123!`

### 2. Create Your First Trade

Go to Dashboard → Add Trade:
- Symbol: `AAPL`
- Direction: `LONG`
- Entry Price: `150.00`
- Exit Price: `152.50`
- Lot Size: `100`
- Strategy: `Breakout`

### 3. View Analytics

Go to Analytics page to see:
- Win/Loss statistics
- P&L breakdown
- Performance charts

---

## 🔧 Environment Configuration

Edit `.env` file:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/quanttrack_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Secret (change in production!)
SECRET_KEY=your-super-secret-key-min-32-chars

# Debug mode (set to False in production)
DEBUG=True
ENVIRONMENT=development

# Frontend API URL
REACT_APP_API_URL=http://localhost:8000/api
```

---

## 📚 Project Structure Quick Ref

```
Backend:
- app/auth/        → Login, JWT tokens
- app/trades/      → Trade CRUD operations
- app/analytics/   → Metrics calculations
- app/ml/          → Predictive models
- app/nlp/         → Behavioral analysis

Frontend:
- src/pages/       → Page components
- src/services/    → API calls
- src/store/       → Redux state management
- src/components/  → Reusable components
```

---

## 🚀 Next: Building Features

### Development Workflow

1. **Create a new feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Backend Development**
   - Create service in `app/module/service.py`
   - Create schemas in `app/module/schemas.py`
   - Create routes in `app/module/router.py`
   - Add to `app/main.py`

3. **Frontend Development**
   - Create component in `src/components/`
   - Add API calls in `src/services/api.js`
   - Update Redux state if needed
   - Create page in `src/pages/`

4. **Test Locally**
   ```bash
   # Backend
   pytest tests/
   
   # Frontend
   npm test
   ```

5. **Deploy**
   ```bash
   docker-compose up -d
   ```

---

## 🐛 Troubleshooting

### Docker Issues

```bash
# View logs
docker-compose logs backend

# Restart services
docker-compose restart

# Complete reset
docker-compose down -v
docker-compose up -d
```

### Database Issues

```bash
# Connect to database
psql postgresql://quanttrack_user:password@localhost:5432/quanttrack_db

# Check migrations
alembic current
alembic history
```

### Frontend Issues

```bash
# Clear npm cache
npm cache clean --force

# Reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## 📖 Learn More

- [Architecture Documentation](ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [ML Pipeline](docs/ML_PIPELINE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

---

## 💡 Tips & Tricks

### Fast API Development
- Use `--reload` flag in `uvicorn` for auto-restart
- Use `swagger-ui` at `/api/docs` for testing endpoints
- Use `breakpoint()` in Python for debugging

### Fast Frontend Development
- Use Redux DevTools extension
- Use React DevTools extension
- Use Tailwind CSS IntelliSense extension

### Database Management
- Use `pgAdmin` for visual database management
- Keep migrations organized with timestamps
- Test migrations before production

---

## 🎯 Common Tasks

### Add New API Endpoint

1. Create schema in `schemas.py`:
```python
class MyCreateSchema(BaseModel):
    field: str

class MyResponse(BaseModel):
    id: int
    field: str
```

2. Create service method in `service.py`:
```python
class MyService:
    @staticmethod
    def create(data: MyCreateSchema, user_id: int, db: Session):
        obj = MyModel(...)
        db.add(obj)
        db.commit()
        return obj
```

3. Create route in `router.py`:
```python
@router.post("/my-endpoint", response_model=MyResponse)
def my_endpoint(data: MyCreateSchema, db: Session = Depends(get_db)):
    return MyService.create(data, user_id, db)
```

4. Add router to `main.py`:
```python
app.include_router(my_router)
```

---

## 🔐 Security Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Use strong database password
- [ ] Enable HTTPS in production
- [ ] Set `DEBUG=False` in production
- [ ] Configure CORS for production domain
- [ ] Set up rate limiting
- [ ] Enable CSRF protection
- [ ] Use environment variables for all secrets

---

**Ready to build? Start with the [Architecture](ARCHITECTURE.md) documentation!**
