# Acceptance
- Remove redundant index=True where unique=True exists
- Add server_default for is_active (SQL true)
- Alembic migration updates schema without data loss
- Tests cover insert without ORM default and uniqueness
