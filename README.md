# Installation

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

sudo apt install libpq-dev
wget -qO- https://astral.sh/uv/install.sh | sh

cd ${filePath}OllamaFileSearch/py
uv sync

mkdir .config
touch .config/secret.yaml
```

* Set user information of SQL Database to .yaml file like below.
```.config/secret.yaml
db_name: vectorized_files_db
db_user: user
db_pass: password
db_host: localhost
db_port: 5432
```

# Requirements