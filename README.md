# Radius ChatOps Bot

Discord-based ChatOps system for managing and monitoring FreeRADIUS users using MariaDB and daloRADIUS integration.

## Overview

The system integrates:

- FreeRADIUS
- MariaDB
- daloRADIUS
- Discord Bot (Python)

to provide centralized authentication management and monitoring through Discord slash commands.

---

# Architecture

```text
Discord User
      │
      ▼
Discord Bot (Python)
      │
      ▼
MariaDB (radius)
      │
 ┌────┴────┐
 ▼         ▼
FreeRADIUS daloRADIUS
      │
      ▼
MikroTik NAS
```

## Features

### User Management

- Add user
- Delete user
- Change password
- Assign profile/group

### Monitoring

- Online user monitoring
- NAS monitoring
- User statistics
- Session history

### Security

- Discord role restriction
- Slash command authorization
- MariaDB user isolation
- Audit logging

## Technology Stack

| Component              | Technology     |
| ---------------------- | -------------- |
| Backend Authentication | FreeRADIUS     |
| Database               | MariaDB        |
| Web Dashboard          | daloRADIUS     |
| ChatOps Bot            | Python         |
| Discord Library        | disnake        |
| Database Driver        | aiomysql       |
| Containerization       | Docker         |
| Orchestration          | Docker Compose |

## Project Structure

```
discordbot/
│
├── main.py
├── requirements.txt
├── Dockerfile
├── .env
├── .env.example
│
├── cogs/
├── database/
├── services/
├── utils/
│
└── logs/
```

## Development Environment

Development is performed using:

- Windows 11
- CachyOS Linux
- Docker
- Visual Studio Code

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/radius-chatops.git
```

### 2. Create Virtual Environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create `.env`

```
DISCORD_TOKEN=

DB_HOST=
DB_PORT=3306
DB_USER=
DB_PASSWORD=
DB_NAME=radius
```

### Run Bot

```bash
python main.py
```

## Docker Deployment

### Build Image

```bash
docker build -t radius-chatops .
```

### Run Container

```bash
docker run -d radius-chatops
```

## Database Tables Used

| Table         | Purpose                      |
| ------------- | ---------------------------- |
| radcheck      | User authentication          |
| radacct       | Accounting and monitoring    |
| nas           | NAS/router management        |
| radusergroup  | User group assignment        |
| radgroupreply | Profile and bandwidth policy |

## Example Commands

### General

- `/ping`
- `/users`

### User Management

- `/adduser`
- `/deluser`
- `/changepass`

### Monitoring

- `/online`
- `/userstats`
- `/naslist`

## Security Notes

- Do not expose MariaDB publicly in production
- Use private Docker network
- Never upload `.env`
- Use dedicated MariaDB user for bot access
- Restrict Discord commands using roles
