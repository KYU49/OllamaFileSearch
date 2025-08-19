# Installation
```bash
filePath="/usr/local/bin/"

sudo cp OllamaFileSearch ${filePath}
sudo chmod 0755 ${filePath}OllamaFileSearch/py/fileDetector.py
sudo cp fileDetector.service /etc/systemd/system/fileDetector.service
sudo systemctl enable fileDetector.service

wget -qO- https://astral.sh/uv/install.sh | sh
cd ${filePath}OllamaFileSearch/py
uv sync
```

# Requirements