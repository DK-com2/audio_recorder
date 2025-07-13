# 録音システム

自動録音とGoogle Driveアップロード機能を持つシステムです。

## ファイル構成

```
S:\Documents\audio_recorder\
├── config.py          # 設定ファイル
├── recorder.py        # メイン録音クラス
├── cron_manager.py    # cron管理
├── setup.py           # セットアップスクリプト
├── requirements.txt   # 依存関係
├── README.md          # このファイル
└── recordings\        # 録音ファイル保存先（自動作成）
```

## セットアップ

1. **依存関係のインストール**
```bash
cd "S:\Documents\audio_recorder"
pip install -r requirements.txt
```

2. **初期設定**
```bash
python setup.py
```

3. **Google Drive認証設定**
   - [Google Cloud Console](https://console.cloud.google.com/)で認証情報を作成
   - `client_secrets.json`を作業ディレクトリに配置
   - `config.py`で`UPLOAD_FOLDER_ID`を設定

## 設定変更

`config.py`で以下の設定を変更できます：

- `RECORD_SECONDS`: 録音時間（秒）
- `UPLOAD_FOLDER_ID`: Google Driveの保存先フォルダID
- `DEVICE_INDEX`: マイクのデバイス番号
- `RECORD_DIR`: 録音ファイルの保存先

## 使用方法

### 手動実行
```bash
cd "S:\Documents\audio_recorder"
python recorder.py
```

### Windows タスクスケジューラー設定（cronの代替）

Windows環境ではcronの代わりにタスクスケジューラーを使用します：

1. **タスクスケジューラーを開く**
   - `Win + R` → `taskschd.msc`

2. **基本タスクの作成**
   - 右パネルから「基本タスクの作成」をクリック
   - 名前: "Audio Recorder"
   - 説明: "自動録音システム"

3. **トリガー設定**
   - 毎日/毎週/毎月から選択
   - 開始時刻を設定

4. **操作設定**
   - プログラム/スクリプト: `python`
   - 引数: `"S:\Documents\audio_recorder\recorder.py"`
   - 開始場所: `S:\Documents\audio_recorder`

### cronジョブ管理（Linux/macOS環境）

**cronジョブを追加（毎時0分に実行）:**
```bash
python cron_manager.py add "0 */1 * * *"
```

**cronジョブを削除:**
```bash
python cron_manager.py remove
```

**cronジョブを確認:**
```bash
python cron_manager.py list
```

### スケジュール例

| スケジュール | 説明 |
|-------------|------|
| `0 */1 * * *` | 毎時0分 |
| `0 9 * * *` | 毎日9時 |
| `0 9 * * 1-5` | 平日9時 |
| `*/30 * * * *` | 30分ごと |

## ログ

- メインログ: `S:\Documents\audio_recorder\recorder.log`
- cronログ: `S:\Documents\audio_recorder\recorder_cron.log`

## トラブルシューティング

### マイクが認識されない
1. 以下のコマンドでデバイス一覧を確認：
```python
import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    print(f"{i}: {p.get_device_info_by_index(i)}")
```
2. `config.py`の`DEVICE_INDEX`を適切な値に変更

### Google Drive認証エラー
1. `client_secrets.json`が正しく配置されているか確認
2. 初回実行時にブラウザで認証を完了
3. 認証ファイルの権限を確認

### ffmpegエラー（Windows）
1. [FFmpeg公式サイト](https://ffmpeg.org/download.html)からダウンロード
2. 環境変数PATHに追加
3. または以下でインストール：
```bash
# Chocolateyを使用
choco install ffmpeg

# Scoopを使用
scoop install ffmpeg
```

## 主な機能

- 自動録音（設定可能な時間）
- WAV → MP3変換
- Google Driveへの自動アップロード
- タスクスケジューラー/cronによる定期実行
- 詳細なログ出力
- 設定ファイルによる柔軟な管理
