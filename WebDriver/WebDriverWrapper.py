# required packages:
# selenium
# webdriver-manager

# selenium
from selenium import webdriver
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
from typing import Union
from typing import Optional
from typing import List
from enum import IntEnum
from enum import auto
import traceback
import os
import unicodedata
import time
import urllib.parse
import random
import inspect


# Original WebDriver Wrapper Class
class WebDriverWrapper(object):
	# possible driver classes
	__DRIVER_CLASSES = Union[
		webdriver.Chrome,
		webdriver.Edge,
		webdriver.Firefox,
		webdriver.Ie,
		webdriver.Opera
	]

	# possible driver classes
	__DRIVER_CLASS_TYPES = Union[
		type(webdriver.Chrome),
		type(webdriver.Edge),
		type(webdriver.Firefox),
		type(webdriver.Ie),
		type(webdriver.Opera)
	]

	# CONST VALUES
	class BrowserIds(IntEnum):
		NONE: auto = auto()
		CHROME: auto = auto()
		CHROMIUM: auto = auto()
		EDGE: auto = auto()
		FIREFOX: auto = auto()
		IE: auto = auto()
		OPERA: auto = auto()

	# コンストラクタ
	def __init__(
			self,
			browser_id: int = BrowserIds.CHROME.value,
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
		self.__abspath_of_this_module: str = inspect.getfile(self.__class__)
		# モジュールファイルの格納ディレクトリ
		self.__abspath_directory_of_this_module: str = os.path.dirname(self.__abspath_of_this_module)
		# インスタンス毎の一時データ格納用ディレクトリの格納用ディレクトリ
		self.__abspath_temp_directory_of_this_module: str = self.__abspath_directory_of_this_module + "\\" + "_temp"

		# メンバ変数としてIDを設定、保持
		self.__id: Optional[int] = self.__get_unique_id()

		# インスタンス毎の一時データ格納用ディレクトリ
		self.__temporary_directory: Optional[str] = self.__make_temporary_directory()
		# 自身のインスタンスで一時保存用ディレクトリを生成したかどうか
		self.__made_temporary_directory_by_myself: bool = (self.__temporary_directory is not None)

	# 利用可能なIDを探索
	def __get_unique_id(self) -> Optional[int]:
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

				_id = random.randrange(10**(_digit - 1), 10**_digit)
				# 一時利用用のデータ保存領域を再設定
				_temporary_directory = \
					self.__abspath_temp_directory_of_this_module + "\\" + str(_id)

				# 次のループへ
				_iter += 1

		# 見つからなかった場合
		return None

	# インスタンス毎の一時データ格納用ディレクトリ生成
	def __make_temporary_directory(self, catch_exception: bool = False, output_trace: bool = True) -> Optional[str]:
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
	def __del__(self):
		# インスタンス毎の一時データ格納用ディレクトリ削除(自ら作成した場合)
		if self.__made_temporary_directory_by_myself:
			if os.path.exists(self.__temporary_directory):
				os.rmdir(self.__temporary_directory)

		# インスタンス毎の一時データ格納用ディレクトリの格納用ディレクトリ削除(可能なら)
		if os.path.exists(self.__abspath_temp_directory_of_this_module):
			_contents: List[str] = os.listdir(self.__abspath_temp_directory_of_this_module)
			print(_contents)
			if len(_contents) == 0:
				# 中身が空であれば削除
				os.rmdir(self.__abspath_temp_directory_of_this_module)

		# ドライバが生成されている場合はドライバを終了
		if self.driver is not None:
			self.driver.quit()

	# ドライバ取得
	def get_driver(self) -> __DRIVER_CLASSES | None:
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
	) -> Optional[WebElement]:
		# デフォルト返却値
		_found_element: Optional[WebElement] = None

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
	) -> List[WebElement]:
		_found_elements: List[WebElement] = []
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
	def __get_current_browser_id(self) -> int:
		return self.__browser_id

	# Pixel 5 相当の動きをするよう設定
	def set_environment_as_pixel5(self):
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
	def save_screen_shot(self, save_path: str = "screenshot.png", make_directory: bool = True) -> bool:
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

	# 読み込み完了待機
	def wait_load_complete(self, timeout_sec: int = 10) -> bool:
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
	def set_user_agent(self, user_agent: str) -> bool:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return False

		self.driver.execute_cdp_cmd(
			"Emulation.setUserAgentOverride",
			{"userAgent": user_agent}
		)

		return True

	# 直接指定したurlに遷移
	def move_to_url(self, url: str) -> bool:
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
	def remove_query(cls, url: str) -> str:
		_parse_result: urllib.parse.ParseResult = urllib.parse.urlparse(url)
		_replaced_parse_result: urllib.parse.ParseResult = _parse_result._replace(query=None)
		_removed_url: str = urllib.parse.urlunparse(_replaced_parse_result)
		return _removed_url

	# 現在のURLを取得
	def get_current_url(self) -> str:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return ""

		return self.driver.current_url

	# スクリプト経由でクリックする
	def click_element(self, element: WebElement) -> bool:
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
			browser_id: int = BrowserIds.CHROME.value,
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
		if browser_id == cls.BrowserIds.CHROMIUM.value:
			# Chromium
			_driver = cls.__get_new_chromium_driver(
				chromium_user_data_dir=chromium_user_data_dir,
				chromium_profile_directory=chromium_profile_directory,
				headless=headless
			)
		elif browser_id == cls.BrowserIds.EDGE.value:
			# Edge(Chromium版)
			_driver = cls.__get_new_edge_driver()
		elif browser_id == cls.BrowserIds.FIREFOX.value:
			# Firefox
			_driver = cls.__get_new_firefox_driver()
		elif browser_id == cls.BrowserIds.IE.value:
			# IE
			_driver = cls.__get_new_ie_driver()
		elif browser_id == cls.BrowserIds.OPERA.value:
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
			output_trace: bool = True
	) -> Optional[webdriver.Chrome]:
		_options = webdriver.ChromeOptions()
		if chrome_user_data_dir != "" and os.path.exists(chrome_user_data_dir) and chrome_profile_directory != "":
			_options.add_argument("--user-data-dir=" + chrome_user_data_dir)
			_options.add_argument("--profile-directory=" + chrome_profile_directory)

		if headless:
			_options.add_argument("--headless")

		_driver: Optional[webdriver.Chrome] = None

		try:
			_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=_options)
		except:
			if output_trace:
				traceback.print_exc()

		return _driver

	@classmethod
	# ドライバ取得(Chromium)
	# TODO:動作確認
	def __get_new_chromium_driver(
			cls,
			chromium_user_data_dir: str = "",
			chromium_profile_directory: str = "",
			headless: bool = False
	) -> Optional[webdriver.Chrome]:
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
	def __get_new_edge_driver(cls) -> Optional[webdriver.Edge]:
		_driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
		return _driver

	@classmethod
	# ドライバ取得(Firefox)
	# TODO:動作確認
	def __get_new_firefox_driver(cls) -> Optional[webdriver.Firefox]:
		_driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
		return _driver

	@classmethod
	# ドライバ取得(IE)
	# TODO:動作確認
	def __get_new_ie_driver(cls) -> Optional[webdriver.Ie]:
		_driver = webdriver.Ie(IEDriverManager().install())
		return _driver

	@classmethod
	# ドライバ取得(Opera)
	# TODO:動作確認
	def __get_new_opera_driver(cls) -> Optional[webdriver.Opera]:
		_driver = webdriver.Opera(executable_path=OperaDriverManager().install())
		return _driver

	@classmethod
	# ブラウザID取得
	# ChromeとChromiumを区別できない制約あり
	def __get_browser_id(cls, driver: __DRIVER_CLASSES) -> int:
		_browser_id: int = cls.BrowserIds.NONE.value
		_driver_class_type: cls.__DRIVER_CLASS_TYPES = type(driver)
		if _driver_class_type is type(webdriver.Chrome):
			# Chrome(/ Chromium)
			_browser_id = cls.BrowserIds.CHROME.value
		elif _driver_class_type is type(webdriver.Edge):
			# Edge
			_browser_id = cls.BrowserIds.EDGE.value
		elif _driver_class_type is type(webdriver.Firefox):
			# Firefox
			_browser_id = cls.BrowserIds.FIREFOX.value
		elif _driver_class_type is type(webdriver.Ie):
			# IE
			_browser_id = cls.BrowserIds.IE.value
		elif _driver_class_type is type(webdriver.Opera):
			# Opera
			_browser_id = cls.BrowserIds.OPERA.value

		return _browser_id

	@classmethod
	# ドライバのクラス取得
	def __get_driver_class(cls, browser_id: int = BrowserIds.CHROME.value) -> __DRIVER_CLASS_TYPES:
		if browser_id == cls.BrowserIds.CHROMIUM.value:
			# Chromium
			_driver_class = webdriver.Edge
		elif browser_id == cls.BrowserIds.EDGE.value:
			# Edge(Chromium)
			_driver_class = webdriver.Chrome
		elif browser_id == cls.BrowserIds.FIREFOX.value:
			# Firefox
			_driver_class = webdriver.Firefox
		elif browser_id == cls.BrowserIds.IE.value:
			# IE
			_driver_class = webdriver.Ie
		elif browser_id == cls.BrowserIds.OPERA.value:
			# Opera
			_driver_class = webdriver.Opera
		else:
			# Chrome(default)
			_driver_class = webdriver.Chrome
		return _driver_class

	@classmethod
	# 文字列を正規化
	def normalize_text(cls, text: str = "") -> str:
		_normalized_text: str = unicodedata.normalize('NFKC', text)
		return _normalized_text

	@classmethod
	# 指定した秒数待機
	def wait_sec(cls, sec: float = 1.0, print_sec: bool = False):
		# スリープ時間表示
		if print_sec:
			print("wait " + str(sec) + " second.")

		# スリープ
		time.sleep(sec)

	@classmethod
	# ランダムな値を計算(下限と上限を指定)
	def _calc_random_num(cls, min_num: float = 0.0, max_num: float = 0.0) -> float:
		# 格納用変数初期化
		_min_num: float = 0.0
		_max_num: float = 0.0

		# 入力チェック(min_num)
		try:
			_min_num = float(min_num)
		except:
			_min_num = 0.0

		# 入力チェック(max_num)
		try:
			_max_num = float(max_num)
		except:
			_max_num = 0.0

		# 範囲制限
		_min_num = float(max(_min_num, 0.0))
		_max_num = float(min(_max_num, 100000.0))

		_random_num: float = random.uniform(_min_num, _max_num)

		return _random_num

	@classmethod
	# ランダムな時間待機(下限と上限を指定)
	def wait_random_sec(cls, min_sec: float = 1.0, max_sec: float = 3.0, print_sec: bool = False):
		# スリープ時間計算
		_random_sleep_sec: float = cls._calc_random_num(min_num=min_sec, max_num=max_sec)

		# スリープ
		cls.wait_sec(sec=_random_sleep_sec, print_sec=print_sec)

	# 読み込み待機 / +αの時間待機
	def wait_load_and_additional_time(self, min_sec: float = 1.0, max_sec: float = 3.0, print_sec: bool = False) -> bool:
		# ドライバが生成されていなければそのまま終了
		if self.driver is None:
			return False

		self.wait_load_complete()
		self.wait_random_sec(min_sec=min_sec, max_sec=max_sec, print_sec=print_sec)

		return True
