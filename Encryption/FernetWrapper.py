from cryptography.fernet import Fernet
from typing import Tuple


class FernetWrapper(Fernet):
	# コンストラクタ
	def __init__(self):
		# 暗号化キー(メンバ変数としては保存しない)
		__key: bytes = super().generate_key()

		# 親クラス初期化
		super().__init__(key=__key)

		# メンバ変数初期化
		# 最後に暗号化した文字列(暗号化前)
		self.__last_str_to_encrypt: str = ""
		# 最後に暗号化したバイト列(暗号化前)
		self.__last_bytes_to_encrypt: bytes = b""
		# 最後に暗号化したバイト列(暗号化後)
		self.__last_encrypted_bytes: bytes = b""
		# 最後に暗号化した文字列(暗号化後)
		self.__last_encrypted_str: str = ""

		# 最後に復号した文字列(復号前)
		self.__last_str_to_decrypt: str = ""
		# 最後に復号したバイト列(復号前)
		self.__last_bytes_to_decrypt: bytes = b""
		# 最後に復号したバイト列(復号後)
		self.__last_decrypted_bytes: bytes = b""
		# 最後に復号した文字列(復号後)
		self.__last_decrypted_str: str = ""

	# 暗号化
	def encrypt(
			self,
			source_to_encrypt: str | bytes,
			encoding: str = "utf-8",
			save: bool = False,
			return_as_str: bool = False,
			return_as_bytes: bool = True
	) -> str | bytes | Tuple[str, bytes]:
		# 暗号化前の文字列(初期化)
		_str_to_encrypt: str = ""
		# 暗号化前のバイト列(初期化)
		_bytes_to_encrypt: bytes = b""

		# 入力チェック
		if type(source_to_encrypt) is str:
			# 入力文字列はそのまま
			_str_to_encrypt = source_to_encrypt
			# 入力文字列をバイト列に変換
			_bytes_to_encrypt = source_to_encrypt.encode(encoding=encoding)
		else:
			# 入力バイト列を文字列に変換
			_str_to_encrypt = source_to_encrypt.decode(encoding=encoding)
			# 入力バイト列はそのまま
			_bytes_to_encrypt = source_to_encrypt

		# バイト列を暗号化されたバイト列に変換
		_encrypted_bytes: bytes = super().encrypt(data=_bytes_to_encrypt)
		# 暗号化されたバイト列を暗号化された文字列に変換
		_encrypted_str: str = _encrypted_bytes.decode(encoding=encoding)

		# 要すれば記録
		if save:
			self.__last_str_to_encrypt = _str_to_encrypt
			self.__last_bytes_to_encrypt = _bytes_to_encrypt
			self.__last_encrypted_bytes = _encrypted_bytes
			self.__last_encrypted_str = _encrypted_str
		else:
			# 記録不要な場合は各メンバ変数初期化
			self.__last_str_to_encrypt = ""
			self.__last_bytes_to_encrypt = b""
			self.__last_encrypted_bytes = b""
			self.__last_encrypted_str = ""

		# 指定の形式で返却(str | bytes | Tuple[str, bytes])
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
			encoding: str = "utf-8",
			save: bool = False,
			return_as_str: bool = True,
			return_as_bytes: bool = False
	) -> str | bytes | Tuple[str, bytes]:
		# 復号前の文字列(初期化)
		_str_to_decrypt: str = ""
		# 復号前のバイト列(初期化)
		_bytes_to_decrypt: bytes = b""

		# 入力チェック
		if type(source_to_decrypt) is str:
			# 入力文字列はそのまま
			_str_to_decrypt = source_to_decrypt
			# 入力文字列をバイト列に変換
			_bytes_to_decrypt = source_to_decrypt.encode(encoding=encoding)
		else:
			# 入力バイト列を文字列に変換
			_str_to_decrypt = source_to_decrypt.decode(encoding=encoding)
			# 入力バイト列はそのまま
			_bytes_to_decrypt = source_to_decrypt

		# 暗号化されたバイト列を復号
		_decrypted_bytes: bytes = super().decrypt(_bytes_to_decrypt)
		# 復号されたバイト列を文字列に変換
		_decrypted_str: str = _decrypted_bytes.decode(encoding=encoding)

		# 要すれば記録
		if save:
			self.__last_str_to_decrypt = _str_to_decrypt
			self.__last_bytes_to_decrypt = _bytes_to_decrypt
			self.__last_decrypted_bytes = _decrypted_bytes
			self.__last_decrypted_str = _decrypted_str
		else:
			# 記録不要な場合は各メンバ変数初期化
			self.__last_str_to_decrypt = ""
			self.__last_bytes_to_decrypt = b""
			self.__last_decrypted_bytes = b""
			self.__last_decrypted_str = ""

		# 指定の形式で返却(bytes | str | Tuple[str, bytes])
		if return_as_str:
			if return_as_bytes:
				return _decrypted_str, _decrypted_bytes
			else:
				return _decrypted_str
		else:
			return _decrypted_bytes

	# 最後に暗号化した文字列/バイト列(暗号化前)
	# デフォルトでは文字列を返却
	def get_last_data_to_encrypt(
			self,
			return_as_str: bool = True,
			return_as_bytes: bool = False
	) -> str | bytes | Tuple[str, bytes]:
		# 指定の形式で返却(str | bytes | Tuple[str, bytes])
		if return_as_str:
			if return_as_bytes:
				return self.__last_str_to_encrypt, self.__last_bytes_to_encrypt
			else:
				return self.__last_str_to_encrypt
		else:
			return self.__last_bytes_to_encrypt

	# 最後に暗号化した文字列/バイト列(暗号化後)
	# デフォルトではバイト列を返却
	def get_last_encrypted_data(
			self,
			return_as_str: bool = False,
			return_as_bytes: bool = True
	) -> str | bytes | Tuple[str, bytes]:
		# 指定の形式で返却(str | bytes | Tuple[str, bytes])
		if return_as_str:
			if return_as_bytes:
				return self.__last_encrypted_str, self.__last_encrypted_bytes
			else:
				return self.__last_encrypted_str
		else:
			return self.__last_encrypted_bytes

	# 最後に復号した文字列/バイト列(復号前)
	# デフォルトではバイト列を返却
	def get_last_data_to_decrypt(
			self,
			return_as_str: bool = False,
			return_as_bytes: bool = True
	) -> str | bytes | Tuple[str, bytes]:
		# 指定の形式で返却(str | bytes | Tuple[str, bytes])
		if return_as_str:
			if return_as_bytes:
				return self.__last_str_to_decrypt, self.__last_bytes_to_decrypt
			else:
				return self.__last_str_to_decrypt
		else:
			return self.__last_bytes_to_decrypt

	# 最後に復号された文字列/バイト列(復号後)
	def get_last_decrypted_data(
			self,
			return_as_str: bool = True,
			return_as_bytes: bool = False
	) -> str | bytes | Tuple[str, bytes]:
		# 指定の形式で返却(str | bytes | Tuple[str, bytes])
		if return_as_str:
			if return_as_bytes:
				return self.__last_decrypted_str, self.__last_decrypted_bytes
			else:
				return self.__last_decrypted_str
		else:
			return self.__last_decrypted_bytes
