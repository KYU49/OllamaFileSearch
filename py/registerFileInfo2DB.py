#from vectorize import vectorize
from pathlib import Path
# import pyinotify
from markitdown import MarkItDown
import chardet


#class Handler(pyinotify.ProcessEvent):
#	# 参考: https://zenn.dev/lsii/scraps/58b5901c632e62
#	# ファイル追加 (SQLへの追加)
#	def process_IN_CREATE(self, event):
#		pass
#
#	# ファイル削除 (SQLからの削除)
#	def process_IN_DELETE(self, event):
#		pass
#
#	# それ以外 (SQLの情報編集)
#	def process_default(self, event):
#		pass

def getFileText(filePath: str):
	# 特定のファイル形式か判定
	p = Path(filePath)
	ext = p.suffix.lower()

	match ext:
		case ".txt" | ".md":
			text = ""
			# 文字コードの判定
			with open(filePath, "rb") as file:
				raw_data = file.read()
				result = chardet.detect(raw_data)
				encoding = result["encoding"]
			# 判定した文字コードで開く
			with open(filePath, "r", encoding=encoding) as file:
				text = file.read()
			return text
		case ".docx" | ".xlsx" | ".pptx" | ".pdf":
			md = MarkItDown(enable_plugins=False)
			result = md.convert(filePath)
			return result.text_content
	return ""


def detect(file = ""):
	# 内部テキストの変更がなければ、フラグなどのみ編集

	# ファイル内容をテキストとして取得
	text = getFileText(file)
	
	# ファイル内容を登録するために、Vectorを取得
	#vector = vectorize(text)
	
	# 変更があったファイルについて、変更の種類によって場合分けし、変更をDBに反映するSQLを生成

	# SQLに反映

def main():
	detect()
#	wm = pyinotify.WatchManager()
#	mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY
#	handler = EventHandler()
#	notifier = pyinotify.Notifier(wm, handler)
#
#
#	# 監視対象のディレクトリ
#	watch_target_dirs = [
#		'/var/www/html',
#		'/etc/httpd'
#		]
#
#	for target_dir in watch_target_dirs:
#		wdd = wm.add_watch(target_dir, mask, rec=True)
#
#	notifier.loop()

if __name__ == "__main__":
	main()
