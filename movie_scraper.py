import requests
from config import TMDB_ACCESS_TOKEN
import json
from datetime import datetime, timedelta
import pytz
from PIL import Image
from io import BytesIO

def resize_image(image, size=(500, 750)):
    """
    画像を指定したサイズにリサイズする
    """
    return image.resize(size, Image.ANTIALIAS)

def save_image(image, path):
    """
    画像を指定したパスに保存する
    """
    image.save(path, format='JPEG')

def get_new_movies():
    # 日本時間のタイムゾーンを取得
    JST = pytz.timezone('Asia/Tokyo')
    
    # 現在の年と月を日本時間で取得
    now = datetime.now(JST)
    current_year = now.year
    current_month = now.month
    
    # 月の初日と末日を取得
    start_date = datetime(current_year, current_month, 1).date()
    if current_month == 12:
        end_date = datetime(current_year + 1, 1, 1).date()
    else:
        end_date = datetime(current_year, current_month + 1, 1).date()
    
    # TMDB APIのエンドポイントURL
    base_url = (f'https://api.themoviedb.org/3/discover/movie?language=ja-JP'
                f'&primary_release_date.gte={start_date}'
                f'&primary_release_date.lte={end_date}'
                '&sort_by=release_date.desc'
                '&page=')
    
    # APIリクエストのヘッダーにアクセストークンをセット
    headers = {
        'Authorization': f'Bearer {TMDB_ACCESS_TOKEN}'
    }
    
    movies = []
    page = 1
    total_pages = 1
    
    # 全ページを取得するためにループ
    while page <= total_pages:
        # ページごとにリクエストURLを更新
        url = base_url + str(page)
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            total_pages = data['total_pages']  # 総ページ数を更新
            
            # 各映画情報を取り出し、必要なデータをリストに追加
            for movie in data['results']:
                poster_path = movie['poster_path']
                if poster_path:
                    full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                    # 画像をダウンロード
                    response = requests.get(full_poster_url)
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        resized_image = resize_image(image)
                        image_filename = f"posters/{movie['id']}.jpg"
                        save_image(resized_image, image_filename)
                    else:
                        image_filename = f"img/NoPhoto_image.jpg"
                else:
                    image_filename = f"img/NoPhoto_image.jpg"
                
                movie_info = {
                    'title': movie['title'],                 # 作品タイトル
                    'overview': movie['overview'],           # あらすじ
                    'release_date': movie['release_date'],   # 公開日
                    'poster_path': image_filename,           # 保存されたポスター画像のパス
                    'genre': get_genre_names(movie['genre_ids'])  # ジャンル名
                }
                movies.append(movie_info)
            
            page += 1
        else:
            break
    
    # 公開日順にソート
    sorted_movies = sorted(movies, key=lambda x: x['release_date'])
    
    # データをJSONファイルに書き出す（初期化処理を含む）
    with open('new_movies.json', 'w', encoding='utf-8') as json_file:
        json.dump(sorted_movies, json_file, ensure_ascii=False, indent=4)
    
    return sorted_movies

def get_genre_names(genre_ids):
    """
    ジャンルIDリストからジャンル名を取得
    """
    genre_mapping = {
        28: 'アクション',
        12: 'アドベンチャー',
        16: 'アニメーション',
        35: 'コメディ',
        80: '犯罪',
        99: 'ドキュメンタリー',
        18: 'ドラマ',
        10751: 'ファミリー',
        14: 'ファンタジー',
        36: '歴史',
        27: 'ホラー',
        10402: '音楽',
        9648: 'ミステリー',
        10749: 'ロマンス',
        878: 'サイエンスフィクション',
        10770: 'テレビ映画',
        53: 'スリラー',
        10752: '戦争',
        37: '西部劇'
    }
    # ジャンルIDからジャンル名に変換
    genre_names = [genre_mapping.get(id, 'Unknown') for id in genre_ids]
    return ', '.join(genre_names)

# 新しい映画情報を取得してJSONファイルにエクスポート
movies = get_new_movies()
