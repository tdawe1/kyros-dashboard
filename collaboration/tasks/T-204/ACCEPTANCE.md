# Acceptance
- router.get("/users", response_model=List[User]) applied
- Endpoint returns schema-conformant payload; pagination respected
- Test asserts 200 and response shape under admin role
