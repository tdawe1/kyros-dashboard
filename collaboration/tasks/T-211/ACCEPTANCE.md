# Acceptance
- Settings.jwt_secret_key uses default_factory instead of required Field
- Validator enforces min length (>=32) and logs guidance
- App boots without env; docs note setting JWT_SECRET_KEY for stability
- Secret scan remains clean
