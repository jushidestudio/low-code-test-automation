# models.py

# app.pyからdbオブジェクトをインポート
# ここで `app.py` 自身が `models` をインポートするため、循環参照になりますが、
# Flask-SQLAlchemyでは一般的なパターンであり、通常は問題ありません。
# from app import db　←これの影響インポートエラーが発生する？
from app.extensions import db
from datetime import datetime


# Scenario モデルの定義
class TestCase(db.Model):

    # id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(
    # db.Integer, db.ForeignKey('user.id'), nullable=False
    # ) # Userモデルのidを参照
    # name = db.Column(db.String(120), nullable=False)
    # script_json = db.Column(db.Text, nullable=False) # テキスト形式でJSON文字列を保存
    # created_at = db.Column(db.DateTime, default=datetime.utcnow) # 作成日時を自動で記録
    __tablename__ = 'testcases'  # 明示的にテーブル名を指定
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(300), nullable=False)
    code = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
        )

    def __repr__(self):
        return f'<Scenario {self.name}>'
