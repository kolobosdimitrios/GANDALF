# Setup Directory Reorganization Summary

**Date:** 2026-01-25
**Ticket:** GANDLF-0010
**Change:** Consolidated all setup logic into dedicated `setup/` directory

## Changes Made

### 1. Created Setup Directory Structure

All setup-related files are now organized in `/var/www/projects/gandlf/setup/`:

```
setup/
├── README.md                 # Setup directory guide (NEW)
├── cloud-init.yaml          # Cloud-init configuration (MOVED & RENAMED)
├── setup.sh                 # Main setup script (MOVED)
├── verify_setup.sh          # Verification script (MOVED)
├── SETUP_GUIDE.md          # Comprehensive guide (MOVED)
└── SETUP_README.md         # Quick reference (MOVED)
```

### 2. Files Moved

| Original Location | New Location | Status |
|-------------------|--------------|--------|
| `setup.sh` | `setup/setup.sh` | ✅ Moved |
| `verify_setup.sh` | `setup/verify_setup.sh` | ✅ Moved |
| `cloud-init-with-setup.yaml` | `setup/cloud-init.yaml` | ✅ Moved & Renamed |
| `SETUP_GUIDE.md` | `setup/SETUP_GUIDE.md` | ✅ Moved |
| `SETUP_README.md` | `setup/SETUP_README.md` | ✅ Moved |

### 3. Files Removed

| File | Reason |
|------|--------|
| `cloud-init/gandalf-cloud-init.yaml` | Outdated, used wrong database credentials (`gandalf` vs `gandalf_db`) |
| `cloud-init/` directory | Empty after cleanup |

### 4. Files Created

| File | Purpose |
|------|---------|
| `setup/README.md` | Guide for the setup directory with quick start instructions |
| `setup/REORGANIZATION_SUMMARY.md` | This document |

### 5. Files Updated

| File | Changes |
|------|---------|
| `setup/cloud-init.yaml` | Updated path: `cd /var/www/projects/gandlf/setup` |
| `README.md` | Added setup directory references and automated setup option |

## Why This Change?

### Before (Problems)
- Setup files scattered in project root
- Confusing to find setup-related files
- Two different cloud-init files with conflicting configs
- Old cloud-init used wrong database credentials

### After (Benefits)
✅ **Organized** - All setup logic in one place
✅ **Clear** - Easy to find and understand setup process
✅ **Consistent** - Single source of truth for setup
✅ **Updated** - Removed outdated configuration files
✅ **Documented** - Comprehensive guides in dedicated location

## Migration Guide

### For New Deployments

Use the new setup directory:

```bash
# Automated setup
cd /var/www/projects/gandlf/setup
sudo bash setup.sh "your-anthropic-api-key"

# Verify
bash verify_setup.sh
```

### For Cloud-Init

Use the updated cloud-init file:

```bash
# Replace API key
sed 's/ANTHROPIC_API_KEY_PLACEHOLDER/your-actual-key/' \
    setup/cloud-init.yaml > /tmp/gandalf-cloud-init.yaml

# Launch VM
multipass launch 24.04 --name gandalf \
    --cloud-init /tmp/gandalf-cloud-init.yaml
```

### For Existing Deployments

No action needed. The scripts work from their new location.

## Path References Updated

| Component | Old Path | New Path |
|-----------|----------|----------|
| Setup script | `/var/www/projects/gandlf/setup.sh` | `/var/www/projects/gandlf/setup/setup.sh` |
| Cloud-init | `/var/www/projects/gandlf/cloud-init-with-setup.yaml` | `/var/www/projects/gandlf/setup/cloud-init.yaml` |
| Verification | `/var/www/projects/gandlf/verify_setup.sh` | `/var/www/projects/gandlf/setup/verify_setup.sh` |

## Documentation Updates

### Main README.md
- Added "Automated Setup Available!" notice at top of Quick Start
- Created "Option 1: Automated Setup" and "Option 2: Manual Setup" sections
- Reorganized Documentation section with setup links at top

### Setup Directory README
- Created comprehensive guide for setup directory
- Quick start instructions
- Service management commands
- Troubleshooting tips

## Database Credential Clarification

The old `cloud-init/gandalf-cloud-init.yaml` used incorrect credentials:
- ❌ Database: `gandalf` (wrong)
- ❌ User: `gandalf` (wrong)

The correct credentials (used by all current code):
- ✅ Database: `gandalf_db`
- ✅ User: `gandlf_user`
- ✅ Password: `PQnIQQkNTn90kKF4`

The new `setup/cloud-init.yaml` uses the correct credentials via `setup.sh`.

## Testing

All setup files have been:
- ✅ Moved to new location
- ✅ Updated with correct paths
- ✅ Synced to both `/var/www/projects/gandlf/` and `/opt/apps/gandlf/`
- ✅ Made executable where needed (`setup.sh`, `verify_setup.sh`)
- ✅ Documented in README files

## Next Steps

1. ✅ Commit changes to git
2. ✅ Push to remote repository
3. ✅ Update any external documentation referencing old paths
4. ✅ Test cloud-init deployment with new configuration

## File Sizes

```
setup/
├── README.md              3.0 KB  (NEW)
├── cloud-init.yaml        1.6 KB  (renamed from cloud-init-with-setup.yaml)
├── setup.sh               16  KB  (moved)
├── verify_setup.sh        8.2 KB  (moved)
├── SETUP_GUIDE.md         9.7 KB  (moved)
└── SETUP_README.md        3.8 KB  (moved)

Total: 42.3 KB of setup documentation and scripts
```

## Summary

This reorganization makes GANDALF easier to deploy and maintain by consolidating all setup logic into a dedicated directory. The setup process is now:

1. **One command**: `cd setup && sudo bash setup.sh "api-key"`
2. **One location**: All setup files in `setup/` directory
3. **One config**: Single cloud-init configuration file
4. **Clear docs**: Comprehensive guides in predictable location

The project is now more professional and easier to understand for new users.
