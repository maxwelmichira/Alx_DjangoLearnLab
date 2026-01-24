# HTTPS and SSL/TLS Deployment Guide

## Overview
This guide provides instructions for deploying LibraryProject with HTTPS using Nginx and Let's Encrypt SSL certificates.

---

## 1. Install Required Packages
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

---

## 2. Initial Nginx Configuration

Create `/etc/nginx/sites-available/libraryproject`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location /static/ {
        alias /path/to/LibraryProject/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/libraryproject /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

---

## 3. Obtain SSL Certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Certbot will automatically configure HTTPS and set up renewal.

---

## 4. Final Nginx Configuration (After Certbot)
```nginx
# HTTP - Redirect to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Configuration
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    add_header X-Frame-Options "DENY";
    add_header X-Content-Type-Options "nosniff";

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

---

## 5. Django Configuration

Settings are already configured in `settings.py`:
- SECURE_SSL_REDIRECT = True
- SECURE_HSTS_SECONDS = 31536000
- SESSION_COOKIE_SECURE = True
- CSRF_COOKIE_SECURE = True

---

## 6. Deploy with Gunicorn
```bash
pip install gunicorn
gunicorn --bind 127.0.0.1:8000 LibraryProject.wsgi:application
```

---

## 7. Verify HTTPS

- Visit: https://yourdomain.com
- Check SSL: https://www.ssllabs.com/ssltest/
- Test auto-renewal: `sudo certbot renew --dry-run`

---

## Security Checklist

- [x] SSL certificate installed
- [x] HTTP redirects to HTTPS
- [x] HSTS configured (31536000 seconds)
- [x] Secure cookies enabled
- [x] Security headers active
- [x] Django deployment check passed

Run: `python manage.py check --deploy`

---

## Troubleshooting

**502 Bad Gateway**: Check Gunicorn is running
**Certificate Errors**: Verify domain DNS points to server
**Mixed Content**: Ensure all assets use HTTPS

---

For more info: https://docs.djangoproject.com/en/stable/howto/deployment/
