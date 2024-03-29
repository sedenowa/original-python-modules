from requests import Response
from requests import post


class LineNotify(object):
	# LINE Notify API URL
	API_URL: str = "https://notify-api.line.me/api/notify"

	def __init__(
			self,
			token: str,
			debug: bool = False
	) -> None:
		self.token: str = token

		# 入力チェック(debug)
		self.debug: bool = False
		if isinstance(debug, bool):
			self.debug: bool = debug

	def set_token(self, token: str) -> None:
		# 入力チェック
		if not isinstance(token, str):
			print("Invalid Token.")
			return
		elif len(token) == 0:
			print("Empty Token.")
			return

		self.token = token

	# LINE notify APIを使って通知
	def send_message(
			self,
			message: str,
			token: str | None = None,
			debug: bool | None = None
	) -> Response | None:
		# トークン取得
		_token: str = self.__get_api_token(token=token)
		if _token == "":
			print("Invalid Token.")
			return

		# 入力チェック
		if message == "":
			print("Empty Message.")
			return

		_url: str = self.__get_api_url()
		# debug
		self.__print_debug_message(
			debug_message="url : " + _url,
			debug=debug
		)

		_header: dict | None = self.__get_api_header()
		# debug
		self.__print_debug_message(
			debug_message="header : " + str(_header),
			debug=debug
		)

		_payload: dict | None = self.__get_api_payload(message=message)
		# debug
		self.__print_debug_message(
			debug_message="payload : " + str(_payload),
			debug=debug
		)

		_response: Response | None = None
		if (_header is not None) and (_payload is not None):
			# リクエスト送信
			_response = post(
				url=self.API_URL,
				headers=self.__get_api_header(),
				params=self.__get_api_payload(message=message)
			)
			# debug
			self.__print_debug_message(
				debug_message="response : " + _response.text,
				debug=debug
			)
		else:
			print("Invalid header or payload.")
			return

		return _response

	# 画像送信
	def send_image(
			self,
			message: str,
			image_file_path: str,
			debug: bool | None = None
	) -> Response | None:
		# TODO
		return None

	# スタンプ送信
	def send_sticker(
			self,
			message: str,
			sticker_package_id: int,
			sticker_id: int,
			debug: bool | None = None
	) -> Response | None:
		# TODO
		return None

	# トークンを入力チェック(引数がなければメンバ変数を返す)
	def __get_api_token(
			self,
			token: str | None = None
	) -> str:
		_token: str = ""

		# 入力チェック
		if isinstance(token, str) and len(token) > 0:
			# 引数のトークンを利用
			_token = token
		elif isinstance(self.token, str) and len(self.token) > 0:
			# 引数でトークンの指定がない場合
			# 有効なトークンが設定されているかチェック
			# メンバ変数のトークンを利用
			_token = self.token

		return _token

	# API引数取得用メソッド
	# APIのURL
	@classmethod
	def __get_api_url(cls) -> str:
		return cls.API_URL

	# ヘッダー
	def __get_api_header(
			self,
			token: str | None = None
	) -> dict | None:
		# トークン取得
		_token: str = self.__get_api_token(token=token)

		# 有効なトークンが設定されているかチェック
		if len(_token) == 0:
			return

		# content type
		_content_type: str = "application/x-www-form-urlencoded"

		# authorization
		authorization: str = "Bearer" + " " + _token

		# _header
		_header: dict = {
			"Content-Type": _content_type,
			"Authorization": authorization
		}

		return _header

	# ペイロード
	@staticmethod
	def __get_api_payload(
			message: str,
			sticker_package_id: int | None = None,
			sticker_id: int | None = None
	) -> dict | None:
		# 入力チェック
		if not isinstance(message, str):
			return
		elif len(message) == 0:
			return

		if not isinstance(sticker_package_id, int):
			sticker_package_id = None

		if not isinstance(sticker_id, int):
			sticker_id = None

		# payload
		_payload: dict = {
			"message": message
		}

		if (sticker_package_id is not None) and (sticker_id is not None):
			_payload_temp: dict = {
				"stickerPackageId": sticker_package_id,
				"stickerId": sticker_id
			}
			_payload.update(_payload_temp)

		return _payload

	# ファイル
	@staticmethod
	def __get_api_file(file_path: str) -> dict | None:
		# TODO
		return None

	# debugオンオフ取得
	def __get_debug(
			self,
			debug: bool | None
	) -> bool:
		_debug: bool = False

		if isinstance(debug, bool):
			_debug = debug
		elif isinstance(self.debug, bool):
			_debug = self.debug

		return _debug

	# デバッグ用メッセージ表示
	def __print_debug_message(
			self,
			debug_message: str,
			debug: bool | None
	) -> None:
		# 入力チェック
		if not isinstance(debug_message, str):
			return
		elif len(debug_message) == 0:
			return

		# デバッグオンオフ取得
		_debug: bool = self.__get_debug(debug=debug)

		# デバッグ用メッセージ表示処理
		if _debug:
			print(debug_message)
