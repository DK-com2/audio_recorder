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
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if self.config.MICROPHONE_NAME in device_info['name']:
                logging.info(f"マイクが見つかりました: {device_info['name']} (index: {i})")
                return i
        logging.warning(f"指定されたマイクが見つかりません。デフォルトのindex {self.config.DEVICE_INDEX} を使用します")
        return self.config.DEVICE_INDEX
    
    def record_to_mp3(self):
        """音声を直接MP3で録音"""
        try:
            device_index = self.get_microphone_index()
            
            # pyaudioストリームを開く
            stream = self.audio.open(
                format=pyaudio.paInt16,
                rate=self.config.SAMPLE_RATE,
                channels=self.config.CHANNELS,
                input_device_index=device_index,
                input=True,
                frames_per_buffer=self.config.CHUNK
            )
            
            logging.info(f"録音開始: {self.config.RECORD_SECONDS}秒間")
            
            # ffmpegプロセスを開始（パイプ経由でリアルタイム変換）
            process = (
                ffmpeg
                .input('pipe:', format='s16le', acodec='pcm_s16le', 
                       ar=self.config.SAMPLE_RATE, ac=self.config.CHANNELS)
                .output(self.mp3_file, acodec='mp3', audio_bitrate='128k')
                .overwrite_output()
                .run_async(pipe_stdin=True, quiet=True)
            )
            
            total_frames = int((self.config.SAMPLE_RATE / self.config.CHUNK) * self.config.RECORD_SECONDS)
            
            for i in range(total_frames):
                data = stream.read(self.config.CHUNK)
                process.stdin.write(data)
                
                # 進捗表示（10%ごと）
                if total_frames > 10 and i % (total_frames // 10) == 0:
                    progress = (i / total_frames) * 100
                    logging.info(f"録音進捗: {progress:.0f}%")
            
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
        """Google Driveにアップロード"""
        try:
            logging.info("Google Driveアップロード開始")
            
            # 認証
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()
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
