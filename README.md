# Installation
```bash
$filePath="/usr/local/bin/"

sudo cp OllamaFileSearch ${filePath}
sudo chmod 0755 ${filePath}OllamaFileSearch/fileWatcherHandler.sh
sudo systemctl deamon-reload
sudo systemctl enable ${filePath}OllamaFileSearch/fileWatcher.path
sudo systemctl start ${filePath}OllamaFileSearch/fileWatcher.path
echo "#!/bin/bash" > fileWatcherHandler.sh
echo "" >> fileWatcherHandler.sh
echo "${filePath}OllamaFileSearch/py/.venv/bin/python ${filePath}OllamaFileSearch/py/fileDetector.py" >> fileWatcherHandler.sh
wget -qO- https://astral.sh/uv/install.sh | sh
cd ${filePath}OllamaFileSearch/py
uv sync
```

# Requirements