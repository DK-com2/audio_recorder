#!/bin/bash

# 音声デバイス検出・設定スクリプト

echo "=== 音声デバイス診断ツール ==="
echo ""

# システム音声デバイスの確認
echo "1. システム音声デバイス一覧:"
arecord -l 2>/dev/null || echo "arecordコマンドが見つかりません"
echo ""

# PyAudio デバイス一覧
echo "2. PyAudio認識デバイス一覧:"
cd "$(dirname "${BASH_SOURCE[0]}")"
source venv/bin/activate 2>/dev/null

python3 -c "
import pyaudio
import sys

try:
    p = pyaudio.PyAudio()
    print('利用可能な音声デバイス:')
    print('-' * 50)
    
    for i in range(p.get_device_count()):
        try:
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:  # 入力可能なデバイスのみ
                print(f'Index {i}: {info[\"name\"]}')
                print(f'  - 最大入力チャンネル: {info[\"maxInputChannels\"]}')
                print(f'  - デフォルトサンプリング周波数: {info[\"defaultSampleRate\"]}')
                print(f'  - ホストAPI: {info[\"hostApi\"]}')
                print()
        except Exception as e:
            print(f'Index {i}: エラー - {e}')
    
    p.terminate()
    
except Exception as e:
    print(f'PyAudioエラー: {e}')
    print('音声システムの設定を確認してください')
"

echo ""
echo "3. 推奨設定:"
echo "USBマイクを接続している場合は、上記リストから適切なindexを確認し、"
echo "config_changer.shまたはconfig.pyでDEVICE_INDEXを設定してください。"
echo ""
echo "内蔵マイクを使用する場合は、DEVICE_INDEX = 0 を試してください。"
