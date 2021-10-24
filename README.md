# Re.Next Hime

![鳴花 PROJECT](https://s3.akarinext.org/assets/*/HIME%20MIKOT%20(3).png)

<a href="https://codeclimate.com/github/yupix/NextHime/maintainability"><img src="https://api.codeclimate.com/v1/badges/4c0c6adf8a722fc70a36/maintainability" /></a> 
<a href="https://codeclimate.com/github/yupix/NextHime/test_coverage"><img src="https://api.codeclimate.com/v1/badges/4c0c6adf8a722fc70a36/test_coverage" /></a>
[![CodeFactor](https://www.codefactor.io/repository/github/yupix/nexthime/badge)](https://www.codefactor.io/repository/github/yupix/nexthime)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fyupix%2FNextHime.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fyupix%2FNextHime?ref=badge_shield)
[![Shields](https://img.shields.io/badge/Dev%20Python-3.9-ff7964.svg?style=for-the-badge)](https://img.shields.io/badge/Dev%20Python-3.9-ff7964.svg?style=for-the-badge)

## 概要

このProjectは [SSM](https://github.com/yupix/ssm) の後継作です。 また、このProjectは[MPL2.0](LICENSE)ライセンスのもと配布または使用できます

## 注意

このプロジェクトは現在 Discord.py の開発終了に伴う変更によりほとんどすべての機能を書き直しています。そのため多くの不具合などがこのブランチには存在します。
そのため、運営目的では使用しないでください。

## OS毎の依存関係

### ArchLinux | Zorin(Ubuntu)

- libpq-dev
- python3.9-dev # 3.9は使用しているバージョンによる
- postgresql
- git
- base-devel(Build Essential)

### Windows10 | Windows11

Windowsは依存関係を整えればWindows11での動作も確認していますが、これは初期段階での検証であり。 今後のアップデートでUnix専用のパッケージなどを追加することによって正常に動作しなくなる可能性があります。
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
![img.png](./src/assets/images/README/scopes.png)

INTENTSの設定
![img.png](./src/assets/images/README/intents.png)

## 開発者向け情報

- このプロジェクトをPycharmなどのエミュレート端末で動作させるとinputtimeoutが正常に動作しない可能性があります。**この問題は通常の非エミュレート端末では発生しません**

## ライセンス

[サードパーティーライセンス](./src/3rdlisence.md)

[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B18676%2Fgit%40github.com%3Ayupix%2FNextHime.git.svg?type=large)](https://app.fossa.com/projects/custom%2B18676%2Fgit%40github.com%3Ayupix%2FNextHime.git?ref=badge_large)
