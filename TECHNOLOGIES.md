# GANDALF Technologies

**Last Updated:** 2026-01-19 (GANDLF-0005: Multi-agent system)

## Stack Overview

- **Primary Language:** Python 3.x
- **Framework:** Flask 3.0.2
- **Database:** MySQL 8.0
- **VM Provider:** Multipass (Ubuntu cloud-init)
- **Web Server:** Gunicorn (production WSGI server)

## Core Technologies

### Backend Framework
- **Flask** (3.0.2) - Lightweight Python web framework
  - Purpose: REST API server
  - Endpoints: Intent submission, CTC retrieval, health checks

### GANDALF Modules

#### AI Agent Communication (GANDLF-0004)
- **AgentClient** - HTTP client for AI agent communication
- **CTCOrchestrator** - Workflow orchestration (analyze → detect → clarify OR generate)

#### Multi-Agent System (GANDLF-0005)
- **ModelRouter** - Intelligent model selection for cost optimization
- **AIAgentService** - HTTP service with multi-model Claude support
- **Multi-Model Strategy:**
  - **Haiku**: Fast tasks (classification, validation)
  - **Sonnet**: Balanced tasks (analysis, gap detection)
  - **Opus**: Complex tasks (CTC generation)

### Database
- **MySQL** (8.0) - Relational database
  - Host: localhost
  - Database: `gandalf`
  - User: `gandalf`
  - Character set: utf8mb4_unicode_ci
  - Connector: mysql-connector-python 8.3.0

### Python Libraries

#### API & Web
- `flask==3.0.2` - Web framework
- `flask-cors==4.0.0` - Cross-Origin Resource Sharing support
- `gunicorn==21.2.0` - Production WSGI HTTP server

#### Data Handling
- `pydantic==2.6.1` - Data validation and parsing
- `orjson==3.9.15` - Fast JSON serialization

#### Environment & Configuration
- `python-dotenv==1.0.1` - Environment variable management

#### HTTP & Networking
- `httpx==0.26.0` - HTTP client library

#### Logging
- `structlog==24.1.0` - Structured logging

#### Database
- `mysql-connector-python==8.3.0` - MySQL driver

## Infrastructure

### VM Provisioning
- **Multipass** - Ubuntu VM manager
- **cloud-init** - VM initialization and configuration
  - Config file: `cloud-init/gandalf-cloud-init.yaml`

### Process Management
- **systemd** - Service management
  - Service: `gandalf-api.service`
  - Auto-start on boot
  - Automatic restart on failure

### Python Environment
- **venv** - Virtual environment
  - Location: `/opt/gandalf/venv`
  - Isolated dependencies

## API Specifications

### REST API
- **Protocol:** HTTP
- **Port:** 5000
- **Format:** JSON
- **CORS:** Enabled for all origins

### Authentication
- **Current:** None (TODO)
- **Planned:** API key or JWT

## Environment Variables

Required environment variables:

```bash
# AI Agent Configuration
GANDALF_AGENT_ENDPOINT=http://localhost:8080/agent  # AI agent service URL

# Flask Configuration
FLASK_ENV=production          # production|development
FLASK_PORT=5000              # API port
FLASK_DEBUG=False            # Debug mode

# Database (stored in /etc/gandalf/db.env)
DB_NAME=gandalf
DB_USER=gandalf
DB_HOST=localhost
DB_PORT=3306
DB_PASS=<generated>          # Auto-generated during setup
```

## File Locations

### Application
- Application root: `/opt/apps/gandlf/`
- API code: `/opt/apps/gandlf/api/`
- AI Agent module: `/opt/apps/gandlf/gandalf_agent/`
- AI Agent prompts: `/opt/apps/gandlf/ai_agent_prompts/`
- Scripts: `/opt/apps/gandlf/scripts/`
- Virtual env: `/opt/gandalf/venv/`

### Configuration
- Database env: `/etc/gandalf/db.env`
- Systemd service: `/etc/systemd/system/gandalf-api.service`

### Logs
- Access log: `/var/log/gandalf/access.log`
- Error log: `/var/log/gandalf/error.log`
- Provision log: `/var/log/gandalf-provision.log`
- Verification log: `/var/log/gandalf-verify.log`

## External Services

### AI Agent Service (Multi-Model - GANDLF-0005)
- **Location:** GANDALF VM (port 8080)
- **Purpose:** Performs intent analysis, gap detection, CTC generation
- **Communication:** HTTP/JSON
- **LLM Provider:** Anthropic Claude (Haiku, Sonnet, Opus)
- **Implementation:** `/opt/apps/gandlf/multi-agent/ai_agent_service.py`
- **Model Selection:** Automatic via ModelRouter based on task complexity
- **Cost Optimization:** 30-40% savings vs single-model approach

### Planned Integrations
- **Monitoring** - TBD (Prometheus, Datadog, etc.)

## Development Tools

### Package Management
- **pip** - Python package installer
- **requirements.txt** - Dependency specification

### Version Control
- **Git** - Source control
- **GitHub** - Repository hosting (assumed)

## Production Deployment

### WSGI Server
- **Gunicorn** configuration:
  - Workers: 4
  - Bind: 0.0.0.0:5000
  - Timeout: 120s
  - Graceful timeout: 30s

### Security
- **systemd security features:**
  - NoNewPrivileges=true
  - PrivateTmp=true

## Data Schema

### CTC (Compiled Task Contract)
See `CompiledOutputSchema.md` for complete schema.

Key structure:
- gandalf_version
- ctc (task, context, definition_of_done, constraints, deliverables)
- clarifications
- telemetry

## Future Technologies (Roadmap)

### Planned Additions
- Redis - Caching layer
- Celery - Asynchronous task queue
- pytest - Testing framework
- Docker - Containerization (alternative to Multipass)
- nginx - Reverse proxy
- SSL/TLS - HTTPS support

## Version Information

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.x | System default |
| Flask | 3.0.2 | Latest stable |
| MySQL | 8.0 | Latest LTS |
| Gunicorn | 21.2.0 | Production ready |
| Ubuntu | 22.04+ | Via Multipass |

## Notes

- All SQL queries must use prepared statements
- All API inputs are validated
- All outputs are JSON formatted
- CORS is enabled for development (should be restricted in production)
- Database password is auto-generated during VM setup
- Service runs as root (TODO: create dedicated user)

## Support & Documentation

- Flask docs: https://flask.palletsprojects.com/
- Gunicorn docs: https://docs.gunicorn.org/
- MySQL docs: https://dev.mysql.com/doc/
- Multipass docs: https://multipass.run/docs
