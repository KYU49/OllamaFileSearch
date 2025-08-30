# Installation

## Ollama
* Install Ollama according to the [official website](https://ollama.com/download/linux).
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Only under proxy environment
* Terminal
```bash
sudo systemctl edit ollama.service
```
* Using nano, insert the below text under the comment, `### Anythin between here and the comment below will become the contents of the drop-in file`.
```
[Service]
Environment="HTTP_PROXY=http://your-proxy-address:port"
Environment="HTTPS_PROXY=http://your-proxy-address:port"
```

## This program and the other dependencies
* Navigate to the desired directory, then execute the following command. 
```bash
filePath="/usr/local/lib/"

git repo clone https://github.com/KYU49/OllamaFileSearch
cd OllamaFileSearch
mkdir ./html/OllamaFileSearch/.config
touch ./html/OllamaFileSearch/.config/labelList.yaml

cp -r ./html/OllamaFileSearch /var/www/html/
cp -r OllamaFileSearch ${filePath}

sudo chown -R root:www-data ${filePath}OllamaFileSearch/py
sudo chmod -R 750 ${filePath}OllamaFileSearch/py
sudo chmod +x ${filePath}OllamaFileSearch/py/*.py

sudo apt install inotify-tools
sudo apt install libpq-dev
wget -qO- https://astral.sh/uv/install.sh | sh

cd ${filePath}OllamaFileSearch/py
uv sync

sudo systemctl daemon-reload
sudo systemctl enable ${filePath}OllamaFileSearch/fileWatcher.service
sudo systemctl start fileWatcher.service

```

