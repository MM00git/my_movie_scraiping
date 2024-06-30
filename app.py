from flask import Flask, jsonify, render_template
from movie_scraper import get_new_movies

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

@app.route('/test_new_movies')
def test_new_movies():
    """
    新作映画情報を取得してJSON形式で返すエンドポイント
    """
    # 新作映画情報を取得
    movies = get_new_movies()
    
    # 映画情報が取得できた場合
    if movies:
        return jsonify(movies)
    else:
        # 取得に失敗した場合
        return jsonify({'error': 'Failed to retrieve new movies'}), 500

@app.route('/')
def index():
    """
    新作映画情報を取得してHTMLテンプレートに渡す
    """
    movies = get_new_movies()
    return render_template('index.html', movies=movies)

if __name__ == '__main__':
    # アプリケーションをデバッグモードで実行
    app.run(debug=True, port=5000)
