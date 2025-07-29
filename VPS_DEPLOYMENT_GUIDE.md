# 🚀 VPS Deployment Guide

## Overview
Deploy the NuiFlo WorkForce API to your VPS (37.27.223.110) with local Ollama integration.

## Architecture
```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Container │
│   (External)    │◄──►│   (Port 8000)   │
└─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Host Ollama   │
                       │ (Port 11434)    │
                       └─────────────────┘
```

## Prerequisites

### 1. VPS Requirements
- ✅ Ubuntu/Debian system
- ✅ Docker and Docker Compose installed
- ✅ Ollama running on host (already done)
- ✅ SSH access configured

### 2. Local Requirements
- ✅ Docker installed
- ✅ SSH key access to VPS
- ✅ Environment variables configured

## Deployment Steps

### 1. Prepare Environment File
Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql+psycopg://your_db_user:your_db_password@your_db_host:5432/your_db_name?sslmode=require

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key
SUPABASE_ANON_KEY=your_supabase_anon_key

# LLM API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Ollama Configuration (on host)
OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_MODEL=deepseek-coder:6.7b

# Environment
ENVIRONMENT=production

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2. Run Deployment
```bash
./deploy-vps.sh
```

This script will:
- Build the Docker image locally
- Copy files to VPS
- Deploy the container
- Check health status

### 3. Verify Deployment
```bash
# Check container status
ssh root@37.27.223.110 "docker-compose ps"

# Check logs
ssh root@37.27.223.110 "docker-compose logs -f"

# Test API
curl http://37.27.223.110:8000/health/ping
```

## API Endpoints

Once deployed, your API will be available at:

- **API Base URL**: `http://37.27.223.110:8000`
- **Health Check**: `http://37.27.223.110:8000/health/ping`
- **API Documentation**: `http://37.27.223.110:8000/docs`
- **OpenAPI Spec**: `http://37.27.223.110:8000/openapi.json`

## Troubleshooting

### Container Won't Start
```bash
# Check logs
ssh root@37.27.223.110 "docker-compose logs"

# Check if Ollama is accessible from container
ssh root@37.27.223.110 "docker exec nuiflo-workforce-api curl http://host.docker.internal:11434/api/tags"
```

### API Can't Connect to Ollama
The container uses `host.docker.internal` to connect to the host's Ollama. If this doesn't work:

1. **Check Ollama is running on host:**
   ```bash
   ssh root@37.27.223.110 "curl http://localhost:11434/api/tags"
   ```

2. **Use host network mode** (alternative):
   Update `docker-compose.yml`:
   ```yaml
   network_mode: "host"
   ```

### Database Connection Issues
1. Check your `DATABASE_URL` in `.env`
2. Ensure Supabase is accessible from VPS
3. Verify SSL mode settings

## Security Considerations

### 1. Firewall Setup
```bash
# On VPS
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8000  # API port
sudo ufw allow 11434  # Ollama port (if needed externally)
```

### 2. SSL/TLS (Recommended)
For production, set up SSL with Nginx or Traefik:

```bash
# Install Nginx
sudo apt install nginx

# Configure reverse proxy
sudo nano /etc/nginx/sites-available/nuiflo-api
```

### 3. Environment Variables
- Never commit `.env` files
- Use strong secret keys
- Rotate API keys regularly

## Monitoring

### 1. Container Health
```bash
# Check container status
docker-compose ps

# Monitor logs
docker-compose logs -f nuiflo-api
```

### 2. System Resources
```bash
# Check resource usage
docker stats

# Monitor disk space
df -h
```

### 3. API Health
```bash
# Health check endpoint
curl http://37.27.223.110:8000/health/status
```

## Updates and Maintenance

### 1. Update API
```bash
# Pull latest code
git pull

# Redeploy
./deploy-vps.sh
```

### 2. Update Ollama Model
```bash
# SSH to VPS
ssh root@37.27.223.110

# Pull new model
ollama pull deepseek-coder:6.7b
```

### 3. Backup Database
```bash
# Backup Supabase (if self-hosted)
pg_dump your_database > backup.sql
```

## Performance Optimization

### 1. Container Resources
Update `docker-compose.yml`:
```yaml
services:
  nuiflo-api:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

### 2. Ollama Performance
- Use GPU if available
- Adjust model parameters
- Monitor memory usage

## Support

If you encounter issues:
1. Check container logs
2. Verify network connectivity
3. Test Ollama connection
4. Review environment variables

---

**🎉 Your NuiFlo WorkForce API is now deployed on your VPS with local Ollama integration!** 