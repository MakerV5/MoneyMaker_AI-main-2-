# MoneyMaker AI

This repository contains a minimal skeleton for a trading assistant with a Telegram bot and a web dashboard.

## Quick Start

1. Install dependencies:
   ```bash
   pip install flask python-telegram-bot==20.3
   ```
2. Set your Telegram bot token in `start_all.py`.
3. Run the application:
   ```bash
   python start_all.py
   ```
4. Access the dashboard at `http://localhost:5000`.

## Service Setup

A sample systemd service file is provided in `moneymaker.service`. Update the `ExecStart` path and copy the file to `/etc/systemd/system/`. Then run:

```bash
sudo systemctl enable moneymaker.service
sudo systemctl start moneymaker.service
```

Logs will be written to `/var/log/moneymaker.log`.
