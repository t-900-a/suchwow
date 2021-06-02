MIRROR OF https://git.wownero.com/lza_menace/suchwow

DO NOT PLAN TO MERGE ANY FURTHER COMMITS

# SuchWow!

TBD

## Setup

```
# initialize new wallet and retain seed
docker run --rm -it --name suchwow-wallet-init \
  -v $(pwd)/data:/root \
  lalanza808/wownero \
  wownero-wallet-cli \
    --daemon-address https://node.suchwow.xyz:443 \
    --generate-new-wallet /root/wow \
    --password zzzzzz \

# setup rpc process
docker run --rm -d --name suchwow-wallet \
  -v $(pwd)/data:/root \
  -p 8888:8888 \
  lalanza808/wownero \
  wownero-wallet-rpc \
    --daemon-address https://node.suchwow.xyz:443 \
    --wallet-file /root/wow \
    --password zzzzzz \
    --rpc-bind-port 8888 \
    --rpc-bind-ip 0.0.0.0 \
    --confirm-external-bind \
    --rpc-login xxxx:yyyy \
    --log-file /root/rpc.log

# install python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# setup secrets in config file outside of git
cp suchwow/config.example.py suchwow/config.py
vim !$
```
