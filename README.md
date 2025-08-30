# Abstract


# Attention
This program is intended for use by a limited number of users, typically from a few to around a dozen, and simultaneous usage is expected to be rare. It is also designed to be run on a personal computer that is used for other purposes, without running the program as a background service. Therefore, if it is to be used on a public server or similar environment, optimization will be necessary.

# Installation
Install not only this program but also the tools required to run the LLM and Python, and the tools for file monitoring.

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

## Other Dependencies
* Install inotify (monitoring filesystem events) and uv (Python package manager), following the below commands.
```bash
sudo apt install inotify-tools
wget -qO- https://astral.sh/uv/install.sh | sh
```
* Restart the terminal to enable uv.

## This program
* Navigate to any desired directory, then execute the following command. 
```bash
filePath="/usr/local/lib/"

git repo clone https://github.com/KYU49/OllamaFileSearch
cd OllamaFileSearch
mkdir ./html/OllamaFileSearch/files
mkdir ./html/OllamaFileSearch/.config
touch ./html/OllamaFileSearch/.config/labelList.yaml

sudo cp -r ./html/OllamaFileSearch /var/www/html/
sudo cp -r OllamaFileSearch ${filePath}

sudo chown -R root:www-data ${filePath}OllamaFileSearch/py
sudo chmod -R 750 ${filePath}OllamaFileSearch/py
sudo chmod +x ${filePath}OllamaFileSearch/py/*.py

cd ${filePath}OllamaFileSearch/py
uv sync

sudo systemctl daemon-reload
sudo systemctl enable ${filePath}OllamaFileSearch/fileWatcher.service
sudo systemctl start fileWatcher.service

```

