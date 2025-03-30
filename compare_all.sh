#!/bin/bash

MAPPING_FILE="host_config_map.csv"

while IFS=',' read -r HOST LOCAL_CONFIG; do
    echo "=== $HOST の設定を取得中 ==="
    ./get_config.expect "$HOST"

    TEMP_CONFIG="/tmp/${HOST}_running-config.tmp"

    if [ ! -f "$LOCAL_CONFIG" ]; then
        echo "[警告] ローカル比較対象がありません: $LOCAL_CONFIG"
        continue
    fi

    echo "=== 差分（$HOST） ==="
    diff -u "$LOCAL_CONFIG" "$TEMP_CONFIG"
    echo ""

done < "$MAPPING_FILE"
