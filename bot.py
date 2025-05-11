import requests
import json
import time
import urllib.parse
from colorama import init, Fore, Style

# Coloramaを初期化してターミナルに色を付ける
init()

# 設定
BASE_URL = "https://game-backend-v2.auraxterminal.com/api/v1"
REFERRAL_CODE = "kent6004380466"  # リファラルコード

# ヘッダー
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "origin": "https://game-frontend-v2.auraxterminal.com",
    "pragma": "no-cache",
    "referer": "https://game-frontend-v2.auraxterminal.com/",
    "sec-ch-ua": '"Microsoft Edge";v="136", "Microsoft Edge WebView2";v="136", "Not.A/Brand";v="99", "Chromium";v="136"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
}

# 色付きのログ
def log_success(message):
    print(f"{Fore.GREEN}[成功] {message}{Style.RESET_ALL}")

def log_error(message):
    print(f"{Fore.RED}[エラー] {message}{Style.RESET_ALL}")

def log_warning(message):
    print(f"{Fore.YELLOW}[警告] {message}{Style.RESET_ALL}")

# Banner
def display_banner():
    banner = (
        "╔══════════════════════════════════════════════╗\n"
        "║       🌟 AURAX BOT - Automated Tasks         ║\n"
        "║ Automate your Aurax Terminal tasks: daily    ║\n"
        "║ check-in, token-rain, and factory work!      ║\n"
        "║ Developed by: https://t.me/sentineldiscus    ║\n"
        "╚══════════════════════════════════════════════╝"
    )
    print(f"{Fore.CYAN}{banner}{Style.RESET_ALL}")

# data.txtからinitデータを読み込む関数
def read_init_data():
    try:
        with open("data.txt", "r") as file:
            lines = [line.strip() for line in file.readlines() if line.strip() and line.startswith("user=")]
        if not lines:
            log_error("data.txtが空か、有効なinitデータがありません。")
            return []
        return lines
    except FileNotFoundError:
        log_error("data.txtが見つかりません。")
        return []
    except Exception as e:
        log_error(f"data.txtの読み込みに失敗しました: {str(e)}")
        return []

# data.jsonからトークンを読み込む関数
def read_tokens():
    try:
        with open("data.json", "r") as file:
            tokens = json.load(file)
        return {token["user_id"]: token["token"] for token in tokens}
    except FileNotFoundError:
        return {}
    except Exception as e:
        log_error(f"data.jsonの読み込みに失敗しました: {str(e)}")
        return {}

# data.jsonにトークンを保存する関数
def save_token(user_id, token):
    try:
        tokens = []
        try:
            with open("data.json", "r") as file:
                tokens = json.load(file)
        except FileNotFoundError:
            pass

        # トークンを更新または追加
        tokens = [t for t in tokens if t["user_id"] != user_id]
        tokens.append({"user_id": user_id, "token": token})
        with open("data.json", "w") as file:
            json.dump(tokens, file, indent=4)
        log_success(f"user_id {user_id}のトークンをdata.jsonに保存しました！")
    except Exception as e:
        log_error(f"data.jsonへのトークン保存に失敗しました: {str(e)}")

# クエリからuser_idを抽出
def parse_init_data(init_data):
    try:
        parsed_data = urllib.parse.parse_qs(init_data)
        user_str = parsed_data.get("user", [None])[0]
        if not user_str:
            log_error("init_dataにuserが見つかりません。")
            return None
        user_data = json.loads(urllib.parse.unquote(user_str))
        user_id = user_data.get("id")
        if not user_id:
            log_error("init_dataにuser_idが見つかりません。")
            return None
        return str(user_id)
    except Exception as e:
        log_error(f"init_dataの解析に失敗しました: {str(e)}")
        return None

