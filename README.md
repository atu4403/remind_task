# remind_task ![pytest](https://github.com/atu4403/remind_task/workflows/pytest/badge.svg)

macosで通知を繰り返すCLIアプリケーション

## Install

```shell
> pip install remind_task
```


## Usage

```shell
> remindtask run
```

通知はユーザー設定によりバナーもしくは通知パネルになるが設定方法はシステム環境設定 -> 通知と移動してアプリケーション一覧からスクリプトエディタを選択する。
**停止する場合は`ctrl + c`などでプロセスを止めてください**


## Commands

### run
---
通知を行う。optionがない場合は1回だけ行う。

#### --munute

Type: `int`

通知を繰り返す間隔を分単位で設定する


```shell
> remindtask run --minute 60 # 60分ごとに通知を繰り返す
```

### edit
---
設定ファイルをエディタで開く。optionがない場合は規定のエディタで開く

#### --app

Type: `str`

エディタを指定する。


```shell
> remindtask edit --app vim
```

### init
---
設定ファイルを作成する。既に存在するなら何もしない

#### --force

Type: `bool`

設定ファイルがあっても強制再作成する

#### --silent

Type: `bool`

ログを出力しない


```shell
> remindtask init --force --silent
```



## License

MIT © [atu4403](https://github.com/atu4403)
