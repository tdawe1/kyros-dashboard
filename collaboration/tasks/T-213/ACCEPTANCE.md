# Acceptance
- router.get("/users", response_model=List[User]) applied
- Response matches schema; pagination respected
- Test asserts 200 and response shape (admin-only)
