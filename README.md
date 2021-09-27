# vrf-initializer

VRFを作成, interfaceへの割当を行うスクリプト．
daemon modeを有効にすると常時監視する． 



```
usage: main.py [-h] [-d] [-t TIMEOUT] [-f FILE]

optional arguments:
  -h, --help            show this help message and exit
  -d, --daemon          Daemon mode. Exec eternally default: False
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout seconds is enabled only in daemon mode. (Otherwise, it is ignored). default: 10
  -f FILE, --file FILE  Config file. default: ./config.json
```

## ユースケース
`/etc/networkd-dispatcher/routable.d/` が使えない場合に効果的．
主にnetworkdでhook出来ないInterfaceにVRFをつけたい場合など．


## 使い方
`sample/vrf-initializer.service` を参照．

作ったVRF消したい時は`delete.py`を実行するべし．