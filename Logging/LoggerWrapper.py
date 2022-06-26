from logging import basicConfig, getLogger, Formatter, StreamHandler, FileHandler, Logger
# from logging import DEBUG
from logging import INFO
# from logging import WARNING
# from logging import ERROR
# from logging import CRITICAL
from logging.handlers import RotatingFileHandler
# import logging
import sys
import os
from datetime import date, datetime, timedelta


class LoggerWrapper(object):
	# ログフォーマットデフォルト値
	__default_formatter_str: str = "%(asctime)s: %(levelname)s: %(filename)s, L%(lineno)d (%(funcName)s()) %(message)s"

	# ログファイル保存先関連デフォルト値
	__default_logfile_dir: str = "log"
	__default_logfile_filename_header: str = datetime.now().strftime("%Y%m%d")
	__default_logfile_filename_footer: str = ""
	__default_logfile_full_filename: str = __default_logfile_filename_header + ".log"
	__default_logfile_path: str = __default_logfile_dir + "\\" + __default_logfile_full_filename

	# コンストラクタ
	def __init__(
			self,
			module_name: str = "Default Logger",
			logfile_dir: str = __default_logfile_dir,
			logfile_filename_header: str = __default_logfile_filename_header,
			logfile_filename_footer: str = __default_logfile_filename_footer,
			logfile_filename_extension: str = ".log",
			encoding: str = "utf-8",
			loglevel: int = INFO,
			console_output: bool = False,
			log_rotate: bool = True,
			max_bytes: int = 1000000,
			backup_count: int = 10
	):
		# モジュール個別のロガーを生成
		self.__logger: Logger | None = self.__get_new_logger(
			name=module_name,
			logfile_dir=logfile_dir,
			logfile_filename_header=logfile_filename_header,
			logfile_filename_footer=logfile_filename_footer,
			logfile_filename_extension=logfile_filename_extension,
			encoding=encoding,
			loglevel=loglevel,
			console_output=console_output,
			log_rotate=log_rotate,
			max_bytes=max_bytes,
			backup_count=backup_count
		)

	# デストラクタ
	def __del__(self):
		for handler in self.__logger.handlers:
			self.__logger.removeHandler(handler)

	@classmethod
	# ロガー生成
	def __get_new_logger(
			cls,
			name: str = __name__,
			formatter_str: str = __default_formatter_str,
			logfile_dir: str = __default_logfile_dir,
			logfile_filename_header: str = __default_logfile_filename_header,
			logfile_filename_footer: str = __default_logfile_filename_footer,
			logfile_filename_extension: str = ".log",
			encoding: str = "utf-8",
			loglevel: int = INFO,
			console_output: bool = False,
			log_rotate: bool = True,
			max_bytes: int = 1000000,
			backup_count: int = 10
	) -> Logger | None:
		_logger: Logger | None = None
		try:
			# generate logger
			_logger: Logger = getLogger(name)

			# formatter
			_formatter: Formatter = Formatter(formatter_str)

			# StreamHandler
			if console_output:
				# create StreamHandler
				_stream_handler: StreamHandler = StreamHandler()
				# set StreamHandler to logger
				_stream_handler.setFormatter(_formatter)
				_logger.addHandler(_stream_handler)

			# ログ保存先
			_logfile_path = logfile_dir + "\\" + logfile_filename_header + logfile_filename_footer + logfile_filename_extension

			_exe_directory_path_with_slash: str = os.path.dirname(sys.argv[0])
			_exe_directory_path: str = _exe_directory_path_with_slash.replace('/', '\\')
			_logfile_path = _exe_directory_path + "\\" + _logfile_path
			_log_directory_path = os.path.dirname(_logfile_path)

			# ログ保存先のディレクトリがなければ作成
			cls.__make_directories(directory_path=_log_directory_path)

			# ファイル出力設定
			if _logger is not None:
				# FileHandler
				try:
					# ログファイルのローテーション
					if log_rotate:
						_file_handler = RotatingFileHandler(
							filename=_logfile_path,
							encoding=encoding,
							maxBytes=max_bytes,
							backupCount=backup_count
						)
					else:
						_file_handler = FileHandler(
							filename=_logfile_path,
							encoding=encoding
						)
					_file_handler.setFormatter(_formatter)
					_logger.addHandler(_file_handler)
					basicConfig(level=loglevel)
					_logger.debug("Logger初期化完了")
				except Exception as ex:
					_logger.exception(ex)
		except:
			import traceback
			traceback.print_exc()
			_logger = None

		return _logger

	# ラッパー関数
	def debug(self, msg: str, *args, **kwargs) -> bool:
		if self.__logger is not None:
			# ロガーが初期化されている場合
			self.__logger.debug(msg=msg, *args, **kwargs)
			return True
		else:
			print("No logger is found. : " + msg)
			return False

	def info(self, msg: str, *args, **kwargs) -> bool:
		if self.__logger is not None:
			self.__logger.info(msg=msg, *args, **kwargs)
			return True
		else:
			print("No logger is found. : " + msg)
			return False

	def warning(self, msg: str, *args, **kwargs) -> bool:
		if self.__logger is not None:
			self.__logger.warning(msg=msg, *args, **kwargs)
			return True
		else:
			print("No logger is found. : " + msg)
			return False

	def error(self, msg: str, *args, **kwargs) -> bool:
		if self.__logger is not None:
			self.__logger.error(msg=msg, *args, **kwargs)
			return True
		else:
			print("No logger is found. : " + msg)
			return False

	def critical(self, msg: str, *args, **kwargs) -> bool:
		if self.__logger is not None:
			self.__logger.critical(msg=msg, *args, **kwargs)
			return True
		else:
			print("No logger is found. : " + msg)
			return False

	def exception(self, msg: str, *args, exc_info: bool = True, **kwargs) -> bool:
		if self.__logger is not None:
			self.__logger.exception(msg=msg, *args, exc_info=exc_info, **kwargs)
			return True
		else:
			print("No logger is found. : " + msg)
			return False

	# ディレクトリが無ければ作成
	@classmethod
	def __make_directories(cls, directory_path: str, output_trace: bool = True) -> bool:
		# ディレクトリ存在チェック
		if os.path.exists(directory_path):
			return True

		# ディレクトリ生成
		try:
			os.makedirs(directory_path)
			# print("ディレクトリ作成完了 : " + directory_path)
		except Exception as ex:
			if output_trace:
				import traceback
				traceback.print_exc()
			return False

		# ディレクトリ生成に成功
		return True

	# 指定した日付以前の古いファイルを移動
	def flush_old_files_by_date(self, directory_path: str, delete_date_to: date, output_trace: bool = True):
		# 古いファイルをリストアップ
		_old_filename_list = self.__list_up_old_files_by_date(directory_path=directory_path, delete_date_to=delete_date_to)

		# 古いファイルを移動する用のディレクトリ作成
		_trash_directory_name = "trash"
		_trash_directory_path = directory_path + "\\" + _trash_directory_name
		if not self.__make_directories(_trash_directory_path):
			return

		for _old_filename in _old_filename_list:
			_source_path = directory_path + "\\" + _old_filename
			_destination_path = _trash_directory_path + "\\" + _old_filename
			# ファイルアクセス可能か(開かれていないか)確認
			if not self.__is_file_open(_source_path):
				try:
					import shutil
					shutil.move(_source_path, _destination_path)
				except:
					if output_trace:
						import traceback
						traceback.print_exc()
					self.exception(msg="file access error: " + _source_path + ", " + _destination_path)

		# 移動する用のディレクトリが空でないか確認
		if len(os.listdir(_trash_directory_path)) == 0:
			# 空の場合はディレクトリ削除
			try:
				os.rmdir(_trash_directory_path)
			except:
				if output_trace:
					import traceback
					traceback.print_exc()
				self.exception(msg="failed to remove directory : " + _trash_directory_path)

	# n日前以前の古いファイルを移動
	def flush_old_files_by_days(self, directory_path: str, days: int = 30):
		delete_date_to = (datetime.today() - timedelta(days=days)).date()
		self.flush_old_files_by_date(directory_path=directory_path, delete_date_to=delete_date_to)

	@classmethod
	# 指定した日付を含む、過去のファイルをリストアップ
	def __list_up_old_files_by_date(cls, directory_path: str, delete_date_to: date) -> list[str]:
		_old_file_list = []
		# ディレクトリの存在チェック
		if not os.path.exists(directory_path):
			return _old_file_list

		# ファイル一覧取得・チェック
		_file_or_directory_name_list: list[str] = os.listdir(directory_path)
		for _file_or_directory_name in _file_or_directory_name_list:
			_file_or_directory_full_path: str = directory_path + "\\" + _file_or_directory_name

			# ディレクトリでないことを確認
			if not os.path.isfile(_file_or_directory_full_path):
				continue

			# ファイルのみ処理
			_filename: str = _file_or_directory_name

			# ファイルの更新時刻取得
			_last_updated_timestamp: float = os.path.getmtime(_file_or_directory_full_path)
			_last_updated_datetime: datetime = datetime.fromtimestamp(_last_updated_timestamp)
			_last_updated_date: date = _last_updated_datetime.date()

			# 更新日を判定
			if _last_updated_date <= delete_date_to:
				_old_file_list.append(_filename)

		return _old_file_list

	# 古いファイル削除
	def delete_old_files_directory(self, directory_path: str, trash_directory_name: str = "trash"):
		_trash_directory_path = directory_path + "\\" + trash_directory_name
		if os.path.exists(_trash_directory_path):
			try:
				# ディレクトリごと削除
				import shutil
				shutil.rmtree(_trash_directory_path)
				self.__make_directories(_trash_directory_path)
			except:
				import traceback
				traceback.print_exc()
				self.exception(msg="failed to remove directory : " + _trash_directory_path)

	@classmethod
	# ファイルが開いているか確認
	def __is_file_open(cls, file_path: str, output_trace: bool = False) -> bool:
		# ファイルの存在チェック
		if not os.path.exists(file_path):
			return False

		_original_file_path: str = file_path
		# 一時的なファイル名の探索
		_temporary_file_path: str = _original_file_path
		# 現時点で存在しないファイル名となるまで適当な文字(数字1文字)を付与
		while os.path.exists(_temporary_file_path):
			# ランダムな数字1文字(0～9)を生成
			import random
			_random_int: int = random.randint(0, 9)
			_char_to_add = str(_random_int)

			# 末尾に付与して一時的なファイル名候補を更新
			_temporary_file_path += _char_to_add

		# ファイル名を一時的に変更可能か試みる
		try:
			# ファイル名変更
			os.rename(_original_file_path, _temporary_file_path)
			# ファイル名を元に戻す
			os.rename(_temporary_file_path, _original_file_path)
		except:
			# 例外発生(ファイル名変更に失敗した場合)
			if output_trace:
				import traceback
				traceback.print_exc()
			# ファイルが開かれていると判定
			return True

		# ファイル名の一時変更に成功した場合は、ファイルが開かれていないと判定
		return False
