#!/bin/bash

# fileWatcher.serviceの方で`WorkingDirectory=/usr/local/lib/OllamaFileSearch/py`として設定しているため、uvなどはそのまま動かせる。
WATCH_DIR="/var/www/html/OllamaFileSearch/files"
# 無視したい一時ファイルパターン
IGNORE_REGEX='(\.sw[pox]$|~$|\.tmp$|\.goutputstream.*$|^\.#)'

inotifywait -m -r -e create -e close_write -e delete --format '%e %w%f' "$WATCH_DIR" | while read EVENT CHANGED_FILE
do
	# 一時ファイルは無視
	if [[ "$CHANGED_FILE" =~ $IGNORE_REGEX ]]; then
		continue
	fi
	
	case "$EVENT" in
		CREATE*|MOVED_TO*)
			ACTION="added"
			;;
		CLOSE_WRITE*|MODIFY*)
			ACTION="modified"
			;;
		DELETE*|MOVED_FROM*)
			ACTION="deleted"
			;;
		*)
			ACTION="unknown"
			;;
	esac

	# Python スクリプトに変更の種類を渡す
	.venv/bin/python fileRegisterEndpoint.py "$CHANGED_FILE" "$ACTION"
done