# required packages:
# pushbullet.py

from pushbullet import Pushbullet, Device
from typing import List, Optional


class PushbulletWrapper(Pushbullet):
	# コンストラクタ
	def __init__(
			self,
			api_key: str,
			target_device_nicknames: Optional[List[str]] = None
	):
		# 通知対象のデバイス名リストが指定されていない場合
		if target_device_nicknames is None:
			target_device_nicknames = []

		# 親クラスのコンストラクタ実行
		super().__init__(api_key=api_key)

		# メンバ変数初期化
		self.target_devices: List[Device] = []
		self.target_device_nicknames: List[str] = []

		# 特定のデバイスを抽出
		self.set_target_devices(target_device_nicknames=target_device_nicknames)

	# 特定のデバイスを抽出して保持
	def set_target_devices(
			self,
			target_device_nicknames: Optional[List[str]] = None,
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
			only_target: bool = True,
			device: Optional[Device] = None,
			chat: Optional[str] = None,
			email: Optional[str] = None,
			channel: Optional[str] = None
	):
		if only_target and len(self.target_devices) > 0:
			# 抽出したデバイスにのみ送信
			for _target_device in self.target_devices:
				super().push_note(
					title=title,
					body=body,
					device=_target_device,
					chat=chat,
					email=email,
					channel=channel
				)
		else:
			# 全デバイスに送信
			super().push_note(
				title=title,
				body=body,
				device=device,
				chat=chat,
				email=email,
				channel=channel
			)

	# メソッド拡張(push_link)
	def push_link(
			self,
			title: str,
			url: str,
			# 以下オプション
			only_target: bool = True,
			body: Optional[str] = None,
			device: Optional[Device] = None,
			chat: Optional[str] = None,
			email: Optional[str] = None,
			channel: Optional[str] = None
	):
		if only_target and len(self.target_devices) > 0:
			# 抽出したデバイスにのみ送信
			for _target_device in self.target_devices:
				super().push_link(
					title=title,
					url=url,
					body=body,
					device=_target_device,
					chat=chat,
					email=email,
					channel=channel
				)
		else:
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

	# メソッド拡張(push_file)
	def push_file(
			self,
			file_name: str,
			file_url: str,
			file_type: str,
			# 以下オプション
			only_target: bool = True,
			body: Optional[str] = None,
			title: Optional[str] = None,
			device: Optional[Device] = None,
			chat: Optional[str] = None,
			email: Optional[str] = None,
			channel: Optional[str] = None
	):
		if only_target and len(self.target_devices) > 0:
			# 抽出したデバイスにのみ送信
			for _target_device in self.target_devices:
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
		else:
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