# トークンを取得する関数
def get_auth_token(init_data):
    url = f"{BASE_URL}/auth/web-app"
    payload = {
        "init_data": init_data,
        "referral_code": REFERRAL_CODE
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            token = response.json().get("token")
            if token:
                log_success("トークンを取得しました！")
                return f"Bearer {token}"
            else:
                log_error("レスポンスにトークンが見つかりません。")
                return None
        else:
            log_warning("init_dataが無効です。data.jsonからトークンを試します...")
            return None
    except Exception as e:
        log_error(f"トークンの取得に失敗しました: {str(e)}")
        return None

# トークンの検証
def validate_token(user_id, token):
    headers["authorization"] = token
    url = f"{BASE_URL}/users/{user_id}/daily/claim"
    payload = {}
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.status_code == 201
    except Exception:
        return False

# デイリーチェックイン
def daily_check_in(user_id, token):
    headers["authorization"] = token
    url = f"{BASE_URL}/users/{user_id}/daily/claim"
    payload = {}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            log_success("チェックインに成功しました！")
        else:
            log_error("チェックインに失敗しました。")
    except Exception as e:
        log_error(f"チェックインに失敗しました: {str(e)}")

# トークンレインゲームをプレイ
def start_token_rain(user_id, token):
    headers["authorization"] = token
    url = f"{BASE_URL}/users/{user_id}/games/token-rain/start"
    payload = {}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            log_success("トークンレインゲームを開始しました！")
            return response.json()
        else:
            log_error("トークンレインゲームの開始に失敗しました。")
            return None
    except Exception as e:
        log_error(f"ゲームの開始に失敗しました: {str(e)}")
        return None

# リワードを請求
def claim_token_rain(user_id, token, attempt_id, points):
    headers["authorization"] = token
    url = f"{BASE_URL}/users/{user_id}/games/token-rain/claim"
    payload = {
        "attempt_id": attempt_id,
        "points": [
            {"currency": point["currency"], "points_amount": point["points"]}
            for point in points
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            log_success("リワードの請求に成功しました！")
        else:
            log_error("リワードの請求に失敗しました。")
    except Exception as e:
        log_error(f"リワードの請求に失敗しました: {str(e)}")

# アクティビティ（工場での作業）を実行
def do_activity(user_id, token):
    headers["authorization"] = token
    url = f"{BASE_URL}/users/{user_id}/activity"
    payload = {"type": "work", "section": "factory"}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            log_success("アクティビティ（工場作業）に成功しました！")
        else:
            log_error("アクティビティに失敗しました。")
    except Exception as e:
        log_error(f"アクティビティに失敗しました: {str(e)}")

# 1つのアカウントを処理
def process_account(init_data, account_index):
    log_warning(f"アカウント {account_index} を処理中...")
    user_id = parse_init_data(init_data)
    if not user_id:
        log_error(f"アカウント {account_index}: user_idの取得に失敗しました。")
        return

    # init_dataからトークンを取得
    token = get_auth_token(init_data)
    if token:
        save_token(user_id, token.split(" ")[1])  # "Bearer"なしでトークンを保存
    else:
        # data.jsonにフォールバック
        tokens = read_tokens()
        token = tokens.get(user_id)
        if token:
            token = f"Bearer {token}"
            if validate_token(user_id, token):
                log_success(f"user_id {user_id} のdata.jsonからトークンを使用します！")
            else:
                log_error(f"アカウント {account_index}: data.jsonのトークンが無効です。")
                log_warning("data.txtのinit_dataを更新してください。取得方法：")
                log_warning("1. TelegramでAuraxのウェブアプリを開きます。")
                log_warning("2. ブラウザの開発者ツール（F12）を使用して、/auth/web-appへのリクエストを確認します。")
                log_warning("3. init_dataをコピーしてdata.txtに追加します（1行に1つ）。")
                return
        else:
            log_error(f"アカウント {account_index}: data.jsonにトークンがありません。")
            log_warning("data.txtのinit_dataを更新してください。取得方法：")
            log_warning("1. TelegramでAuraxのウェブアプリを開きます。")
            log_warning("2. ブラウザの開発者ツール（F12）を使用して、/auth/web-appへのリクエストを確認します。")
            log_warning("3. init_dataをコピーしてdata.txtに追加します（1行に1つ）。")
            return

    daily_check_in(user_id, token)
    time.sleep(3)  # 待機
    do_activity(user_id, token)
    time.sleep(3)  # 待機
    start_response = start_token_rain(user_id, token)
    if start_response:
        attempt_id = start_response.get("attempt_id")
        points = start_response.get("points", [])
        if attempt_id and points:
            claim_token_rain(user_id, token, attempt_id, points)
        else:
            log_error(f"アカウント {account_index}: attempt_idまたはpointsの取得に失敗しました。")

# メイン関数
def main():
    while True:
        display_banner()
        init_data_list = read_init_data()
        if not init_data_list:
            log_warning("処理するアカウントがありません。7時間後に再試行します...")
            time.sleep(25200)  # 7時間
            continue

        for index, init_data in enumerate(init_data_list, 1):
            process_account(init_data, index)
            if index < len(init_data_list):
                log_warning("次のアカウントを処理する前に5秒待機します...")
                time.sleep(5)  # アカウント間の待機

        log_warning("すべてのアカウントの処理が完了しました。次の繰り返しまで7時間待機します...")
        time.sleep(25200)  # 7時間（秒）

if __name__ == "__main__":
    main()
