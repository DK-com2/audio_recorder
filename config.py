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
    DEVICE_INDEX = 1       # マイクのデバイス番号
    MICROPHONE_NAME = 'USB Microphone'  # 検索するマイク名
    
    # ファイル設定
    RECORD_DIR = os.path.join(os.path.dirname(__file__), 'recordings')  # スクリプトと同じフォルダ内
    FILE_PREFIX = 'OH1_'
    
    # Google Drive設定
    UPLOAD_FOLDER_ID = 'your_google_drive_folder_id_here'
    
    # cron設定用のコマンド
    CRON_COMMAND = f'python "{os.path.dirname(os.path.abspath(__file__))}/recorder.py"'
    
    @staticmethod
    def get_filename(extension='wav'):
        """現在時刻を使ってファイル名を生成"""
        dt_now = datetime.now()
        filename = f"{Config.FILE_PREFIX}{dt_now.strftime('%Y_%m%d_%H%M')}.{extension}"
        return os.path.join(Config.RECORD_DIR, filename)
    
    @staticmethod
    def ensure_record_dir():
        """録音ディレクトリを作成"""
        os.makedirs(Config.RECORD_DIR, exist_ok=True)
