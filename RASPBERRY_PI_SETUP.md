# Raspberry Pi Deployment with SWAG

This guide explains how to deploy the Earring Generator on a Raspberry Pi with SWAG (Secure Web Application Gateway) for SSL and reverse proxy.

## Prerequisites

- Raspberry Pi with Raspbian/Ubuntu
- SWAG already installed and running
- Python 3.8+ installed
- Node.js 16+ installed
- Domain or subdomain pointing to your Pi

## Deployment Steps

### 1. Install Backend Dependencies

```bash
cd /home/xi/projects/earring_generator/backend
pip3 install -r requirements.txt
```

### 2. Build Frontend for Production

```bash
cd /home/xi/projects/earring_generator/frontend
npm install
npm run build
```

This creates optimized static files in `frontend/dist/`

### 3. Set Up Backend Service

Create a systemd service for the Flask backend:

```bash
sudo cp /home/xi/projects/earring_generator/deployment/earring-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable earring-backend
sudo systemctl start earring-backend
```

Check status:
```bash
sudo systemctl status earring-backend
```

### 4. Configure SWAG Reverse Proxy

Copy the nginx configuration to SWAG:

```bash
# Copy the subdomain config to SWAG
sudo cp /home/xi/projects/earring_generator/deployment/earring.subdomain.conf \
    /path/to/swag/nginx/proxy-confs/

# Or if using a subfolder instead of subdomain:
sudo cp /home/xi/projects/earring_generator/deployment/earring.subfolder.conf \
    /path/to/swag/nginx/proxy-confs/
```

**Note**: Update the paths in the config file to match your actual installation directory.

### 5. Restart SWAG

```bash
docker restart swag
```

### 6. Access Your Application

- **Subdomain**: https://earring.yourdomain.com
- **Subfolder**: https://yourdomain.com/earring

## Service Management

**Start backend**:
```bash
sudo systemctl start earring-backend
```

**Stop backend**:
```bash
sudo systemctl stop earring-backend
```

**Restart backend**:
```bash
sudo systemctl restart earring-backend
```

**View logs**:
```bash
sudo journalctl -u earring-backend -f
```

## Updating the Application

### Update Backend Code
```bash
cd /home/xi/projects/earring_generator/backend
git pull
sudo systemctl restart earring-backend
```

### Update Frontend
```bash
cd /home/xi/projects/earring_generator/frontend
git pull
npm run build
# No restart needed - static files are served by nginx
```

## Troubleshooting

### Backend not starting
```bash
# Check logs
sudo journalctl -u earring-backend -n 50

# Check if port 5000 is in use
sudo lsof -i :5000

# Test backend manually
cd /home/xi/projects/earring_generator/backend
gunicorn --bind 0.0.0.0:5000 app:app
```

### Frontend not loading
- Check SWAG logs: `docker logs swag`
- Verify nginx config syntax: `docker exec swag nginx -t`
- Check file permissions on `frontend/dist/` directory

### API calls failing (CORS errors)
- Ensure backend URL in nginx config matches your setup
- Check that CORS is enabled in `backend/app.py` (already configured)

## Configuration Options

### Custom Domain/Subdomain
Edit `/path/to/swag/nginx/proxy-confs/earring.subdomain.conf` and change:
- `server_name` to your subdomain
- Restart SWAG

### Change Backend Port
If port 5000 conflicts with another service:
1. Edit `deployment/earring-backend.service` and change the port in ExecStart
2. Edit the nginx config to point to the new port
3. Restart both services

## Security Notes

- SWAG handles SSL certificates automatically via Let's Encrypt
- Backend runs on localhost:5000 (not exposed to internet)
- All external traffic goes through SWAG's nginx reverse proxy
- Frontend is served as static files (no Node.js server needed in production)
