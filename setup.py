# setup.py
"""
録音システムのセットアップスクリプト
"""
import os
import subprocess
import sys
from config import Config
from cron_manager import CronManager

def install_dependencies():
    """必要なライブラリをインストール"""
    print("必要なライブラリをインストール中...")
    
    packages = [
        'pyaudio',
        'ffmpeg-python',
        'pydrive2'
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ {package} をインストールしました")
        except subprocess.CalledProcessError:
            print(f"✗ {package} のインストールに失敗しました")

def create_directories():
    """必要なディレクトリを作成"""
    print("ディレクトリを作成中...")
    
    # 録音ファイル用ディレクトリ
    Config.ensure_record_dir()
    print(f"✓ 録音ディレクトリを作成: {Config.RECORD_DIR}")

def setup_google_drive():
    """Google Drive認証の設定"""
    print("\nGoogle Drive認証の設定:")
    print("1. Google Cloud Consoleで認証情報を作成")
    print("2. client_secrets.jsonファイルを現在のディレクトリに配置")
    print("3. config.pyでUPLOAD_FOLDER_IDを設定")
    print("4. 初回実行時にブラウザで認証を完了")

def main():
    """メインセットアップ"""
    print("=== 録音システムセットアップ ===")
    
    # ライブラリインストール
    install_dependencies()
    
    # ディレクトリ作成
    create_directories()
    
    # Google Drive設定案内
    setup_google_drive()
    
    # 使用方法の案内
    print("\n=== 使用方法 ===")
    print("1. config.pyで設定を変更")
    print("2. Google Drive認証を設定")
    print("3. cronジョブを追加:")
    print("   python cron_manager.py add '0 */1 * * *'")
    print("4. 手動実行:")
    print("   python recorder.py")
    print("5. cronジョブ管理:")
    print("   python cron_manager.py list    # 一覧表示")
    print("   python cron_manager.py remove  # 削除")
    
    print("\n=== セットアップ完了 ===")

if __name__ == "__main__":
    main()
