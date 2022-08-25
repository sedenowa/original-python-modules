from requests import Response


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
	def notify(
			self,
			message: str,
			token: str | None = None,
			debug: bool = None
	) -> Response | None:
		from requests import post

		# トークン取得
		_token: str = self.__get_token(token=token)

		if _token == "":
			print("Invalid Token.")
			return

		# 入力チェック
		if message == "":
			print("Empty Message.")
			return

		# 入力チェック(debug)
		if debug is None:
			debug = self.debug

		_url: str = self.__get_api_url()
		_header: dict | None = self.__get_api_header()
		_payload: dict | None = self.__get_api_payload(message=message)

		if debug:
			print("header : " + str(self.__get_api_header()))
			print("payload : " + str(self.__get_api_payload(message=message)))

		_response: Response | None = None
		if _header is not None and _payload is not None:
			# リクエスト送信
			_response = post(
				url=self.API_URL,
				headers=self.__get_api_header(),
				params=self.__get_api_payload(message=message)
			)

			if debug:
				print("response : " + _response.text)
		else:
			print("Invalid header or payload.")
			return

		return _response

	# 画像送信
	def send_image(
			self,
			image_file_path: str
	) -> Response | None:
		# TODO
		return None

	# スタンプ送信
	def send_sticker(
			self,
			sticker_package_id: int,
			sticker_id: int
	) -> Response | None:
		# TODO
		return None

	# トークンを入力チェック(引数がなければメンバ変数を返す)
	def __get_token(
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
	def __get_api_header(self) -> dict | None:
		# 有効なトークンが設定されているかチェック
		if not isinstance(self.token, str):
			return
		elif len(self.token) == 0:
			return

		# content type
		_content_type: str = "application/x-www-form-urlencoded"

		# authorization
		authorization: str = "Bearer" + " " + self.token

		# _header
		_header: dict = {
			"Content-Type": _content_type,
			"Authorization": authorization
		}

		return _header

	# ペイロード
	@staticmethod
	def __get_api_payload(message: str) -> dict | None:
		# 入力チェック
		if not isinstance(message, str):
			return
		elif len(message) == 0:
			return

		# payload
		_payload: dict = {
			"message": message
		}

		return _payload

	# ファイル
	@staticmethod
	def __get_api_file(file_path: str) -> dict | None:
		# TODO
		return None