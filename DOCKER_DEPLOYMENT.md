# Docker Deployment Guide

This guide covers deploying the Earring Generator using Docker, particularly for Raspberry Pi with SWAG.

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The application will be available at `http://localhost:8080`

### Option 2: Using Docker Directly

```bash
# Build the image
docker build -t earring-generator .

# Run the container
docker run -d \
  --name earring-generator \
  -p 8080:80 \
  --restart unless-stopped \
  earring-generator

# View logs
docker logs -f earring-generator

# Stop the container
docker stop earring-generator
docker rm earring-generator
```

## Integration with SWAG

SWAG (Secure Web Application Gateway) provides reverse proxy with SSL certificates.

### Step 1: Ensure the Container is Running

```bash
docker-compose up -d
# or
docker ps | grep earring-generator
```

### Step 2: Configure SWAG

Create a new proxy configuration file in your SWAG config directory:

**For Subdomain** (e.g., `earring.yourdomain.com`):

Create `/path/to/swag/config/nginx/proxy-confs/earring.subdomain.conf`:

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    server_name earring.*;

    include /config/nginx/ssl.conf;

    client_max_body_size 50M;

    location / {
        include /config/nginx/proxy.conf;
        resolver 127.0.0.11 valid=30s;
        set $upstream_app earring-generator;
        set $upstream_port 80;
        set $upstream_proto http;
        proxy_pass $upstream_proto://$upstream_app:$upstream_port;
    }
}
```

**For Subfolder** (e.g., `yourdomain.com/earring`):

Add to your main domain config or create `/path/to/swag/config/nginx/proxy-confs/earring.subfolder.conf`:

```nginx
location /earring {
    return 301 $scheme://$host/earring/;
}

location ^~ /earring/ {
    include /config/nginx/proxy.conf;
    resolver 127.0.0.11 valid=30s;
    set $upstream_app earring-generator;
    set $upstream_port 80;
    set $upstream_proto http;
    proxy_pass $upstream_proto://$upstream_app:$upstream_port/;
}
```

### Step 3: Connect to SWAG Network

Add the earring-generator container to SWAG's network:

```bash
# Find SWAG's network name
docker network ls | grep swag

# Connect earring-generator to SWAG network
docker network connect swag_default earring-generator
```

Or update `docker-compose.yml` to use SWAG's network:

```yaml
networks:
  default:
    external:
      name: swag_default
```

### Step 4: Restart SWAG

```bash
docker restart swag
```

### Step 5: Configure DNS

Point your subdomain to your Raspberry Pi's IP address:
- `earring.yourdomain.com` → Your Pi's IP

SWAG will automatically obtain an SSL certificate via Let's Encrypt.

## Building for Raspberry Pi (ARM)

If building on a different architecture:

```bash
# Build for ARM64 (Raspberry Pi 4/5)
docker buildx build --platform linux/arm64 -t earring-generator .

# Build for ARM32 (Raspberry Pi 3 and older)
docker buildx build --platform linux/arm/v7 -t earring-generator .
```

## Updating the Application

### Rebuild and Restart

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Or with docker directly
docker build -t earring-generator .
docker stop earring-generator
docker rm earring-generator
docker run -d --name earring-generator -p 8080:80 --restart unless-stopped earring-generator
```

## Troubleshooting

### Check Container Logs

```bash
docker logs -f earring-generator
```

### Check Container Health

```bash
docker ps
# Look for "healthy" status
```

### Test Container Directly

```bash
# Get container IP
docker inspect earring-generator | grep IPAddress

# Test health endpoint
curl http://localhost:8080/health

# Test API
curl http://localhost:8080/api/preview?seed=test&diameter=12
```

### Common Issues

**Build fails on Raspberry Pi:**
- Ensure you have enough disk space (check with `df -h`)
- Increase swap if needed: `sudo dphys-swapfile swapoff && sudo dphys-swapfile swapon`
- Build may take 10-20 minutes on older Pi models

**Container exits immediately:**
- Check logs: `docker logs earring-generator`
- Verify port 8080 is not in use: `sudo lsof -i :8080`

**Can't access from SWAG:**
- Verify containers are on same network: `docker network inspect swag_default`
- Check SWAG logs: `docker logs swag`
- Verify nginx config syntax: `docker exec swag nginx -t`

**Frontend loads but API calls fail:**
- Check nginx config in container: `docker exec earring-generator nginx -t`
- Verify gunicorn is running: `docker exec earring-generator ps aux | grep gunicorn`

## Configuration

### Environment Variables

Modify in `docker-compose.yml`:

```yaml
environment:
  - USE_VECTOR_GENERATOR=true  # Use vector-based generation (recommended)
  - PYTHONUNBUFFERED=1          # Better logging
```

### Change Port

Modify in `docker-compose.yml`:

```yaml
ports:
  - "9000:80"  # Change 9000 to your preferred port
```

### Resource Limits (for Raspberry Pi)

Add to `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
    reservations:
      memory: 512M
```

## Production Recommendations

1. **Use Docker Compose** for easier management
2. **Set up automatic restarts** with `restart: unless-stopped`
3. **Monitor logs** regularly: `docker-compose logs -f`
4. **Back up configurations** in case of SD card failure
5. **Use SWAG** for automatic SSL certificate management
6. **Set resource limits** to prevent Pi from freezing under load

## Performance Notes

- Initial build on Raspberry Pi 4: ~10-15 minutes
- Initial build on Raspberry Pi 3: ~20-30 minutes
- Runtime memory usage: ~200-400 MB
- Pattern generation: 0.5-2 seconds depending on complexity
- 3D export: 1-3 seconds

## Security

- Container runs nginx and Flask backend internally
- Only port 80 is exposed from container
- SWAG handles SSL/TLS termination
- No sensitive data stored in container
- Frontend and backend run in isolated container
