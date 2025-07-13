# recorder.py
import pyaudio
import ffmpeg
import os
import logging
import tempfile
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from config import Config

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'recorder.log')),
        logging.StreamHandler()
    ]
)

class AudioRecorder:
    def __init__(self):
        self.config = Config()
        self.config.ensure_record_dir()
        self.mp3_file = self.config.get_filename('mp3')
        self.audio = pyaudio.PyAudio()
        
    def get_microphone_index(self):
        """マイクのインデックスを自動検出"""
        # 利用可能な入力デバイスをリストアップ
        input_devices = []
        
        for i in range(self.audio.get_device_count()):
            try:
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:  # 入力可能なデバイス
                    input_devices.append((i, device_info))
                    logging.info(f"入力デバイス {i}: {device_info['name']} (チャンネル: {device_info['maxInputChannels']})")
            except Exception as e:
                logging.warning(f"デバイス {i} の情報取得エラー: {e}")
        
        if not input_devices:
            logging.error("利用可能な入力デバイスが見つかりません")
            return None
        
        # 指定されたマイク名で検索
        for device_index, device_info in input_devices:
            if self.config.MICROPHONE_NAME.lower() in device_info['name'].lower():
                logging.info(f"指定マイクが見つかりました: {device_info['name']} (index: {device_index})")
                return device_index
        
        # 指定マイクが見つからない場合は設定されたインデックスを確認
        if self.config.DEVICE_INDEX < len(input_devices):
            device_index, device_info = input_devices[self.config.DEVICE_INDEX]
            if device_info['maxInputChannels'] > 0:
                logging.info(f"デフォルトインデックス {self.config.DEVICE_INDEX} を使用: {device_info['name']}")
                return device_index
        
        # 最初の入力デバイスを使用
        device_index, device_info = input_devices[0]
        logging.warning(f"最初の入力デバイスを使用: {device_info['name']} (index: {device_index})")
        return device_index
    
    def record_to_mp3(self):
        """音声を直接MP3で録音"""
        try:
            device_index = self.get_microphone_index()
            if device_index is None:
                logging.error("使用可能なマイクデバイスがありません")
                return False
            
            # バッファオーバーフロー対策でチャンクサイズを小さく
            chunk_size = min(self.config.CHUNK, 1024)
            
            # pyaudioストリームを開く
            stream = self.audio.open(
                format=pyaudio.paInt16,
                rate=self.config.SAMPLE_RATE,
                channels=self.config.CHANNELS,
                input_device_index=device_index,
                input=True,
                frames_per_buffer=chunk_size,
                start=False  # 手動でスタート
            )
            
            logging.info(f"録音開始: {self.config.RECORD_SECONDS}秒間 (チャンク: {chunk_size})")
            
            # ffmpegプロセスを開始（パイプ経由でリアルタイム変換）
            process = (
                ffmpeg
                .input('pipe:', format='s16le', acodec='pcm_s16le', 
                       ar=self.config.SAMPLE_RATE, ac=self.config.CHANNELS)
                .output(self.mp3_file, acodec='mp3', audio_bitrate='128k')
                .overwrite_output()
                .run_async(pipe_stdin=True, quiet=True)
            )
            
            # 録音開始
            stream.start_stream()
            
            total_frames = int((self.config.SAMPLE_RATE / chunk_size) * self.config.RECORD_SECONDS)
            
            for i in range(total_frames):
                try:
                    data = stream.read(chunk_size, exception_on_overflow=False)
                    process.stdin.write(data)
                    
                    # 進捗表示（10%ごと）
                    if total_frames > 10 and i % (total_frames // 10) == 0:
                        progress = (i / total_frames) * 100
                        logging.info(f"録音進捗: {progress:.0f}%")
                        
                except IOError as e:
                    if e.errno == pyaudio.paInputOverflowed:
                        logging.warning("バッファオーバーフローが発生しましたが、録音を継続します")
                        continue
                    else:
                        raise
            
            # ストリームとプロセスを終了
            stream.stop_stream()
            stream.close()
            self.audio.terminate()
            
            process.stdin.close()
            process.wait()
            
            logging.info(f"MP3録音完了: {self.mp3_file}")
            return True
            
        except Exception as e:
            logging.error(f"録音エラー: {e}")
            return False
    
    def upload_to_drive(self):
        """Google Driveにアップロード（既存credentials.jsonを優先使用）"""
        try:
            logging.info("Google Driveアップロード開始")
            
            # 認証設定（credentials.jsonを優先使用）
            gauth = GoogleAuth()
            
            # 既存のcredentials.jsonがあるか確認
            if os.path.exists('credentials.json'):
                gauth.LoadCredentialsFile('credentials.json')
                
                # 認証情報が有効か確認
                if gauth.credentials is None:
                    # 認証情報が無効な場合のみ再認証
                    logging.info("認証情報が無効のため再認証します")
                    gauth.LocalWebserverAuth()
                elif gauth.access_token_expired:
                    # アクセストークンが期限切れの場合は更新
                    logging.info("アクセストークンを更新します")
                    gauth.Refresh()
                else:
                    # 有効な認証情報がある場合はそのまま使用
                    logging.info("既存の認証情報を使用")
            else:
                # credentials.jsonがない場合のみ初回認証
                logging.info("credentials.jsonがないため初回認証します")
                gauth.LocalWebserverAuth()
            
            # 認証情報を保存
            gauth.SaveCredentialsFile('credentials.json')
            
            # Google Driveオブジェクトを作成
            drive = GoogleDrive(gauth)
            
            # ファイル名を取得
            filename = os.path.basename(self.mp3_file)
            
            # アップロード
            file_obj = drive.CreateFile({
                'title': filename,
                'parents': [{'id': self.config.UPLOAD_FOLDER_ID}]
            })
            file_obj.SetContentFile(self.mp3_file)
            file_obj.Upload()
            
            logging.info(f"アップロード完了: {filename}")
            return True
            
        except Exception as e:
            logging.error(f"アップロードエラー: {e}")
            return False
    
    def run(self):
        """録音処理のメイン実行"""
        logging.info("録音処理開始")
        
        if not self.record_to_mp3():
            return False
        
        if not self.upload_to_drive():
            return False
        
        logging.info("録音処理完了")
        return True

if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.run()
