# config.py
import os
from datetime import datetime

class Config:
    # 録音設定
    RECORD_SECONDS = 3600  # 録音時間（秒）
    SAMPLE_RATE = 44100    # サンプリング周波数
    CHANNELS = 1           # チャンネル数
    CHUNK = 4096           # バッファサイズ
    
    # デバイス設定
    DEVICE_INDEX = 0       # マイクのデバイス番号（内蔵マイクの場合は0）
    MICROPHONE_NAME = 'default'  # 検索するマイク名
    
    # ファイル設定
    RECORD_DIR = os.path.join(os.path.dirname(__file__), 'recordings')  # スクリプトと同じフォルダ内
    FILE_PREFIX = 'OH1_'
    LOCATION_NAME = 'HOME'  # 地点名（ファイル名に含まれる）
    
    # Google Drive設定
    UPLOAD_FOLDER_ID = 'your_google_drive_folder_id_here'
    
    # cron設定用のコマンド（仮想環境対応）
    CRON_COMMAND = f'bash "{os.path.dirname(os.path.abspath(__file__))}/run_recorder.sh"'
    
    @staticmethod
    def get_filename(extension='mp3'):
        """現在時刻と地点名を使ってファイル名を生成"""
        dt_now = datetime.now()
        # フォーマット: OH1_2025_0713_1430_HOME.mp3
        filename = f"{Config.FILE_PREFIX}{dt_now.strftime('%Y_%m%d_%H%M')}_{Config.LOCATION_NAME}.{extension}"
        return os.path.join(Config.RECORD_DIR, filename)
    
    @staticmethod
    def ensure_record_dir():
        """録音ディレクトリを作成"""
        os.makedirs(Config.RECORD_DIR, exist_ok=True)
