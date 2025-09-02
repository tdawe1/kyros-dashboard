# Phase B - Token & Cost Controls Implementation

This document describes the implementation of Phase B features for the Kyros Dashboard API.

## Features Implemented

### 1. Server-side Input Limits
- **Max Input Characters**: 100,000 characters (configurable via `MAX_INPUT_CHARACTERS` env var)
- **Token Estimation**: Simple heuristic using `tokens ≈ words × 1.3` (configurable via `TOKEN_ESTIMATION_FACTOR`)
- **Token Cap**: 50,000 tokens per job (configurable via `MAX_TOKENS_PER_JOB` env var)
- **Clear Error Messages**: API returns 400 status with detailed error information

### 2. Per-user Quotas
- **Daily Job Limit**: 10 jobs per day per user (configurable via `DAILY_JOB_LIMIT` env var)
- **Redis Storage**: Uses Redis counters with daily expiration
- **Quota Management**: Endpoints to check and reset user quotas
- **Automatic Cleanup**: Redis keys expire after 24 hours

### 3. Rate Limiting
- **Token Bucket Algorithm**: Implements token bucket rate limiting using Redis
- **Configurable Limits**: 100 requests per hour with 10 burst allowance
- **IP-based Limiting**: Uses client IP for rate limiting (can be extended to user-based)
- **Proper Headers**: Returns rate limit information in response headers

## API Endpoints

### Core Endpoints
- `POST /api/generate` - Enhanced with all validation and quota checks
- `GET /api/quota/{user_id}` - Get current quota status
- `POST /api/quota/{user_id}/reset` - Reset user quota (admin function)
- `POST /api/token-stats` - Get token usage statistics without creating job

### Response Format
All endpoints return structured error responses:
```json
{
  "error": "Error type",
  "message": "Human-readable error message",
  "stats": {
    "character_count": 1500,
    "estimated_tokens": 1950,
    "max_characters": 100000,
    "max_tokens": 50000
  }
}
```

## Configuration

### Environment Variables
```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379

# Token and Input Limits
MAX_INPUT_CHARACTERS=100000
MAX_TOKENS_PER_JOB=50000
TOKEN_ESTIMATION_FACTOR=1.3

# User Quotas
DAILY_JOB_LIMIT=10

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
RATE_LIMIT_BURST=10
```

## Testing

### Stress Test Script
Run the comprehensive stress test:
```bash
cd api
python test_stress.py
```

The stress test covers:
- Rate limiting with rapid requests
- Quota enforcement by exceeding daily limits
- Input validation with various text sizes
- Token estimation accuracy

### Manual Testing
1. **Input Validation**:
   ```bash
   curl -X POST http://localhost:8000/api/generate \
     -H "Content-Type: application/json" \
     -d '{"input_text": "Short", "user_id": "test_user"}'
   ```

2. **Quota Testing**:
   ```bash
   # Check quota status
   curl http://localhost:8000/api/quota/test_user
   
   # Reset quota
   curl -X POST http://localhost:8000/api/quota/test_user/reset
   ```

3. **Token Statistics**:
   ```bash
   curl -X POST http://localhost:8000/api/token-stats \
     -H "Content-Type: application/json" \
     -d '{"input_text": "Your test text here", "user_id": "test_user"}'
   ```

## Architecture

### File Structure
```
api/
├── main.py                 # Main FastAPI application
├── utils/
│   ├── quotas.py          # User quota management
│   └── token_utils.py     # Token estimation and validation
├── middleware/
│   └── rate_limiter.py    # Rate limiting middleware
├── test_stress.py         # Stress testing script
└── env.example           # Environment configuration template
```

### Key Components

1. **Quota Management** (`utils/quotas.py`):
   - Redis-based daily counters
   - Automatic expiration
   - Fail-open design (allows requests if Redis is down)

2. **Token Utilities** (`utils/token_utils.py`):
   - Word-based token estimation
   - Input validation
   - Usage statistics

3. **Rate Limiter** (`middleware/rate_limiter.py`):
   - Token bucket algorithm
   - Redis-backed state management
   - Proper HTTP headers

## Error Handling

The implementation follows a fail-open approach for external dependencies:
- If Redis is unavailable, quota checks pass and rate limiting is disabled
- All errors are logged for monitoring
- Clear error messages help users understand limits

## Monitoring

All operations are logged with appropriate levels:
- INFO: Successful operations and quota usage
- WARNING: Rate limit violations
- ERROR: System errors and quota failures

## Next Steps (Phase C)

This implementation provides the foundation for:
- Real OpenAI API integration
- Job lifecycle management
- Database persistence
- Enhanced monitoring and alerting
