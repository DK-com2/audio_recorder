#!/bin/bash

# Raspberry Pi用 音声録音システム セットアップスクリプト

echo "=== Raspberry Pi 音声録音システム セットアップ ==="

# システムパッケージのインストール
echo "1. システムパッケージをインストール中..."
sudo apt update
sudo apt install -y python3-full python3-venv ffmpeg portaudio19-dev python3-dev

# 仮想環境の作成
echo "2. 仮想環境を作成中..."
python3 -m venv venv

# 仮想環境の有効化
echo "3. 仮想環境を有効化中..."
source venv/bin/activate

# 依存関係のインストール
echo "4. Python依存関係をインストール中..."
pip install --upgrade pip
pip install -r requirements.txt

# ディレクトリ作成
echo "5. 必要なディレクトリを作成中..."
mkdir -p recordings

# スクリプトに実行権限を付与
echo "6. スクリプトに実行権限を設定中..."
chmod +x run_recorder.sh
chmod +x run_cron_manager.sh
chmod +x setup_raspberry_pi.sh
chmod +x config_changer.sh

echo ""
echo "=== セットアップ完了 ==="
echo ""
echo "使用方法:"
echo "1. Google Drive認証設定:"
echo "   - client_secrets.jsonを配置"
echo "   - config.pyでUPLOAD_FOLDER_IDを設定"
echo ""
echo "2. 設定変更:"
echo "   ./config_changer.sh    # 録音時間と地点名を変更"
echo ""
echo "3. 実行方法:"
echo "   手動実行: ./run_recorder.sh"
echo "   cron管理: ./run_cron_manager.sh add '0 */1 * * *'"
echo ""
echo "4. 直接仮想環境で実行:"
echo "   source venv/bin/activate"
echo "   python recorder.py"
echo ""
echo "5. 定期実行設定:"
echo "   ./run_cron_manager.sh add '0 */1 * * *'"
echo "   ./run_cron_manager.sh list    # 一覧表示"
echo "   ./run_cron_manager.sh remove  # 削除"
echo ""
echo "注意: 実行時は必ず 'source venv/bin/activate' で仮想環境を有効化してください"
