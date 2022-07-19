# TradingBot for Kucoin

# install

```bash
sudo apt update && sudo apt upgrade -y

apt install python3-pip

pip3 install -r requirements.txt

python3 run_bot.py
```

# create systemd
 ```bash 

cat<<-EOF > /etc/systemd/system/run_bot.service
[Unit]
Description=run_bot daemon
After=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=1
User=root
WorkingDirectory=/root/TradingBot
ExecStart=python3 run_bot.py
SyslogIdentifier=run_bot
StartLimitInterval=0
LimitNOFILE=65536
LimitNPROC=65536

[Install]
WantedBy=multi-user.target
EOF
```

# Update Services
```bash
sudo systemctl daemon-reload

sudo chmod 755 /etc/systemd/system/run_bot.service

sudo systemctl enable run_bot.service

sudo service run_bot start 

sudo service run_bot status
```

# Check Logs
```bash
tail -f /var/log/syslog
```