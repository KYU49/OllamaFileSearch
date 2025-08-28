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

* Run the following command on terminal in the OllamaFileSearch directory (`cd OllamaFileSearch`).
```bash
$filePath="/usr/local/lib/"

mkdir html/OllamaFileSearch/.config
touch html/OllamaFileSearch/.config/labelList.yaml

cp html/OllamaFileSearch /var/www/http/

cp OllamaFileSearch ${filePath}
sudo chmod 0755 ${filePath}OllamaFileSearch/fileWatcherHandler.sh

sudo apt install inotify-tools
sudo apt install libpq-dev
wget -qO- https://astral.sh/uv/install.sh | sh

cd ${filePath}OllamaFileSearch/py
uv sync

sudo systemctl deamon-reload
sudo systemctl enable ${filePath}OllamaFileSearch/fileWatcher.service
sudo systemctl start ${filePath}OllamaFileSearch/fileWatcher.service

```

