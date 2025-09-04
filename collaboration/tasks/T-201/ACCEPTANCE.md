# Acceptance
- Handles Redis byte keys/values for "tokens" and "last_refill"
- Maintains correct token counts across consecutive requests
- Safe fallback if pipeline() unavailable (non-atomic path)
- Unit tests cover str/bytes Redis responses
