## Env Preparing

Install `Python 3.11`

```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.11
```

Setup `venv`:

```bash
sudo apt install python3.11-venv
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

Install requirements:

```bash
pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt --upgrade
```

## Env Preparing in MacOS

Install `Python 3.11`

```bash
brew update
brew install python@3.11
```

Setup `venv`:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt --upgrade
```

