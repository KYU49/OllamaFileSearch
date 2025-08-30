# Abstract


# Attention
**Linux Only** not for Windows.  
This program is intended for use by a limited number of users, typically from a few to around a dozen, and simultaneous usage is expected to be rare. It is also designed to be run on a personal computer that is used for other purposes, without running the program as a background service. Therefore, if it is to be used on a public server or similar environment, optimization will be necessary.

# Installation
Install not only this program but also the tools required to run the LLM and Python, and the tools for file monitoring.

## NVIDIA Driver
* Install [cuda-toolkit, cuda-drivers](https://developer.nvidia.com/cuda-12-9-0-download-archive?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=24.04&target_type=deb_local)

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
curl -LsSf https://astral.sh/uv/install.sh | sudo env UV_INSTALL_DIR="/opt/uv" sh
```
* Restart the terminal to enable uv.

## This program
* Navigate to any desired directory, then execute the following command. 
```bash
filePath="/usr/local/lib/"
git clone https://github.com/KYU49/OllamaFileSearch
cd OllamaFileSearch
mkdir OllamaFileSearch/py/chromadb
mkdir ./html/OllamaFileSearch/files
mkdir ./html/OllamaFileSearch/.config
touch ./html/OllamaFileSearch/.config/labelList.yaml

sudo cp -r ./html/OllamaFileSearch /var/www/html/
sudo cp -r OllamaFileSearch ${filePath}

cd cd ${filePath}OllamaFileSearch/py
sudo -u www-data /opt/uv/uv sync
sudo -u www-data /opt/uv/uv run BertModelInstaller.py


sudo chown -R root:www-data ${filePath}OllamaFileSearch/py/chromadb
sudo chmod -R 775 ${filePath}OllamaFileSearch/py/chromadb
sudo chown -R root:www-data ${filePath}OllamaFileSearch/py
sudo chmod -R 750 ${filePath}OllamaFileSearch/py
sudo chmod +x ${filePath}OllamaFileSearch/py/*.py

sudo systemctl daemon-reload
sudo systemctl enable ${filePath}OllamaFileSearch/fileWatcher.service
sudo systemctl start fileWatcher.service

```

# Setting File Storage Directory

