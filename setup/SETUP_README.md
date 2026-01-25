# GANDALF Setup - Quick Reference

## One-Command Setup

Make GANDALF ready to play with a single command:

```bash
sudo bash setup.sh "your-anthropic-api-key"
```

That's it! The script will:
- ✅ Install all dependencies (MySQL, Python, Node.js, Claude CLI)
- ✅ Set up the database
- ✅ Create Python virtual environment
- ✅ Install all packages
- ✅ Configure environment variables
- ✅ Create and start systemd services
- ✅ Verify everything is working

## Quick Start

### 1. Get Your API Key

Get your Anthropic API key from: https://console.anthropic.com

### 2. Run Setup

```bash
cd /var/www/projects/gandlf
sudo bash setup.sh "sk-ant-api03-..."
```

### 3. Verify

```bash
# Check services
systemctl status gandalf-api.service
systemctl status gandalf-pipeline.service

# Test API
curl http://localhost:5000/health
```

### 4. Test the Application

```bash
curl -X POST http://localhost:5000/api/intent \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-01-25T12:00:00Z",
    "generate_for": "AI-AGENT",
    "user_prompt": "Add a logout button to the navigation bar"
  }'
```

## What Gets Installed

| Component | Version | Port | Purpose |
|-----------|---------|------|---------|
| MySQL | 8.0 | 3306 | Database |
| Python | 3.12 | - | Runtime |
| Node.js | 20.x | - | Claude CLI |
| Flask API | 3.0.2 | 5000 | Main API |
| Pipeline Agent | - | 8081 | CTC Generation |
| Claude Code CLI | 0.2.3 | - | AI Agent |

## Service Management

```bash
# View status
systemctl status gandalf-api.service

# View logs
journalctl -u gandalf-api.service -f

# Restart
systemctl restart gandalf-api.service
```

## Files & Directories

```
/opt/apps/gandlf/              # Application files
/opt/apps/gandlf/venv/         # Python virtual environment
/opt/apps/gandlf/.env          # Configuration (including API key)
/etc/gandalf/db.env            # Database credentials
/var/log/gandlf/               # Service logs
/var/log/gandalf-setup.log     # Setup script log
```

## Troubleshooting

### Setup Failed?

```bash
# Check setup log
cat /var/log/gandalf-setup.log

# Try again
sudo bash setup.sh "your-api-key"
```

### Service Not Starting?

```bash
# Check service logs
journalctl -u gandalf-api.service -n 50

# Check configuration
cat /opt/apps/gandlf/.env

# Restart services
systemctl restart gandalf-pipeline.service
systemctl restart gandalf-api.service
```

### API Not Responding?

```bash
# Check if running
systemctl status gandalf-api.service

# Check port
netstat -tlnp | grep 5000

# Test manually
cd /opt/apps/gandlf
source venv/bin/activate
python3 -m api.app
```

## Cloud-Init Setup

For automated VM provisioning:

```bash
# Edit the cloud-init file with your API key
sed 's/ANTHROPIC_API_KEY_PLACEHOLDER/sk-ant-api03-.../' \
    cloud-init-with-setup.yaml > my-cloud-init.yaml

# Launch VM
multipass launch 24.04 \
    --name gandalf \
    --cpus 2 \
    --memory 4G \
    --disk 40G \
    --cloud-init my-cloud-init.yaml

# Wait for setup (5-10 minutes)
multipass exec gandalf -- cloud-init status --wait

# Check setup log
multipass exec gandalf -- tail -100 /var/log/gandalf-setup.log

# Test API
multipass exec gandalf -- curl http://localhost:5000/health
```

## Next Steps

1. **Read the Full Guide**: See `SETUP_GUIDE.md` for detailed documentation
2. **Test the API**: Try the quick start examples in `QUICK_START.md`
3. **Explore Features**: Check out `QUICK_REFERENCE.md` for API endpoints
4. **Monitor Services**: Use `journalctl` to watch service logs

## Support

- **Setup Issues**: Check `/var/log/gandalf-setup.log`
- **Service Issues**: Check `journalctl -u gandalf-api.service`
- **API Issues**: Check `/var/log/gandlf/api-error.log`
- **Documentation**: See `SETUP_GUIDE.md` for complete guide

---

**Ready in one command!** 🚀
