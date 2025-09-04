# Acceptance
- Reads Redis hash keys/values as str or bytes for tokens/last_refill
- Maintains correct token counts across consecutive requests
- Safe non-atomic path if pipeline() unavailable
- Adds unit tests covering str/bytes hash responses
