# MoneyMaker AI

A small demo of an automated trading assistant including:

- FastAPI dashboard with WebSocket stream
- Telegram bot interaction
- Simple ML based trading strategy
- systemd service example

## Quick Start

1. Install Python dependencies

```bash
pip install -r requirements.txt
```

2. Create a `.env` file (see provided sample) with your Telegram token and dashboard users.
3. Run the application

```bash
python start_all.py
```

Open the dashboard on `http://localhost:5000` and login with your credentials.

## Service Setup

Copy `moneymaker.service` to `/etc/systemd/system/` and adjust the `WorkingDirectory` if necessary. Enable and start the service:

```bash
sudo systemctl enable moneymaker.service
sudo systemctl start moneymaker.service
```

Logs will appear in `/var/log/moneymaker.log` and rotated daily as configured in `config/logrotate.conf`.
