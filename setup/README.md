# GANDALF Setup Directory

This directory contains all the setup scripts and configuration needed to deploy GANDALF.

## Files

### 🚀 Main Setup Script
- **`setup.sh`** - Complete automated setup script (run this to install everything)

### ☁️ Cloud Configuration
- **`cloud-init.yaml`** - Cloud-init configuration for automated VM provisioning

### ✅ Verification
- **`verify_setup.sh`** - Post-installation verification script with 17+ checks

### 📚 Documentation
- **`SETUP_GUIDE.md`** - Comprehensive setup guide with troubleshooting
- **`SETUP_README.md`** - Quick reference card for common operations

## Quick Start

### Manual Setup
```bash
cd /var/www/projects/gandlf/setup
sudo bash setup.sh "your-anthropic-api-key"
```

### Cloud-Init (Automated VM)
```bash
# Replace API key in cloud-init config
sed 's/ANTHROPIC_API_KEY_PLACEHOLDER/your-actual-key/' \
    setup/cloud-init.yaml > /tmp/gandalf-cloud-init.yaml

# Launch VM with multipass
multipass launch 24.04 --name gandalf \
    --cloud-init /tmp/gandalf-cloud-init.yaml \
    --cpus 2 --memory 4G --disk 20G

# Or with custom mount for development
multipass launch 24.04 --name gandalf \
    --cloud-init /tmp/gandalf-cloud-init.yaml \
    --mount /local/path:/var/www/projects/gandlf \
    --cpus 2 --memory 4G --disk 20G
```

### Verify Installation
```bash
cd /var/www/projects/gandlf/setup
bash verify_setup.sh
```

## What Gets Set Up

✅ MySQL Server 8.0 with `gandalf_db` database
✅ Python 3.12 virtual environment with all packages
✅ Flask API service on port 5000
✅ Pipeline Agent service on port 8081
✅ Claude Code CLI
✅ All services enabled for auto-start on boot
✅ Comprehensive logging to `/var/log/gandlf/`
✅ Secure configuration files

## Service Management

```bash
# Check service status
sudo systemctl status gandalf-api.service
sudo systemctl status pipeline-agent.service

# View logs
sudo journalctl -u gandalf-api.service -f
sudo journalctl -u pipeline-agent.service -f

# Restart services
sudo systemctl restart gandalf-api.service
sudo systemctl restart pipeline-agent.service
```

## Troubleshooting

See **`SETUP_GUIDE.md`** for comprehensive troubleshooting guide.

Common issues:
- **Services won't start**: Check logs with `journalctl -xe`
- **Database connection fails**: Verify `.env` file in `/opt/apps/gandlf/`
- **API returns 500**: Check `/var/log/gandlf/error.log`

## Directory Structure

```
/var/www/projects/gandlf/    # Source code repository
/opt/apps/gandlf/            # Runtime directory
/var/log/gandlf/             # Application logs
/etc/gandlf/                 # Configuration files
```

## Security Notes

- Database credentials: `/opt/apps/gandlf/.env` (mode 600)
- API key configuration: `/opt/apps/gandlf/.env` (mode 600)
- All services run as user `claude`
- MySQL only listens on localhost

## Support

For issues or questions:
1. Check `SETUP_GUIDE.md` for detailed documentation
2. Run `verify_setup.sh` to identify configuration problems
3. Check service logs: `/var/log/gandlf/` and `journalctl`
