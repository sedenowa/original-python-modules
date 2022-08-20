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

	def set_token(self, token: str):
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
			debug: bool = None
	) -> Response | None:
		from requests import post

		# 入力チェック
		# 有効なトークンが設定されているかチェック
		if not isinstance(self.token, str):
			print("Invalid Token.")
			return
		elif len(self.token) == 0:
			print("Empty Token.")
			return

		if message == "":
			print("Empty Message.")
			return

		# 入力チェック(debug)
		if debug is None:
			debug = self.debug

		if debug:
			print("header : " + str(self.get_api_header()))
			print("payload : " + str(self.get_api_payload(message)))

		# リクエスト送信
		_response: Response = post(
			url=self.API_URL,
			headers=self.get_api_header(),
			params=self.get_api_payload(message)
		)

		if debug:
			print("response : " + _response.text)

		return _response

	# API引数取得用メソッド
	# APIのURL
	@classmethod
	def get_api_url(cls) -> str:
		return cls.API_URL

	# ヘッダー
	def get_api_header(self) -> dict | None:
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
	def get_api_payload(message: str) -> dict | None:
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
