# auth_helper.py - SSH環境用認証ヘルパー（修正版）
from pydrive2.auth import GoogleAuth

def get_auth_url():
    """認証URLを取得"""
    gauth = GoogleAuth()
    
    # 手動認証モードに設定（refresh_token強制取得）
    gauth.settings = {
        'client_config_backend': 'file',
        'client_config_file': 'client_secrets.json',
        'oauth_scope': ['https://www.googleapis.com/auth/drive'],
        'oauth_redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'get_refresh_token': True
    }
    
    try:
        # 認証URLを取得
        auth_url = gauth.GetAuthUrl()
        print("="*60)
        print("以下のURLをローカルPCのブラウザで開いてください:")
        print(auth_url)
        print("="*60)
        print("認証完了後、ブラウザに表示される認証コードをコピーして入力してください")
        print()
        
        # 認証コードの入力を求める
        auth_code = input("認証コードを入力してください: ").strip()
        
        if not auth_code:
            print("認証コードが入力されていません。")
            return False
        
        # 認証コードで認証
        gauth.Auth(auth_code)
        
        # credentials.jsonを保存
        gauth.SaveCredentialsFile("credentials.json")
        print("認証完了! credentials.jsonが保存されました。")
        return True
        
    except Exception as e:
        print(f"認証エラー: {e}")
        print("もう一度やり直してください。")
        return False

if __name__ == "__main__":
    success = get_auth_url()
    if success:
        print("\n次のステップ:")
        print("./run_recorder.sh を実行して録音・アップロードをテストしてください")
    else:
        print("\n認証に失敗しました。もう一度実行してください。")
