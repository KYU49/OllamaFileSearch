# Installation
```bash
filePath="/usr/local/bin/"

sudo cp OllamaFileSearch ${filePath}
sudo chmod 0755 ${filePath}OllamaFileSearch/fileWatcherHandler.sh
sudo systemctl deamon-reload
sudo systemctl enable ${filePath}OllamaFileSearch/fileWatcher.path
sudo systemctl start ${filePath}OllamaFileSearch/fileWatcher.path

wget -qO- https://astral.sh/uv/install.sh | sh
cd ${filePath}OllamaFileSearch/py
uv sync
```

# Requirements