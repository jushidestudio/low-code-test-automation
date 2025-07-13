# app/__init__.py

from flask import Flask, send_from_directory # send_from_directory を追加
import logging
import os # osモジュールを追加

from flask_moment import Moment
# from flask_sqlalchemy import SQLAlchemy # コメントアウトされているのでそのまま
# from flask_login import LoginManager # コメントアウトされているのでそのまま

# 拡張機能は extensions.py からインポートする
from .extensions import db

# モデルは __init__.py でインポートする
from .models import TestCase

# 各Blueprintをインポート（名前が正しいことを確認）
from .routes.main import main_bp
from .routes.crud_views import crud_views_bp


def create_app():
    # Flaskアプリケーションのインスタンスを作成する際に、static_folder を明示的に指定
    # os.path.abspath(os.path.dirname(__file__)) は現在のファイル（__init__.py）のディレクトリパス（つまり app ディレクトリのパス）を取得
    # os.path.join でそのパスに 'static' を結合し、app/static を静的ファイルのルートとして指定
    app = Flask(__name__, static_folder=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static'))

    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testcases.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 拡張機能をアプリケーションに紐付ける
    db.init_app(app)

    # config.py から設定を読み込む
    app.config.from_pyfile('config.py')

    # ログ設定
    if app.config["ENV"] == "production":
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)

    # Flask-Moment の初期化
    moment = Moment(app)

    # アプリケーションコンテキスト内でデータベースを初期化 (初回起動時やテーブルがない場合)
    with app.app_context():
        db.create_all()

    # Blueprintを登録
    app.register_blueprint(crud_views_bp)
    app.register_blueprint(main_bp) # main_bpはホームページなので通常は登録
    # instance フォルダ内のレポートファイルを /reports/ URLで公開する設定
    # これにより、生成された pytest HTML レポートをブラウザで表示できるようになります
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # 開発中にキャッシュを無効にするため
    app.add_url_rule(
        '/reports/<path:filename>',
        endpoint='reports_static', # エンドポイント名を指定
        view_func=lambda filename: send_from_directory(app.instance_path, filename)
    )

    return app