from cryptography.fernet import Fernet
from typing import Any
from dataclasses import dataclass


@dataclass
class FernetWrapper(Fernet):
	# コンストラクタ
	def __init__(
			self,
			key: bytes | str | None = None,
			backend: Any | None = None
	):
		# 暗号化キー(メンバ変数としては保存しない)
		_key: bytes
		# 引数で暗号化キーの指定があればそちらを優先する
		if (type(key) is str) and (len(key) > 0):
			# 引数の型がstrの場合、bytesに変換
			_key = key.encode()
		elif (type(key) is bytes) and (len(key) > 0):
			# 引数の型がbytesの場合、そのまま適用
			_key = key
		else:
			# 上記以外の場合は自動生成
			_key = super().generate_key()

		# 親クラス初期化
		super().__init__(key=_key, backend=backend)

		# メンバ変数初期化
		self.__set_last_data(
			str_to_encrypt="",
			bytes_to_encrypt=b"",
			encrypted_bytes=b"",
			encrypted_str="",
			str_to_decrypt="",
			bytes_to_decrypt=b"",
			decrypted_bytes=b"",
			decrypted_str=""
		)

	# 暗号化
	def encrypt(
			self,
			source_to_encrypt: str | bytes,
			# 以下オプション
			encoding: str = "utf-8",
			save: bool = False,
			return_as_str: bool = False,
			return_as_bytes: bool = True
	) -> str | bytes | tuple[str, bytes]:
		# 暗号化前の文字列/バイト列(初期化)
		_str_to_encrypt: str = ""
		_bytes_to_encrypt: bytes = b""
		# 型変換(str <-> bytes)
		_str_to_encrypt, _bytes_to_encrypt = self.get_str_and_bytes(source=source_to_encrypt, encoding=encoding)

		# バイト列を暗号化されたバイト列に変換
		_encrypted_bytes: bytes = super().encrypt(data=_bytes_to_encrypt)
		# 暗号化されたバイト列を暗号化された文字列に変換
		_encrypted_str: str = _encrypted_bytes.decode(encoding=encoding)

		# 要すれば記録
		if save:
			self.__set_last_data(
				str_to_encrypt=_str_to_encrypt,
				bytes_to_encrypt=_bytes_to_encrypt,
				encrypted_bytes=_encrypted_bytes,
				encrypted_str=_encrypted_str
			)
		else:
			# 記録不要な場合は各メンバ変数初期化
			self.__set_last_data(
				str_to_encrypt="",
				bytes_to_encrypt=b"",
				encrypted_bytes=b"",
				encrypted_str=""
			)

		# 指定の形式で返却(str | bytes | tuple[str, bytes])
		if return_as_str:
			if return_as_bytes:
				return _encrypted_str, _encrypted_bytes
			else:
				return _encrypted_str
		else:
			return _encrypted_bytes

	# 復号
	def decrypt(
			self,
			source_to_decrypt: str | bytes,
			# 以下オプション
			encoding: str = "utf-8",
			save: bool = False,
			return_as_str: bool = True,
			return_as_bytes: bool = False
	) -> str | bytes | tuple[str, bytes]:
		# 復号前の文字列/バイト列(初期化)
		_str_to_decrypt: str = ""
		_bytes_to_decrypt: bytes = b""
		# 型変換(str <-> bytes)
		_str_to_decrypt, _bytes_to_decrypt = self.get_str_and_bytes(source=source_to_decrypt, encoding=encoding)

		# 暗号化されたバイト列を復号
		_decrypted_bytes: bytes = super().decrypt(_bytes_to_decrypt)
		# 復号されたバイト列を文字列に変換
		_decrypted_str: str = _decrypted_bytes.decode(encoding=encoding)

		# 要すれば記録
		if save:
			self.__set_last_data(
				str_to_decrypt=_str_to_decrypt,
				bytes_to_decrypt=_bytes_to_decrypt,
				decrypted_bytes=_decrypted_bytes,
				decrypted_str=_decrypted_str
			)
		else:
			# 記録不要な場合は各メンバ変数初期化
			self.__set_last_data(
				str_to_decrypt="",
				bytes_to_decrypt=b"",
				decrypted_bytes=b"",
				decrypted_str=""
			)

		# 指定の形式で返却(bytes | str | tuple[str, bytes])
		if return_as_str:
			if return_as_bytes:
				return _decrypted_str, _decrypted_bytes
			else:
				return _decrypted_str
		else:
			return _decrypted_bytes

	@staticmethod
	# 文字列またはバイト列から、両者に変換した際の値を得る
	# str | bytes -> tuple[str, bytes]
	def get_str_and_bytes(
			source: str | bytes,
			encoding: str = "utf-8"
	) -> tuple[str, bytes]:
		if type(source) is str:
			# 入力文字列はそのまま
			_source_str = source
			# 入力文字列をバイト列に変換
			_source_bytes = source.encode(encoding=encoding)
		else:
			# 入力バイト列を文字列に変換
			_source_str = source.decode(encoding=encoding)
			# 入力バイト列はそのまま
			_source_bytes = source

		return _source_str, _source_bytes

	# 最後に暗号化/復号したデータの更新
	def __set_last_data(
			self,
			str_to_encrypt: str | None = None,
			bytes_to_encrypt: bytes | None = None,
			encrypted_bytes: bytes | None = None,
			encrypted_str: str | None = None,
			str_to_decrypt: str | None = None,
			bytes_to_decrypt: bytes | None = None,
			decrypted_bytes: bytes | None = None,
			decrypted_str: str | None = None
	):
		if str_to_encrypt is not None:
			self.__last_str_to_encrypt = str_to_encrypt
		if bytes_to_encrypt is not None:
			self.__last_bytes_to_encrypt = bytes_to_encrypt
		if encrypted_bytes is not None:
			self.__last_encrypted_bytes = encrypted_bytes
		if encrypted_str is not None:
			self.__last_encrypted_str = encrypted_str
		if str_to_decrypt is not None:
			self.__last_str_to_decrypt = str_to_decrypt
		if bytes_to_decrypt is not None:
			self.__last_bytes_to_decrypt = bytes_to_decrypt
		if decrypted_bytes is not None:
			self.__last_decrypted_bytes = decrypted_bytes
		if decrypted_str is not None:
			self.__last_decrypted_str = decrypted_str

	# 最後に暗号化した文字列/バイト列(暗号化前)
	# デフォルトでは文字列を返却
	def get_last_data_to_encrypt(
			self,
			return_as_str: bool = True,
			return_as_bytes: bool = False
	) -> str | bytes | tuple[str, bytes] | None:
		# 指定の形式で返却(str | bytes | tuple[str, bytes])
		return self.__assemble_str_and_bytes_to_return(
			str_to_return=self.__last_str_to_encrypt,
			bytes_to_return=self.__last_bytes_to_encrypt,
			return_as_str=return_as_str,
			return_as_bytes=return_as_bytes
		)

	# 最後に暗号化した文字列/バイト列(暗号化後)
	# デフォルトではバイト列を返却
	def get_last_encrypted_data(
			self,
			return_as_str: bool = False,
			return_as_bytes: bool = True
	) -> str | bytes | tuple[str, bytes] | None:
		# 指定の形式で返却(str | bytes | tuple[str, bytes])
		return self.__assemble_str_and_bytes_to_return(
			str_to_return=self.__last_encrypted_str,
			bytes_to_return=self.__last_encrypted_bytes,
			return_as_str=return_as_str,
			return_as_bytes=return_as_bytes
		)

	# 最後に復号した文字列/バイト列(復号前)
	# デフォルトではバイト列を返却
	def get_last_data_to_decrypt(
			self,
			return_as_str: bool = False,
			return_as_bytes: bool = True
	) -> str | bytes | tuple[str, bytes] | None:
		# 指定の形式で返却(str | bytes | tuple[str, bytes])
		return self.__assemble_str_and_bytes_to_return(
			str_to_return=self.__last_str_to_decrypt,
			bytes_to_return=self.__last_bytes_to_decrypt,
			return_as_str=return_as_str,
			return_as_bytes=return_as_bytes
		)

	# 最後に復号された文字列/バイト列(復号後)
	def get_last_decrypted_data(
			self,
			return_as_str: bool = True,
			return_as_bytes: bool = False
	) -> str | bytes | tuple[str, bytes] | None:
		# 指定の形式で返却(str | bytes | tuple[str, bytes])
		return self.__assemble_str_and_bytes_to_return(
			str_to_return=self.__last_decrypted_str,
			bytes_to_return=self.__last_decrypted_bytes,
			return_as_str=return_as_str,
			return_as_bytes=return_as_bytes
		)

	@staticmethod
	# 文字列/バイト列の返却形式を成型
	def __assemble_str_and_bytes_to_return(
			return_as_str: bool = True,
			str_to_return: str = "",
			return_as_bytes: bool = True,
			bytes_to_return: bytes = b""
	) -> str | bytes | tuple[str, bytes] | None:
		if return_as_str:
			if return_as_bytes:
				return str_to_return, bytes_to_return
			else:
				return str_to_return
		else:
			if return_as_bytes:
				return bytes_to_return
			else:
				return None
