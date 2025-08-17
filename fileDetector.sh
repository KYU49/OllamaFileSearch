#!/bin/bash

# 参考: https://qiita.com/raux/items/88747277ee4119c22bb7

# 監視対象のディレクトリ（Sambaで共有されているディレクトリを想定）
WATCH_DIR = "/mnt/d/SharedDirectory/KnowledgeShare"

# ログファイルの出力先（ファイル追加の記録を保存）
LOG_FILE = "/var/log/filewatch_discord.log"

# DiscordのWebhook URL（事前にDiscord側で作成しておく）
WEBHOOK_URL="https://discord.com/api/webhooks/xxxxxxxx"  # 自分のWebhook URLに置き換える

# inotifywaitで対象ディレクトリを監視
# -m：常に監視し続ける（monitorモード）
# -e create：新しいファイルが作成されたイベントだけを監視
# --format "%w%f"：フルパス形式で出力（%w=ディレクトリ, %f=ファイル名）
inotifywait -m -e create --format "%w%f" "$WATCH_DIR" | while read NEWFILE
do
	# 現在時刻を取得（ログに記録するため）
	NOW=$(date "+%Y-%m-%d %H:%M:%S")

	# フルパスからファイル名だけを抽出
	FILENAME=$(basename "$NEWFILE")

	# ファイルの所有ユーザー名を取得（アップロード者として表示）
	FILEOWNER=$(stat -c %U "$NEWFILE")

	# ログファイルに記録（タイムスタンプ・ファイル名・ユーザー）
	echo "[$NOW] $FILENAME was created by $FILEOWNER" >> "$LOG_FILE"

	# DiscordへWebhook通知を送信
	# -s：進捗を表示しない
	# -H：HTTPヘッダでContent-Type指定（JSON）
	# -d：POSTするJSONデータ（改行は \\n で表現）
	curl -s -H "Content-Type: application/json" \
		 -X POST \
		 -d "{
			 \"content\": \"📥 新しいファイルがアップロードされました！\\n🗂️ ファイル名: \`$FILENAME\`\\n👤 アップロードユーザー: \`$FILEOWNER\`\"
		 }" \
		 "$WEBHOOK_URL"
done
