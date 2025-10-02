# Railway Deployment Instructions

## 🚀 Quick Setup

### 1. Add PostgreSQL Database
1. In Railway dashboard, click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
2. Wait for database to provision

### 2. Configure Environment Variables
Go to your **Backend Service** → **Variables** tab and add:

```
DATABASE_URL=${{ Postgres.DATABASE_URL }}
SECRET_KEY=<generate-a-random-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

### 3. Generate SECRET_KEY
Run locally to generate a secure key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 4. Verify Deployment
Check the logs for:
```
✅ DATABASE_URL found in environment variables
Creating database tables...
✅ Database tables created successfully!
```

## ⚠️ Common Issues

### Error: "connection to server at localhost"
**Solution**: You forgot to add `DATABASE_URL` environment variable in Railway.
- Go to Variables tab
- Add: `DATABASE_URL=${{ Postgres.DATABASE_URL }}`

### Error: "pydantic-core build failed"
**Solution**: Already fixed with Python 3.11 in `runtime.txt`

## 📝 Environment Variables Reference

| Variable | Value | Required |
|----------|-------|----------|
| `DATABASE_URL` | `${{ Postgres.DATABASE_URL }}` | ✅ Yes |
| `SECRET_KEY` | Random secure string | ✅ Yes |
| `ALGORITHM` | `HS256` | Optional |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` | Optional |
