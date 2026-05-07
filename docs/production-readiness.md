# Production Readiness Checklist

## Security Baseline

- Set `DJANGO_DEBUG=False`
- Set a strong `DJANGO_SECRET_KEY`
- Configure `DJANGO_ALLOWED_HOSTS`
- Enable cookie security and TLS flags in `.env`
- Configure `DJANGO_CSRF_TRUSTED_ORIGINS` for real domains

## Observability

- Use `APP_LOG_LEVEL=INFO` (or stricter in production)
- Aggregate stdout logs in your hosting platform
- Monitor error rate on API namespaces under `/api/v1/`

## Push Delivery

- Default `PUSH_PROVIDER=log` is safe for staging
- Use `PUSH_PROVIDER=mock` for integration testing
- Keep `PUSH_PROVIDER=disabled` for environments that must avoid external delivery

## Backups and Recovery

- Run backup tasks on a schedule and validate artifacts
- Validate restore flow before go-live
- Define retention policy and ownership

## Testing Gate

- Run `python manage.py test` in CI
- Add coverage for accounts approvals, attendance, notifications, and reports before launch
