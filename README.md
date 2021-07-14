# Next Hime Project

![YX SERIES](https://s3.akarinext.org/misskey/*/29af8bc0-54d3-4ac1-801c-aef2990855cc.png)


## 概要

このProjectは [SSM](https://github.com/yupix/ssm) の後継作です。
また、このProjectは[AGPL](LICENSE)ライセンスのもと配布または使用できます

## OS毎の依存関係

### ArchLinux | Neon(Ubuntu)

- libpq-dev 
- python-dev 
- libxml2-dev 
- libxslt1-dev
- libldap2-dev
- libsasl2-dev 
- libffi-dev
- postgresql
- git
- base-devel

### Windows10 | Windows11

Windowsは依存関係を整えればWindows11での動作も確認していますが、これは初期段階での検証であり。
今後のアップデートでUnix専用のパッケージなどを追加することによって正常に動作しなくなる可能性があります。
また、これらは過去の断片的な記憶から書いている依存関係であり、実際は他の依存関係も必要かもしれません。

- postgresql
- git

## セットアップ方法

```shell
git clone https://github.com/yupix/NextHime.git  # プロジェクトをclone 
cd NextHime  # cloneしたプロジェクトに移動
python3 -m virtualenv .venv  # 仮想環境の作成

# 仮想環境の有効化
  # Linuxの場合
  source ./.venv/bin/activate
  # Windowsの場合
  .venv\Scripts\activate.bat

pip install -r requirements.txt  # 依存関係のインストール

python3 run.py  # 実行 
```

### Discord BOTの設定
BOTを招待する際のSCOPES
![img.png](assets/images/README/scopes.png)

INTENTSの設定
![img.png](./assets/images/README/intents.png)
