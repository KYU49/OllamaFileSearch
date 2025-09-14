import os
import time
import msvcrt

# fcntl 定数の模倣
LOCK_EX = 1
LOCK_NB = 2

class FileLock:
	"""
	Windows 用の簡易 fcntl.flock コンテキストマネージャ
	- LOCK_EX | LOCK_NB のみ対応
	"""
	def __init__(self, file, flags):
		if not hasattr(file, "fileno"):
			raise ValueError("file must be a file object")
		self.file = file
		self.fd = file.fileno()
		self.flags = flags

	def __enter__(self):
		# 排他ロック
		if self.flags & LOCK_EX:
			if self.flags & LOCK_NB:
				try:
					msvcrt.locking(self.fd, msvcrt.LK_NBLCK, 1)
				except OSError:
					raise BlockingIOError("Lock would block")
			else:
				while True:
					try:
						msvcrt.locking(self.fd, msvcrt.LK_LOCK, 1)
						break
					except OSError:
						time.sleep(0.01)
		else:
			raise NotImplementedError("Only LOCK_EX is implemented")
		return self.file

	def __exit__(self, exc_type, exc_val, exc_tb):
		try:
			msvcrt.locking(self.fd, msvcrt.LK_UNLCK, 1)
		except OSError:
			pass

# fcntl.flock 風の関数
def flock(file, flags):
	return FileLock(file, flags)