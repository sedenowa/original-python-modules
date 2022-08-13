# required packages:
# selenium
# webdriver-manager
# Pillow

# selenium
from selenium import webdriver
from selenium.common import NoSuchWindowException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager
from webdriver_manager.opera import OperaDriverManager

# other
from enum import IntEnum
import traceback
import os
import io
import unicodedata
import time
import urllib.parse
import random
import inspect
from dataclasses import dataclass
from PIL import Image


@dataclass
# Original WebDriver Wrapper Class
class WebDriverWrapper(object):
	# possible driver classes
	__DRIVER_CLASSES = \
		webdriver.Chrome \
		| webdriver.Edge \
		| webdriver.Firefox \
		| webdriver.Ie

	# possible driver classes
	__DRIVER_CLASS_TYPES = \
		type(webdriver.Chrome) \
		| type(webdriver.Edge) \
		| type(webdriver.Firefox) \
		| type(webdriver.Ie)

	# CONST VALUES
	class BrowserIds(IntEnum):
		NONE: int = 0
		CHROME: int = 1
		CHROMIUM: int = 2
		EDGE: int = 3
		FIREFOX: int = 4
		IE: int = 5
		OPERA: int = 6

	# コンストラクタ
	def __init__(
			self,
			browser_id: int = BrowserIds.CHROME,
			chrome_user_data_dir: str = "",
			chrome_profile_directory: str = "",
			chromium_user_data_dir: str = "",
			chromium_profile_directory: str = "",
			headless: bool = False,
			catch_exception: bool = False,
			output_trace: bool = True
	):
		# ブラウザ用のドライバ取得
		self.driver: WebDriverWrapper.__DRIVER_CLASSES = \
			self.__get_new_driver(
				browser_id=browser_id,
				chrome_user_data_dir=chrome_user_data_dir,
				chrome_profile_directory=chrome_profile_directory,
				chromium_user_data_dir=chromium_user_data_dir,
				chromium_profile_directory=chromium_profile_directory,
				headless=headless
			)
		# ブラウザID保存
		self.__browser_id: int = browser_id

		# モジュールファイルの絶対パス
		_abspath_of_this_module: str = inspect.getfile(self.__class__)
		# モジュールファイルの格納ディレクトリ
		self.__abspath_directory_of_this_module: str = os.path.dirname(_abspath_of_this_module)
		# モジュールファイルのファイル名
		self.__filename_of_this_module: str = os.path.basename(_abspath_of_this_module)
		# インスタンス毎の一時データ格納用ディレクトリの格納用ディレクトリ
		self.__abspath_temp_directory_of_this_module: str = self.__abspath_directory_of_this_module + "\\" + "_temp"

		# メンバ変数としてIDを設定、保持
		self.__id: int | None = self.__get_unique_id()

		# インスタンス毎の一時データ格納用ディレクトリ
		self.__temporary_directory: str | None = \
			self.__make_temporary_directory(catch_exception=catch_exception, output_trace=output_trace)
		# 自身のインスタンスで一時保存用ディレクトリを生成したかどうか
		self.__made_temporary_directory_by_myself: bool = (self.__temporary_directory is not None)

	# 利用可能なIDを探索
	def __get_unique_id(
			self
	) -> int | None:
		_is_id_set: bool = False

		# デフォルトではインスタンスのidを取得・設定
		_id: int = id(self)

		# 一時利用用のデータ保存領域のパス
		_temporary_directory: str = \
			self.__abspath_temp_directory_of_this_module + "\\" + str(_id)

		# 探索準備
		_max_iter: int = 100
		_iter: int = 1

		# 探索
		while _iter < _max_iter:
			if not os.path.exists(_temporary_directory):
				# 未使用のidを発見
				return _id
			else:
				# 未使用のidを探索
				# 新たに自動生成するidの桁数を、現在のidと揃える
				_digit: int = len(str(_id))
				# 最低3桁
				_digit = max(3, _digit)
				# 最大100桁
				_digit = min(100, _digit)

				_id = random.randrange(10 ** (_digit - 1), 10 ** _digit)
				# 一時利用用のデータ保存領域を再設定
				_temporary_directory = \
					self.__abspath_temp_directory_of_this_module + "\\" + str(_id)

				# 次のループへ
				_iter += 1

		# 見つからなかった場合
		return None

	# インスタンス毎の一時データ格納用ディレクトリ生成
	def __make_temporary_directory(
			self,
			catch_exception: bool = False,
			output_trace: bool = True
	) -> str | None:
		_temporary_directory: str = self.__abspath_temp_directory_of_this_module + "\\" + str(self.__id)

		# インスタンス毎の一時データ格納用ディレクトリ生成
		if not os.path.exists(_temporary_directory):
			try:
				# データ保存領域作成
				os.makedirs(_temporary_directory)
				self.__made_temporary_directory_by_myself = True
				return _temporary_directory
			except Exception as e:
				if catch_exception:
					# 例外をcatchする場合
					if output_trace:
						# トレースを出力
						traceback.print_exc()
				else:
					# 例外をcatchしない場合はそのままraise
					raise e

		# 生成できなければNoneを返却
		return None

	# デストラクタ
	def __del__(
			self
	):
		# インスタンス毎の一時データ格納用ディレクトリ削除(自ら作成した場合)
		if self.__made_temporary_directory_by_myself:
			if os.path.exists(self.__temporary_directory):
				os.rmdir(self.__temporary_directory)

		# インスタンス毎の一時データ格納用ディレクトリの格納用ディレクトリ削除(可能なら)
		if os.path.exists(self.__abspath_temp_directory_of_this_module):
			_contents: list[str] = os.listdir(self.__abspath_temp_directory_of_this_module)
			if len(_contents) == 0:
				# 中身が空であれば削除
				os.rmdir(self.__abspath_temp_directory_of_this_module)

		# ドライバが生成されている場合はドライバを終了
		if self.driver is not None:
			self.driver.quit()

	# ドライバ取得
	def get_driver(
			self
	) -> __DRIVER_CLASSES | None:
		return self.driver

	# よく使うメソッドの疑似オーバーロード
	# find_element
	# 対象が見つからなければNoneを返す
	def find_element(
			self,
			by: str = By.ID,
			value=None,
			# 独自追加
			catch_exception: bool = True,
			output_trace: bool = True
	) -> WebElement | None:
		# デフォルト返却値
		_found_element: WebElement | None = None

		# ドライバが初期化されていない場合
		if self.driver is None:
			return _found_element

		# 探索
		try:
			_found_element = self.driver.find_element(by=by, value=value)
		except Exception as e:
			if catch_exception:
				if output_trace:
					traceback.print_exc()
			else:
				raise e
		finally:
			return _found_element

	# find_elements
	# 対象が見つからなければ[]を返す
	def find_elements(
			self,
			by: str = By.ID,
			value=None,
			# 独自追加
			catch_exception: bool = True,
			output_trace: bool = True
	) -> list[WebElement]:
		_found_elements: list[WebElement] = []
		if self.driver is None:
			return _found_elements

		try:
			_found_elements = self.driver.find_elements(by=by, value=value)
		except Exception as e:
			if catch_exception:
				if output_trace:
					traceback.print_exc()
				_found_elements = []
			else:
				raise e
		finally:
			return _found_elements

	# 現在のブラウザID取得
	def __get_current_browser_id(
			self
	) -> int:
		return self.__browser_id

	# Pixel 5 相当の動きをするよう設定
	def set_environment_as_pixel5(
			self
	) -> bool:
		_width: int = 393
		_height: int = 851
		_device_scale_factor: int = 3
		_mobile: bool = True
		_user_agent: str = \
			"--user-agent=Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) \
			Chrome/101.0.4951.41 Mobile Safari/537.36"

		return self.__set_environment_as(
			width=_width,
			height=_height,
			device_scale_factor=_device_scale_factor,
			mobile=_mobile,
			user_agent=_user_agent
		)

	# 指定したデバイス相当の動きをするよう設定
	def __set_environment_as(
			self,
			width: int,
			height: int,
			device_scale_factor: int,
			mobile: bool,
			user_agent: str,
	) -> bool:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return False

		self.set_user_viewport(
			width=width,
			height=height,
			device_scale_factor=device_scale_factor,
			mobile=mobile
		)

		self.set_user_agent(
			user_agent=user_agent
		)

		self.driver.set_window_size(
			width=width,
			height=height
		)

		return True

	# その時点のスクリーンショットを保存
	def save_screen_shot(
			self,
			save_path: str = "screenshot.png",
			make_directory: bool = True
	) -> bool:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return False

		# 保存先ディレクトリの存在チェック
		_directory_path: str = os.path.dirname(save_path)
		if (_directory_path == "") or os.path.exists(_directory_path):
			# ディレクトリの指定がないか、指定ディレクトリが存在
			pass
		elif make_directory:
			# 指定ディレクトリが存在せず、ディレクトリ作成したい場合
			os.makedirs(_directory_path)
		else:
			# 指定ディレクトリが存在せず、ディレクトリ作成もしない
			return False

		# スクリーンショット保存
		self.driver.save_screenshot(save_path)

		return True

	# 全画面のスクリーンショットを保存
	def save_screen_shot_of_full_screen(
			self,
			save_path: str = "screenshot.png",
			make_directory: bool = True,
			crop_horizontal_scroll_bar: bool = True,
			crop_vertical_scroll_bar: bool = True,
	) -> bool:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return False

		# 保存先ディレクトリの存在チェック
		_directory_path: str = os.path.dirname(save_path)
		if (_directory_path == "") or os.path.exists(_directory_path):
			# ディレクトリの指定がないか、指定ディレクトリが存在
			pass
		elif make_directory:
			# 指定ディレクトリが存在せず、ディレクトリ作成したい場合
			os.makedirs(_directory_path)
		else:
			# 指定ディレクトリが存在せず、ディレクトリ作成もしない
			return False

		# ウィンドウ最大化
		self.get_driver().maximize_window()
		# 一度ページを最後まで読み込ませる
		self._scroll_to_end_of_page(interval_of_scroll=0.0)

		# コンテンツ全体のサイズ取得
		_scroll_width, _scroll_height, _inner_width, _inner_height, _client_width, _client_height = self._get_contents_sizes()

		# スクロールバーの幅
		_height_of_horizontal_scroll_bar: int = _inner_height - _client_height
		_width_of_vertical_scroll_bar: int = _inner_width - _client_width

		# スクロール回数算出
		_required_horizontal_scroll_num = (_scroll_width - 1) // _client_width + 1
		_required_vertical_scroll_num = (_scroll_height - 1) // _client_height + 1

		# スクロール最後の端数部分のサイズ
		_fraction_width: int = (_scroll_width - 1) % _client_width + 1
		_fraction_height: int = (_scroll_height - 1) % _client_height + 1

		# スクロール原点に移動
		self.get_driver().execute_script("window.scrollTo(arguments[0], arguments[1]);", 0, 0)

		# 元となる画像を取得
		_screenshot_image: Image.Image = self._get_screenshot_image()

		# 要すればスクロールバー分をカット
		_width_to_crop: int = _inner_width
		_height_to_crop: int = _inner_height
		if crop_vertical_scroll_bar:
			_width_to_crop = _client_width
		if crop_vertical_scroll_bar:
			_height_to_crop = _client_height
		_screenshot_image = _screenshot_image.crop(
			(0, 0, _width_to_crop, _height_to_crop)
		)

		# スクロールしながらスクリーンショット結合
		for _index_horizontal_scroll in range(_required_horizontal_scroll_num):
			_horizontal_scroll_to: int = _index_horizontal_scroll * _client_width
			for _index_vertical_scroll in range(_required_vertical_scroll_num):
				# 目的のスクロール位置に移動
				_vertical_scroll_to: int = _index_vertical_scroll * _client_height
				self.get_driver().execute_script(
					"window.scrollTo(arguments[0], arguments[1]);",
					_horizontal_scroll_to,
					_vertical_scroll_to
				)

				# ループ初回の場合はスキップ
				if _index_horizontal_scroll == 0 and _index_vertical_scroll == 0:
					continue

				# ループ初回以外の場合は追加するスクリーンショットを取得
				_screenshot_image_to_add: Image.Image = self._get_screenshot_image()

				# 結合用に使う領域のサイズ算出
				_width_to_crop: int = _client_width
				_height_to_crop: int = _client_height
				if _index_horizontal_scroll == _required_horizontal_scroll_num - 1:
					# ループの最後の場合は端数部分のサイズを設定
					_width_to_crop = _fraction_width
				if _index_vertical_scroll == _required_vertical_scroll_num - 1:
					# ループの最後の場合は端数部分のサイズを設定
					_height_to_crop = _fraction_height

				# ループの最後以外、またはループの最後で要すればスクロールバー分をカット
				if (_index_horizontal_scroll != _required_horizontal_scroll_num - 1) or crop_vertical_scroll_bar:
					_width_to_crop -= _width_of_vertical_scroll_bar
				if (_index_vertical_scroll != _required_vertical_scroll_num - 1) or crop_horizontal_scroll_bar:
					_height_to_crop -= _height_of_horizontal_scroll_bar

				# 結合用に使う領域を切り取り
				_screenshot_image_to_add = _screenshot_image_to_add.crop(
					(
						_client_width - _width_to_crop,
						_client_height - _height_to_crop,
						_client_width,
						_client_height
					)
				)

				# スクリーンショット結合
				_screenshot_image = self._concat_images(
					image_base=_screenshot_image,
					image_to_add=_screenshot_image_to_add,
					concat_vertically=True
				)

		# スクリーンショット保存
		_screenshot_image.save(save_path)

		return True

	# ページ全体を一度最後まで表示させるためにページ最後までスクロール
	def _scroll_to_end_of_page(
			self,
			interval_of_scroll: float = 0.0
	) -> None:
		# ドライバが生成されていなければそのまま終了
		if self.get_driver() is None:
			return None

		# 入力チェック(interval_of_scroll)
		try:
			interval_of_scroll = float(interval_of_scroll)
		except ValueError:
			interval_of_scroll = 0.0

		# コンテンツ全体のサイズ取得
		_scroll_width, _scroll_height, _client_width, _client_height = \
			self._get_contents_sizes(
				get_inner_width=False,
				get_inner_height=False
			)

		# スクロール回数算出
		_required_horizontal_scroll_num: int = (_scroll_width - 1) // _client_width + 1
		_required_vertical_scroll_num: int = (_scroll_height - 1) // _client_height + 1

		# 次に移動すべきスクロール位置
		_horizontal_scroll_to: int = 0
		_vertical_scroll_to: int = 0
		# 次に移動すべきスクロール位置のバックアップ(初期値は上記とずらしておく)
		_previous_horizontal_scroll_to: int = -1
		_previous_vertical_scroll_to: int = -1

		# ページのサイズが最大になりそこに到達するまで順にスクロール
		_timeout_sec: int = 60
		_start_time: float = time.time()
		while (_previous_horizontal_scroll_to != _horizontal_scroll_to) or \
				(_previous_vertical_scroll_to != _vertical_scroll_to):
			# タイムアウト確認
			_end_time: float = time.time()
			if (_end_time - _start_time) > _timeout_sec:
				break

			# スクロール
			self.get_driver().execute_script(
				"window.scrollTo(arguments[0], arguments[1]);",
				_horizontal_scroll_to,
				_vertical_scroll_to
			)

			# スクロール操作間のインターバル
			self.wait_sec(interval_of_scroll)

			# コンテンツ全体のサイズ再取得
			_scroll_width, _scroll_height = \
				self._get_contents_sizes(
					get_inner_width=False,
					get_inner_height=False,
					get_client_width=False,
					get_client_height=False
				)

			# 次に移動すべきスクロール位置のバックアップ
			_previous_horizontal_scroll_to = _horizontal_scroll_to
			_previous_vertical_scroll_to = _vertical_scroll_to

			# 次に移動すべきスクロール位置を算出
			_horizontal_scroll_to = min(_scroll_width, _horizontal_scroll_to + _client_width)
			_vertical_scroll_to = min(_scroll_height, _vertical_scroll_to + _client_height)

	# スクリーンショット取得
	def _get_screenshot_image(
			self,
			crop_horizontal_scrollbar: bool = False,
			crop_vertical_scrollbar: bool = False
	) -> Image.Image | None:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return None

		# コンテンツ全体のサイズ取得
		_inner_width, _inner_height, _client_width, _client_height = \
			self._get_contents_sizes(
				get_scroll_width=False,
				get_scroll_height=False
			)

		# スクリーンショット取得
		_screenshot_png_bytes: bytes = self.get_driver().get_screenshot_as_png()
		_screenshot_bytes_io: io.BytesIO = io.BytesIO(_screenshot_png_bytes)
		_screenshot_image: Image.Image = Image.open(_screenshot_bytes_io)

		if crop_horizontal_scrollbar:
			if _client_height < _inner_height:
				_screenshot_image = _screenshot_image.crop(
					(0, 0, _inner_width, _client_height)
				)

		if crop_vertical_scrollbar:
			if _client_width < _inner_width:
				_screenshot_image = _screenshot_image.crop(
					(0, 0, _client_width, _inner_height)
				)

		return _screenshot_image

	# 画像の結合
	@staticmethod
	def _concat_images(
			image_base: Image.Image,
			image_to_add: Image.Image,
			offset: int = None,
			concat_vertically: bool = True,
			align_center: bool = False
	) -> Image.Image | None:
		# 入力チェック(画像)
		if not isinstance(image_base, Image.Image):
			return None
		elif not isinstance(image_to_add, Image.Image):
			return image_base

		# 入力チェック(結合用オフセット)
		if offset is None:
			# 指定がない場合はそのまま並べる
			if concat_vertically:
				offset = image_base.height
			else:
				offset = image_base.width
		elif offset < 0:
			# 負値が指定されている場合は0に丸める
			offset = 0
		else:
			# それ以外は整数に丸める
			offset = int(offset)

		# 結合後の画像サイズ
		_merged_width: int = 0
		_merged_height: int = 0
		if concat_vertically:
			# 縦方向に結合
			_merged_width = max(image_base.width, image_to_add.width)
			_merged_height = max(image_base.height, offset + image_to_add.height)
		else:
			# 横方向に結合
			_merged_width = max(image_base.width, offset + image_to_add.width)
			_merged_height = max(image_base.height, image_to_add.height)

		# 結合後の画像の入れ物を生成
		merged_image: Image.Image = Image.new(
			"RGB",
			(_merged_width, _merged_height)
		)

		# ベース画像の貼り付け位置
		_horizontal_position_to_paste_base: int = 0
		_vertical_position_to_paste_base: int = 0
		# 中央揃えの場合の位置調整
		if align_center:
			if concat_vertically:
				# 縦方向に結合
				if image_base.width < image_to_add.width:
					# ベース画像の方を浮かせる場合
					_horizontal_position_to_paste_base = (image_to_add.width - image_base.width) // 2
			else:
				# 横方向に結合
				if image_base.height < image_to_add.height:
					# ベース画像の方を浮かせる場合
					_vertical_position_to_paste_base = (image_to_add.height - image_base.height) // 2
		# ベース画像の貼り付け
		merged_image.paste(
			image_base,
			(_horizontal_position_to_paste_base, _vertical_position_to_paste_base)
		)

		# 結合する画像を縦方向か横方向に貼り付け
		_horizontal_position_to_concat: int = 0
		_vertical_position_to_concat: int = 0
		if concat_vertically:
			# 縦方向に結合
			if align_center:
				# 中央揃えの場合の位置調整
				if image_to_add.width < image_base.width:
					# 結合する画像の方を浮かせる場合
					_horizontal_position_to_concat = (image_base.width - image_to_add.width) // 2
			_vertical_position_to_concat = offset
		else:
			# 横方向に結合
			_horizontal_position_to_concat = offset
			if align_center:
				# 中央揃えの場合の位置調整
				if image_to_add.height < image_base.height:
					# 結合する画像の方を浮かせる場合
					_vertical_position_to_concat = (image_base.height - image_to_add.height) // 2
		# 結合する画像を貼り付け
		merged_image.paste(
			image_to_add,
			(_horizontal_position_to_concat, _vertical_position_to_concat)
		)

		# 結合後の画像を返却
		return merged_image

	# 表示中の各種コンテンツサイズを取得(下記の順)
	# スクロール込みの全体のサイズ(width, height)
	# スクロールバー含むウィンドウに表示中のサイズ(width, height)
	# スクロールバー抜いた表示中コンテンツのサイズ(width, height)
	def _get_contents_sizes(
			self,
			get_scroll_width: bool = True,
			get_scroll_height: bool = True,
			get_inner_width: bool = True,
			get_inner_height: bool = True,
			get_client_width: bool = True,
			get_client_height: bool = True
	) -> tuple[int, ...] | None:
		# ドライバが生成されていなければそのまま終了
		if self.get_driver() is None:
			return None

		_return_list: list[int] = []
		# スクロール込みの全体のサイズ
		# width
		if get_scroll_width:
			_scroll_width: int = self.get_driver().execute_script("return document.body.scrollWidth;")
			_return_list.append(_scroll_width)
		# height
		if get_scroll_height:
			_scroll_height: int = self.get_driver().execute_script("return document.body.scrollHeight;")
			_return_list.append(_scroll_height)

		# スクロールバー含むウィンドウに表示中のサイズ
		# width
		if get_inner_width:
			_inner_width: int = self.get_driver().execute_script("return window.innerWidth;")
			_return_list.append(_inner_width)
		# height
		if get_inner_height:
			_inner_height: int = self.get_driver().execute_script("return window.innerHeight;")
			_return_list.append(_inner_height)

		# スクロールバー抜いた表示中コンテンツのサイズ
		# width
		if get_client_width:
			_client_width: int = self.get_driver().execute_script("return document.documentElement.clientWidth;")
			_return_list.append(_client_width)
		# height
		if get_client_height:
			_client_height: int = self.get_driver().execute_script("return document.documentElement.clientHeight;")
			_return_list.append(_client_height)

		# リストの要素数に応じて返却
		if len(_return_list) > 0:
			return tuple(_return_list)
		else:
			return None

	@staticmethod
	def __make_directory_if_not_exist(
			directory_path: str
	) -> bool:
		# 保存先ディレクトリの存在チェック
		if directory_path == "":
			# ディレクトリの指定がない
			return False
		elif os.path.exists(directory_path):
			# 指定ディレクトリが存在
			return True

		# 指定ディレクトリが存在せず、ディレクトリ作成もしない
		os.makedirs(directory_path)
		return False

	# 読み込み完了待機
	def wait_load_complete(
			self,
			timeout_sec: int = 10
	) -> bool:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return False

		self.driver.implicitly_wait(timeout_sec)
		return True

	# user_viewportを設定
	def set_user_viewport(
			self,
			width: int,
			height: int,
			device_scale_factor: int = 1,
			mobile: bool = False
	) -> bool:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return False

		_viewport = {
			"width": width,
			"height": height,
			"deviceScaleFactor": device_scale_factor,  # ?
			"mobile": mobile
		}
		self.driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", _viewport)
		return True

	# user_agentを設定
	def set_user_agent(
			self,
			user_agent: str
	) -> bool:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return False

		self.driver.execute_cdp_cmd(
			"Emulation.setUserAgentOverride",
			{"userAgent": user_agent}
		)

		return True

	# 直接指定したurlに遷移
	def move_to_url(
			self,
			url: str
	) -> bool:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return False

		self.driver.get(url)
		return True

	# 戻る操作を使って指定したurlに遷移
	def back_to_url(
			self,
			url: str,
			# 以下オプション
			max_iter: int = 1,
			move_anyway_finally: bool = False,
			interval_sec: float = 1,
			include_query: bool = True,
			wait_load: bool = True
	) -> bool:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return False

		# 入力チェック
		if (url == "") or (url in self.driver.current_url):
			return False

		# 目的のurlが空でないかチェック
		if url == "":
			return False
		else:
			# 現在のurlが目的のurlであるかチェック
			try:
				if url in self.driver.current_url:
					return False
			except NoSuchWindowException as e:
				import traceback
				traceback.print_exc()
				return False

		# 要すればクエリ除去
		if not include_query:
			url = self.remove_query(url=url)

		# 入力チェック
		max_iter = int(max_iter)
		if max_iter < 1:
			max_iter = 1
		else:
			# ループ回数上限以下にする
			_max_iter_limitation: int = 255
			max_iter = min(max_iter, _max_iter_limitation)

		# 最大回数までループ
		for _iter in range(max_iter):
			# 戻る操作
			self.driver.back()

			# 読み込み待機
			if wait_load:
				self.wait_load_complete()

			# 遷移ができていれば終了
			if url in self.driver.current_url:
				return True

			# 戻る操作のインターバル
			if interval_sec > 0:
				time.sleep(interval_sec)

		if move_anyway_finally:
			self.move_to_url(url=url)

		return True

	# urlからクエリを除去
	@classmethod
	def remove_query(
			cls,
			url: str
	) -> str:
		_parse_result: urllib.parse.ParseResult = urllib.parse.urlparse(url)
		_replaced_parse_result: urllib.parse.ParseResult = _parse_result._replace(query=None)
		_removed_url: str = urllib.parse.urlunparse(_replaced_parse_result)
		return _removed_url

	# 現在のURLを取得
	def get_current_url(
			self
	) -> str:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return ""

		return self.driver.current_url

	# 現在居るページを判定
	def is_at_url(
			self,
			url: str,
			remove_query: bool = True
	) -> bool:
		# 要るかどうか判定するurlが空の場合はFalse
		if url == "":
			return False

		# 現在のurlを取得
		_current_url: str = self.get_current_url()

		# 現在のurlが空の場合はFalse
		if _current_url == "":
			return False

		# 現在のurlからクエリを除去
		if remove_query:
			_current_url = self.remove_query(_current_url)

		# 判定
		_result: bool = (_current_url in url)

		return _result

	# スクリプト経由でクリックする
	def click_element(
			self,
			element: WebElement
	) -> bool:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return False

		self.driver.execute_script("arguments[0].click();", element)

		return True

	@classmethod
	# 新しいドライバ生成・取得
	def __get_new_driver(
			cls,
			# 以下オプション
			browser_id: int = BrowserIds.CHROME,
			wdm_log_level: int = 0,
			wdm_print_first_line: bool = False,
			chrome_user_data_dir: str = "",
			chrome_profile_directory: str = "",
			chromium_user_data_dir: str = "",
			chromium_profile_directory: str = "",
			headless: bool = False,
	) -> __DRIVER_CLASSES:
		# webdriver_manager関連のログ出力抑制(ログを出す場合はコメントアウト)
		os.environ['WDM_LOG_LEVEL'] = wdm_log_level.__str__()
		# webdriver_manager動作時の1行目の空行を省略(出す場合はコメントアウト)
		os.environ['WDM_PRINT_FIRST_LINE'] = wdm_print_first_line.__str__()

		# ブラウザ毎個別処理でドライバ生成
		if browser_id == cls.BrowserIds.CHROMIUM:
			# Chromium
			_driver = cls.__get_new_chromium_driver(
				chromium_user_data_dir=chromium_user_data_dir,
				chromium_profile_directory=chromium_profile_directory,
				headless=headless
			)
		elif browser_id == cls.BrowserIds.EDGE:
			# Edge(Chromium版)
			_driver = cls.__get_new_edge_driver()
		elif browser_id == cls.BrowserIds.FIREFOX:
			# Firefox
			_driver = cls.__get_new_firefox_driver()
		elif browser_id == cls.BrowserIds.IE:
			# IE
			_driver = cls.__get_new_ie_driver()
		elif browser_id == cls.BrowserIds.OPERA:
			# Opera
			_driver = cls.__get_new_opera_driver()
		else:
			# Chrome(default)
			_driver = cls.__get_new_chrome_driver(
				chrome_user_data_dir=chrome_user_data_dir,
				chrome_profile_directory=chrome_profile_directory,
				headless=headless
			)

		return _driver

	@classmethod
	# ドライバ取得(Chrome)
	def __get_new_chrome_driver(
			cls,
			# 以下オプション
			chrome_user_data_dir: str = "",
			chrome_profile_directory: str = "",
			headless: bool = False,
			catch_exception: bool = False,
			output_trace: bool = True
	) -> webdriver.Chrome | None:
		_options = webdriver.ChromeOptions()
		if chrome_user_data_dir != "" and os.path.exists(chrome_user_data_dir) and chrome_profile_directory != "":
			_options.add_argument("--user-data-dir=" + chrome_user_data_dir)
			_options.add_argument("--profile-directory=" + chrome_profile_directory)

		if headless:
			_options.add_argument("--headless")

		_driver: webdriver.Chrome | None = None

		try:
			_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=_options)
		except Exception as e:
			if catch_exception:
				# 例外をcatchする場合
				if output_trace:
					# トレースを出力
					traceback.print_exc()
			else:
				# 例外をcatchしない場合はそのままraise
				raise e

		return _driver

	@classmethod
	# ドライバ取得(Chromium)
	# TODO:動作確認
	def __get_new_chromium_driver(
			cls,
			chromium_user_data_dir: str = "",
			chromium_profile_directory: str = "",
			headless: bool = False
	) -> webdriver.Chrome | None:
		_options = webdriver.ChromeOptions()
		if chromium_user_data_dir != "" and chromium_profile_directory != "":
			if os.path.exists(chromium_user_data_dir):
				_options.add_argument("--user-data-dir=" + chromium_user_data_dir)
				_options.add_argument("--profile-directory=" + chromium_profile_directory)
		if headless:
			_options.add_argument("--headless")
		_driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), options=_options)
		return _driver

	@classmethod
	# ドライバ取得(Edge)
	# TODO:動作確認
	def __get_new_edge_driver(
			cls
	) -> webdriver.Edge | None:
		_driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
		return _driver

	@classmethod
	# ドライバ取得(Firefox)
	# TODO:動作確認
	def __get_new_firefox_driver(
			cls
	) -> webdriver.Firefox | None:
		_driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
		return _driver

	@classmethod
	# ドライバ取得(IE)
	# TODO:動作確認
	def __get_new_ie_driver(
			cls
	) -> webdriver.Ie | None:
		_driver = webdriver.Ie(IEDriverManager().install())
		return _driver

	@classmethod
	# ドライバ取得(Opera)
	# TODO:動作確認
	def __get_new_opera_driver(
			cls
	) -> webdriver.Chrome | None:
		_driver: webdriver.Chrome = webdriver.Chrome(OperaDriverManager().install())
		return _driver

	@classmethod
	# ブラウザID取得
	# ChromeとChromiumを区別できない制約あり
	def __get_browser_id(
			cls,
			driver: __DRIVER_CLASSES
	) -> int:
		_browser_id: int = cls.BrowserIds.NONE
		if isinstance(driver, webdriver.Chrome):
			# Chrome(/ Chromium/ Opera)
			_browser_id = cls.BrowserIds.CHROME
		elif isinstance(driver, webdriver.Edge):
			# Edge
			_browser_id = cls.BrowserIds.EDGE
		elif isinstance(driver, webdriver.Firefox):
			# Firefox
			_browser_id = cls.BrowserIds.FIREFOX
		elif isinstance(driver, webdriver.Ie):
			# IE
			_browser_id = cls.BrowserIds.IE

		return _browser_id

	@classmethod
	# ドライバのクラス取得
	def __get_driver_class(
			cls,
			browser_id: int = BrowserIds.CHROME
	) -> __DRIVER_CLASS_TYPES:
		if browser_id == cls.BrowserIds.CHROMIUM:
			# Chromium
			_driver_class = webdriver.Chrome
		elif browser_id == cls.BrowserIds.EDGE:
			# Edge(Chromium)
			_driver_class = webdriver.Edge
		elif browser_id == cls.BrowserIds.FIREFOX:
			# Firefox
			_driver_class = webdriver.Firefox
		elif browser_id == cls.BrowserIds.IE:
			# IE
			_driver_class = webdriver.Ie
		elif browser_id == cls.BrowserIds.OPERA:
			# Opera(Chromium)
			_driver_class = webdriver.Chrome
		else:
			# Chrome(default)
			_driver_class = webdriver.Chrome
		return _driver_class

	@classmethod
	# 文字列を正規化
	def normalize_text(
			cls,
			text: str = ""
	) -> str:
		_normalized_text: str = unicodedata.normalize('NFKC', text)
		return _normalized_text

	@classmethod
	# 指定した秒数待機
	def wait_sec(
			cls,
			sec: float = 1.0,
			print_sec: bool = False
	):
		# スリープ時間表示
		if print_sec:
			print("wait " + str(sec) + " second.")

		# スリープ
		time.sleep(sec)

	@classmethod
	# ランダムな値を計算(下限と上限を指定)
	def _calc_random_num(
			cls,
			min_num: float = 0.0,
			max_num: float = 0.0
	) -> float:
		# 格納用変数初期化
		_min_num: float = 0.0
		_max_num: float = 0.0

		# 入力チェック(min_num)
		try:
			_min_num = float(min_num)
		except ValueError:
			_min_num = 0.0

		# 入力チェック(max_num)
		try:
			_max_num = float(max_num)
		except ValueError:
			_max_num = 0.0

		# 範囲制限
		_min_num = float(max(_min_num, 0.0))
		_max_num = float(min(_max_num, 100000.0))

		_random_num: float = random.uniform(_min_num, _max_num)

		return _random_num

	@classmethod
	# ランダムな時間待機(下限と上限を指定)
	def wait_random_sec(
			cls,
			min_sec: float | None = None,
			max_sec: float | None = None,
			print_sec: bool = False
	):
		# デフォルト値
		_default_min_sec: float = 1.0
		_default_max_sec: float = 3.0

		# 入力チェック
		# 入力チェック(min_sec)
		try:
			min_sec = float(min_sec)
			# マイナスの場合は0に丸める
			if min_sec < 0:
				min_sec = 0.0
		except ValueError:
			min_sec = 0.0

		# 入力チェック(max_num)
		try:
			max_sec = float(max_sec)
			# マイナスの場合は0に丸める
			if max_sec < 0:
				max_sec = 0.0
		except ValueError:
			# 指定なしの場合はデフォルト値に丸める
			max_sec = _default_max_sec

		# スリープ時間計算
		_random_sleep_sec: float = cls._calc_random_num(min_num=min_sec, max_num=max_sec)

		# スリープ
		cls.wait_sec(sec=_random_sleep_sec, print_sec=print_sec)

	# 読み込み待機 / +αの時間待機
	def wait_load_and_additional_time(
			self,
			min_sec: float = 1.0,
			max_sec: float = 3.0,
			print_sec: bool = False
	) -> bool:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return False

		self.wait_load_complete()
		self.wait_random_sec(min_sec=min_sec, max_sec=max_sec, print_sec=print_sec)

		return True
