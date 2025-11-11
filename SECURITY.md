# Security Documentation

## Overview

The Cognisphere implements comprehensive security measures to protect against common vulnerabilities and ensure safe operation in production environments.

## Security Features

### Input Validation

All API endpoints use Pydantic models with comprehensive validation:

- **Type Validation**: All inputs validated for correct types
- **Range Validation**: Numeric inputs validated with min/max constraints
- **Path Traversal Prevention**: File paths validated to prevent directory traversal attacks
- **Action Whitelisting**: Simulation actions validated against allowed values
- **String Length Limits**: String inputs validated with maximum length constraints

### CORS Configuration

CORS (Cross-Origin Resource Sharing) is configured based on environment:

- **Development**: Allows all origins for local development
- **Production**: Restricts to configured origins via `CORS_ORIGINS` environment variable
- **Methods**: Only allows safe HTTP methods (GET, POST, PUT, DELETE, OPTIONS)
- **Credentials**: Supports credential-based authentication

### Error Handling

Security-aware error handling prevents information disclosure:

- **Production Mode**: Error messages don't leak internal details
- **Development Mode**: Detailed error messages for debugging
- **HTTP Status Codes**: Uses appropriate status codes (400, 401, 403, 404, 500)
- **Exception Handling**: Global exception handler prevents information disclosure

### Environment Variables

All sensitive data stored in environment variables:

- **No Hardcoded Secrets**: All API keys, tokens, and credentials use environment variables
- **`.env.example` Files**: Example files provided without actual secrets
- **Gitignore Protection**: All `.env` files and secrets directories excluded from version control

## Security Best Practices

### 1. Never Commit Secrets

- All `.env` files are in `.gitignore`
- All `secrets/` directories are in `.gitignore`
- All `*.key`, `*.pem`, `*.secret` files are in `.gitignore`
- Example files (`.env.example`) don't contain actual secrets

### 2. Use Environment Variables

Store all sensitive data in environment variables:

```bash
# Backend
export OPENAI_API_KEY="your-key-here"
export NEO4J_PASSWORD="your-password-here"
export CORS_ORIGINS="https://yourdomain.com"

# Frontend
export VITE_API_URL="https://api.yourdomain.com"
```

### 3. Restrict CORS in Production

Set `CORS_ORIGINS` environment variable for production:

```bash
export CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
export ENVIRONMENT="production"
```

### 4. Validate All Inputs

All API endpoints validate inputs with Pydantic models:

- Type checking
- Range validation
- String length limits
- Path traversal prevention
- Action whitelisting

### 5. Use HTTPS in Production

Always use HTTPS for production deployments:

- Use TLS/SSL certificates
- Redirect HTTP to HTTPS
- Use secure cookies
- Enable HSTS (HTTP Strict Transport Security)

### 6. Regular Updates

Keep dependencies updated to patch security vulnerabilities:

```bash
# Update Python dependencies
pip install --upgrade -r requirements.txt

# Update Node.js dependencies
npm update
```

## Security Audit

The project has been audited for common security issues:

### ✅ No Hardcoded Credentials

- All secrets use environment variables
- No API keys in source code
- No passwords in configuration files
- No tokens in commit history

### ✅ No Dangerous Code Execution

- No `eval()` or `exec()` calls
- No dangerous code execution patterns
- No arbitrary code execution vulnerabilities

### ✅ Input Validation

- All inputs validated and sanitized
- Path traversal prevention
- SQL injection prevention (if using SQL databases)
- XSS prevention (frontend)

### ✅ Path Traversal Protection

- File paths validated to prevent attacks
- Snapshot names validated
- Directory traversal prevented
- Absolute paths rejected

### ✅ CORS Configuration

- Properly configured for production
- Environment-based configuration
- Secure defaults
- Configurable origins

### ✅ Error Handling

- Security-aware error messages
- No information disclosure
- Proper HTTP status codes
- Global exception handling

### ✅ Dependency Security

- Regular dependency updates
- Security vulnerability scanning
- Dependency pinning
- Regular audits

## Common Vulnerabilities

### Path Traversal

**Prevention**: All file paths validated to prevent directory traversal:

```python
@validator("snapshot_directory")
def validate_snapshot_directory(cls, v):
    if ".." in v or v.startswith("/"):
        raise ValueError("Invalid snapshot directory path")
    return v
```

### SQL Injection

**Prevention**: Using parameterized queries and ORM (if using SQL databases):

- Parameterized queries
- ORM usage
- Input validation
- No raw SQL queries

### XSS (Cross-Site Scripting)

**Prevention**: Frontend uses React with automatic XSS protection:

- React's built-in XSS protection
- Input sanitization
- Content Security Policy (CSP)
- No `dangerouslySetInnerHTML` usage

### CSRF (Cross-Site Request Forgery)

**Prevention**: Using CSRF tokens and SameSite cookies:

- CSRF tokens
- SameSite cookies
- Origin validation
- Referer checking

### Information Disclosure

**Prevention**: Security-aware error handling:

- No internal error details in production
- Proper HTTP status codes
- No stack traces in production
- No sensitive data in logs

## Reporting Security Issues

If you discover a security vulnerability, please report it responsibly:

1. **Email**: [security@example.com] (replace with your security contact)
2. **Do not** open a public GitHub issue
3. **Include**: 
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
4. **Response**: We will respond within 48 hours

## Security Checklist

Before deploying to production:

- [ ] All `.env` files are in `.gitignore`
- [ ] All secrets are in environment variables
- [ ] `CORS_ORIGINS` is set for production
- [ ] `ENVIRONMENT` is set to "production"
- [ ] HTTPS is enabled
- [ ] All dependencies are updated
- [ ] Security audit has been performed
- [ ] Input validation is working
- [ ] Error handling is security-aware
- [ ] Logging doesn't expose sensitive data

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [React Security](https://reactjs.org/docs/dom-elements.html#dangerouslysetinnerhtml)
- [Python Security](https://python.readthedocs.io/en/latest/library/security.html)

