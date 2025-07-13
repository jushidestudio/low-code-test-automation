# app/routes/auth.py の修正案
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify, send_from_directory
from ..extensions import db# 修正: 親ディレクトリのextensionsをインポート
from datetime import datetime
from ..models import TestCase

main_bp = Blueprint('main', __name__,)


@main_bp.route('/')
def index():
    """
    ホームページを表示し、データベースに登録されているテストケースの一覧も表示する。
    """
    test_cases = TestCase.query.all() # データベースからすべてのテストケースを取得
    return render_template('index.html', test_cases=test_cases)

@main_bp.route('/reports/<path:filename>')
def serve_report(filename):
    return send_from_directory('instance', filename)
# 必要に応じて、他のルートもここに定義できます
# 例: @main_bp.route('/about')
# def about():
#     return render_template('about.html')
@main_bp.route('/help')
def help_page():
    return render_template('help.html')

@main_bp.route('/about')
def usage_page():
    return render_template('about.html') # ファイル名が '利用について.html' ならばそのままでも良いが、about.htmlが推奨