# NetConfig Diff Checker

このツールは、Ciscoルータ/スイッチの running-config を SSH + Expect を使って自動取得し、
ローカルに保存された設定ファイルと比較するためのものです。

## 使い方（簡易）

1. `get_config.expect` を実行すると、対話形式でユーザー名/パスワードを入力できます。
2. `host_config_map.csv` に、ホスト名とローカルファイルの対応を記述。
3. `compare_all.sh` を実行すると、設定を取得＆差分比較します。

## 必要条件

- expect
- ssh（~/.ssh/config にホストが登録されていること）
