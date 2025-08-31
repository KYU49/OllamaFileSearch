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
git clone https://github.com/KYU49/OllamaFileSearch
cd OllamaFileSearch
echo -e "- マニュアル\n- 未分類" >> html/OllamaFileSearch/.config/labelList.yaml

sudo cp -r ./html/OllamaFileSearch /var/www/html/
sudo mkdir /var/www/myapp
sudo cp -r ./myapp/OllamaFileSearch /var/www/myapp/
sudo cp -r OllamaFileSearch /usr/local/lib/

cd /var/www
sudo mkdir .cache
sudo chown -R root:www-data .cache
sudo chmod -R 770 .cache
sudo mkdir .local
sudo chown -R root:www-data .local
sudo chmod -R 770 .local
sudo chmod -R 775 html/OllamaFileSearch/files
#TODO SharedDirectoryにすること！！！

cd myapp/OllamaFileSearch

sudo chown -R root:www-data ./
sudo chmod -R 755 ./
sudo chmod -R 770 .cache
sudo chown -R root:www-data chromadb
sudo chmod -R 770 chromadb
sudo mkdir .venv
sudo chmod -R 770 .venv
sudo -u www-data /opt/uv/uv sync
sudo -u www-data /opt/uv/uv run BertModelInstaller.py

sudo chmod u+x /usr/local/lib/OllamaFileSearch/fileWatcherHandler.sh
sudo systemctl daemon-reload
sudo systemctl enable /usr/local/lib/OllamaFileSearch/fileWatcher.service
sudo systemctl start fileWatcher.service

```

# Uninstall
```bash
sudo systemctl disable fileWatcher.service
sudo rm /var/www/myapp/OllamaFileSearch /var/www/html/OllamaFileSearch /usr/local/lib/OllamaFileSearch -r
```


# Setting File Storage Directory

