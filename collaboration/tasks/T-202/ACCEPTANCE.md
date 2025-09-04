# Acceptance
- Settings.jwt_secret_key uses default_factory (not required Field)
- Validator enforces min length (>=32) and logs guidance
- App boots without env set; secrets scan remains clean
- Docs note to set JWT_SECRET_KEY in non-dev
