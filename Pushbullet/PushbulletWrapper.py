# required packages:
# pushbullet.py

from pushbullet import Pushbullet
from pushbullet import Device
from typing import BinaryIO
import traceback
from dataclasses import dataclass


@dataclass
class PushbulletWrapper(Pushbullet):
	# コンストラクタ
	def __init__(
			self,
			api_key: str,
			target_device_nicknames: list[str] | None = None
	):
		# 通知対象のデバイス名リストが指定されていない場合
		if target_device_nicknames is None:
			target_device_nicknames = []

		# 親クラスのコンストラクタ実行
		super().__init__(api_key=api_key)

		# メンバ変数初期化
		self.target_devices: list[Device] = []
		self.target_device_nicknames: list[str] = []

		# 特定のデバイスを抽出
		self.set_target_devices(target_device_nicknames=target_device_nicknames)

	# 特定のデバイスを抽出して保持
	def set_target_devices(
			self,
			target_device_nicknames: list[str] | None = None,
			force_reset: bool = False
	):
		# 強制リセットのフラグが立っている場合 または デバイス名の指定がない場合
		if force_reset or (target_device_nicknames is None) or (len(target_device_nicknames) == 0):
			self.target_device_nicknames = []
			self.target_devices = []
			return

		# 指定したnicknameに合致するデバイスのみ抽出
		self.target_devices = list(
			filter(
				lambda device: device.nickname in self.target_device_nicknames,
				self.devices
			)
		)

		# 抽出成功したデバイス名を改めて記録
		self.target_device_nicknames = []
		for target_device in self.target_devices:
			self.target_device_nicknames.append(target_device.nickname)

	# メソッド拡張(push_note)
	def push_note(
			self,
			title: str,
			body: str,
			# 以下オプション
			device: Device | None = None,
			chat: str | None = None,
			email: str | None = None,
			channel: str | None = None,
			# 独自追加
			only_target: bool = True,
			catch_exception: bool = False,
			output_trace: bool = True
	):
		if only_target and len(self.target_devices) > 0:
			# 抽出したデバイスにのみ送信
			for _target_device in self.target_devices:
				try:
					super().push_note(
						title=title,
						body=body,
						device=_target_device,
						chat=chat,
						email=email,
						channel=channel
					)
				except Exception as e:
					if catch_exception:
						# 例外をcatchする場合
						if output_trace:
							# トレースを出力
							traceback.print_exc()
					else:
						# 例外をcatchしない場合はそのままraise
						raise e
		else:
			# 全デバイスに送信
			try:
				super().push_note(
					title=title,
					body=body,
					device=device,
					chat=chat,
					email=email,
					channel=channel
				)
			except Exception as e:
				if catch_exception:
					# 例外をcatchする場合
					if output_trace:
						# トレースを出力
						traceback.print_exc()
				else:
					# 例外をcatchしない場合はそのままraise
					raise e

	# メソッド拡張(push_link)
	def push_link(
			self,
			title: str,
			url: str,
			# 以下オプション
			body: str | None = None,
			device: Device | None = None,
			chat: str | None = None,
			email: str | None = None,
			channel: str | None = None,
			# 独自追加
			only_target: bool = True,
			catch_exception: bool = False,
			output_trace: bool = True
	):
		if only_target and len(self.target_devices) > 0:
			# 抽出したデバイスにのみ送信
			for _target_device in self.target_devices:
				try:
					super().push_link(
						title=title,
						url=url,
						body=body,
						device=_target_device,
						chat=chat,
						email=email,
						channel=channel
					)
				except Exception as e:
					if catch_exception:
						# 例外をcatchする場合
						if output_trace:
							# トレースを出力
							traceback.print_exc()
					else:
						# 例外をcatchしない場合はそのままraise
						raise e
		else:
			try:
				# 全デバイスに送信
				super().push_link(
					title=title,
					url=url,
					body=body,
					device=device,
					chat=chat,
					email=email,
					channel=channel
				)
			except Exception as e:
				if catch_exception:
					# 例外をcatchする場合
					if output_trace:
						# トレースを出力
						traceback.print_exc()
				else:
					# 例外をcatchしない場合はそのままraise
					raise e

	# メソッド拡張(upload_file)
	def upload_file(
			self,
			f: BinaryIO,
			file_name: str,
			# 以下オプション
			file_type: str | None = None,
			# 独自追加
			catch_exception: bool = False,
			output_trace: bool = True
	):
		try:
			return super().upload_file(f=f, file_name=file_name, file_type=file_type)
		except Exception as e:
			if catch_exception:
				# 例外をcatchする場合
				if output_trace:
					# トレースを出力
					traceback.print_exc()
			else:
				# 例外をcatchしない場合はそのままraise
				raise e
		return None

	# メソッド拡張(push_file)
	def push_file(
			self,
			file_name: str,
			file_url: str,
			file_type: str,
			# 以下オプション
			body: str | None = None,
			title: str | None = None,
			device: Device | None = None,
			chat: str | None = None,
			email: str | None = None,
			channel: str | None = None,
			# 独自追加
			only_target: bool = True,
			catch_exception: bool = False,
			output_trace: bool = True
	):
		if only_target and len(self.target_devices) > 0:
			# 抽出したデバイスにのみ送信
			for _target_device in self.target_devices:
				try:
					super().push_file(
						file_name=file_name,
						file_url=file_url,
						file_type=file_type,
						body=body,
						title=title,
						device=_target_device,
						chat=chat,
						email=email,
						channel=channel
					)
				except Exception as e:
					if catch_exception:
						# 例外をcatchする場合
						if output_trace:
							# トレースを出力
							traceback.print_exc()
					else:
						# 例外をcatchしない場合はそのままraise
						raise e
		else:
			try:
				# 全デバイスに送信
				super().push_file(
					file_name=file_name,
					file_url=file_url,
					file_type=file_type,
					body=body,
					title=title,
					device=device,
					chat=chat,
					email=email,
					channel=channel
				)
			except Exception as e:
				if catch_exception:
					# 例外をcatchする場合
					if output_trace:
						# トレースを出力
						traceback.print_exc()
				else:
					# 例外をcatchしない場合はそのままraise
					raise e
