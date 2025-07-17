# Alembic Migrations

## Initialize Alembic (if not already done)
```
alembic init alembic
```

## Edit `alembic.ini`
- Set `sqlalchemy.url` to your `DATABASE_URL` (can use env var)

## Create a Migration
```
alembic revision --autogenerate -m "Initial migration"
```

## Apply Migrations
```
alembic upgrade head
```

## Notes
- Make sure your models are imported in `alembic/env.py`.
- Use `alembic history` to see migration history. 