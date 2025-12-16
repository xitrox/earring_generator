# Docker Setup with SWAG

Quick setup guide for deploying on Raspberry Pi with SWAG.

## Prerequisites

1. SWAG installed and running
2. Domain configured (e.g., `your-domain.com`)
3. DNS record pointing to your Pi:
   - `earring.your-domain.com` → Your Pi IP

**Note**: Only ONE subdomain needed! The backend API is not exposed publicly.

## Setup Steps

### 1. Build and Start Containers

No configuration changes needed - just build and start:

```bash
docker-compose up -d --build
```

This will:
- Build the backend container (earring-api, internal only)
- Build the frontend container (earring-frontend on port 8447)
- Frontend nginx proxies API requests to backend internally
- Start both containers

### 2. Configure SWAG

Copy the SWAG config (only ONE subdomain needed):

```bash
sudo cp deployment/swag-earring.subdomain.conf /path/to/swag/config/nginx/proxy-confs/earring.subdomain.conf
```

Or manually create `/path/to/swag/config/nginx/proxy-confs/earring.subdomain.conf`:

```nginx
server {
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name earring.*;

    include /config/nginx/ssl.conf;

    client_max_body_size 0;

    location / {
        include /config/nginx/proxy.conf;
        include /config/nginx/resolver.conf;
        set $upstream_app earring-frontend;
        set $upstream_port 8447;
        set $upstream_proto http;
        proxy_pass $upstream_proto://$upstream_app:$upstream_port;
    }
}
```

### 3. Connect Container to SWAG Network

```bash
# Find your SWAG network name
docker network ls | grep swag

# Connect frontend container (replace 'swag_default' with your network name if different)
docker network connect swag_default earring-frontend

# Note: Backend doesn't need to be connected - it's only accessed internally by frontend
```

### 4. Restart SWAG

```bash
docker restart swag
```

### 5. Access Your Application

Open your browser and navigate to:
- **https://earring.your-domain.com**

SWAG will automatically obtain SSL certificates via Let's Encrypt.

## Verify Setup

Check that containers are running:
```bash
docker ps | grep earring
```

You should see both:
- `earring-api` (internal only, no host ports)
- `earring-frontend` on port 8447

Check container health:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Both should show "healthy".

## Architecture

```
Internet
  ↓
SWAG (port 443) - earring.your-domain.com
  ↓
earring-frontend:8447 (nginx)
  ├─ Static files (/, /assets/*)
  └─ API proxy (/api/* → earring-api:9447)
       ↓
     earring-api:9447 (Flask, internal only)
```

**Security benefits:**
- Backend API never exposed to internet
- Only frontend port accessible via SWAG
- Internal Docker network communication
- No CORS issues (same domain)

## Updating

To update after code changes:

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

## Logs

View backend logs:
```bash
docker logs -f earring-api
```

View frontend logs:
```bash
docker logs -f earring-frontend
```

View SWAG logs:
```bash
docker logs -f swag
```

## Troubleshooting

### Containers won't start
```bash
# Check logs
docker logs earring-api
docker logs earring-frontend

# Verify ports aren't in use
sudo lsof -i :9447
sudo lsof -i :8447
```

### Can't access through SWAG
```bash
# Verify containers are on SWAG network
docker network inspect swag_default | grep earring

# Check SWAG nginx config
docker exec swag nginx -t

# Restart SWAG
docker restart swag
```

### Frontend shows but API calls fail
- Check that both containers are on the same Docker network: `docker network inspect earring-net`
- Verify frontend nginx can reach backend: `docker exec earring-frontend wget -O- http://earring-api:9447/health`
- Check frontend nginx logs: `docker logs earring-frontend`
- Check backend logs: `docker logs earring-api`

### SSL certificate not working
- Wait a few minutes for Let's Encrypt
- Check SWAG logs: `docker logs swag | grep cert`
- Verify DNS is propagated: `nslookup earring.your-domain.com`

## Resource Usage

Expected resource usage on Raspberry Pi:
- Backend: ~100-200 MB RAM
- Frontend: ~20-30 MB RAM
- CPU: <5% idle, <50% during generation

## Port Reference

- 9447: Backend API (earring-api) - **Internal only, not exposed to host**
- 8447: Frontend nginx (earring-frontend) - Exposed to host for SWAG
- 443: SWAG (exposed to internet)

**Note**: The backend API is only accessible from within the Docker network, not from the host or internet.
