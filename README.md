# Installation

## Ollama
* Install Ollama according to the [official website](https://ollama.com/download/linux).
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Only under proxy environment
* Terminal
```bash
sudo nano /etc/systemd/system/docker.service.d/proxy_setting.conf
```
* nano
```
[Service]
Environment="HTTP_PROXY=http://your-proxy-address:port"
Environment="HTTPS_PROXY=http://your-proxy-address:port"
```

## This program and the other dependencies

* Run the following command on terminal.
```bash
$filePath="/usr/local/lib/"

sudo cp OllamaFileSearch ${filePath}
sudo chmod 0755 ${filePath}OllamaFileSearch/fileWatcherHandler.sh
sudo systemctl deamon-reload
sudo systemctl enable ${filePath}OllamaFileSearch/fileWatcher.path
sudo systemctl start ${filePath}OllamaFileSearch/fileWatcher.path
echo "#!/bin/bash" > fileWatcherHandler.sh
echo "" >> fileWatcherHandler.sh
echo "${filePath}OllamaFileSearch/py/.venv/bin/python ${filePath}OllamaFileSearch/py/fileDetector.py" >> fileWatcherHandler.sh

sudo apt install inotify-tools
sudo apt install libpq-dev
wget -qO- https://astral.sh/uv/install.sh | sh

cd ${filePath}OllamaFileSearch/py
uv sync

touch .config/secret.yaml
touch .config/labelList.yaml
```

* Set user information of SQL Database to .yaml file like below.
```.config/secret.yaml
db_name: vectorized_files_db
db_user: user
db_pass: password
db_host: localhost
db_port: 5432
```

* Set file label to .yaml file like below
```.config/labelList.yaml
- Paper
- Experiment Manual
- Others
```

# Requirements