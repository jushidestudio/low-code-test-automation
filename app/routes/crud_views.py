from flask import Blueprint, request, url_for, jsonify
from app.models import TestCase  # app.models が適切にインポートされていることを確認
from app.extensions import db  # app.extensions が適切にインポートされていることを確認
from datetime import datetime
import os
import subprocess
import re
import logging

# ロガー設定
# logging.basicConfig(level=logging.DEBUG) # create_app() で設定するためコメントアウト
logger = logging.getLogger(__name__)  # __name__ を指定することで、ブループリントごとのログが見やすくなる

crud_views_bp = Blueprint('crud_views', __name__, url_prefix='/crud_views')


# --- 新規追加（モーダル経由） ---
# JavaScriptのFormDataからデータを受け取るため、GETは不要
@crud_views_bp.route('/add-case', methods=['POST'])
def add_case_json():
    # 関数名を add_case_json などに変更すると、既存の add_case.html との混同を防ぎやすい
    try:
        name = request.form['name']
        url = request.form['url']
        code = request.form.get('code', '')  # codeが送られてこない可能性も考慮

        new_case = TestCase(name=name, url=url, code=code)
        db.session.add(new_case)
        db.session.commit()
        logger.info(f"Test case added: ID={new_case.id}, Name={name}")
        return jsonify({
            'success': True, 'message': 'テストケースが正常に追加されました。', 'id': new_case.id
            })
    except Exception as e:
        db.session.rollback()  # エラー時はロールバック
        logger.exception(f"[ERROR] Failed to add test case: {e}")
        return jsonify(
            {'success': False, 'message': f'テストケースの追加中にエラーが発生しました: {str(e)}'}
            ), 500


# --- テストケース編集 - データ取得（モーダル用） ---
# JavaScriptがフォームに初期値をセットするために呼び出すAPI
@crud_views_bp.route('/get-case/<int:case_id>', methods=['GET'])
def get_case_json(case_id):
    case = TestCase.query.get_or_404(case_id)
    return jsonify({
        'id': case.id,
        'name': case.name,
        'url': case.url,
        'code': case.code,
        'created_at': case.created_at.isoformat() if case.created_at else None,
        'updated_at': case.updated_at.isoformat() if case.updated_at else None
    })


# --- テストケース編集 - データ更新（モーダル経由） ---
@crud_views_bp.route('/edit-case/<int:case_id>', methods=['POST'])
def edit_case_json(case_id):  # 関数名を edit_case_json などに変更
    case = TestCase.query.get_or_404(case_id)

    try:
        case.name = request.form['name']
        case.url = request.form['url']
        case.code = request.form.get('code', '')
        case.updated_at = datetime.utcnow()

        db.session.commit()
        logger.info(f"Test case updated: ID={case_id}, Name={case.name}")
        return jsonify(
            {'success': True, 'message': 'テストケースが正常に更新されました。'}
            )
    except Exception as e:
        db.session.rollback()  # エラー時はロールバック
        logger.exception(f"[ERROR] Failed to update test case {case_id}: {e}")
        return jsonify(
            {'success': False, 'message': f'テストケースの更新中にエラーが発生しました: {str(e)}'}
            ), 500


# --- テストケース削除 (既存のコードをそのまま利用) ---
@crud_views_bp.route('/delete_multiple', methods=['POST'])
def delete_multiple_testcases():
    try:
        ids = request.json.get('ids', [])
        if not ids:
            return jsonify({'message': 'IDが指定されていません'}), 400

        deleted_count = 0
        for case_id in ids:
            testcase = TestCase.query.get(case_id)
            if testcase:
                db.session.delete(testcase)
                deleted_count += 1

        db.session.commit()
        logger.info(f"Deleted {deleted_count} test cases: IDs={ids}")
        return jsonify(
            {'message': f'{deleted_count}件のテストケースを削除しました。', 'success': True}
            )  # successキーを追加

    except Exception as e:
        db.session.rollback()  # エラー時はロールバック
        logger.exception(f"[ERROR] delete_multiple_testcases: {e}")
        return jsonify(
            {'message': f'⚠ 削除中にエラーが発生しました: {str(e)}', 'success': False}
            ), 500


# --- テストコード生成画面起動 (既存のコードをそのまま利用) ---
@crud_views_bp.route('/start_codegen', methods=['POST'])
def start_codegen():
    try:
        url = request.form.get("url", "https://google.com")
        command = f"npx playwright codegen --target python {url}"
        logger.debug(f"Executing command: {command}")

        # Popenはノンブロッキングで外部プロセスを開始
        # ここでPopenを使うのは、Playwright codegenがGUIを持つため、バックエンドをブロックしないようにするため
        subprocess.Popen(command, shell=True)

        logger.info(f"Playwright codegen started for URL: {url}")
        return jsonify({
            "status": "started", "message": "Playwright codegenが起動しました。"
            })

    except Exception as e:
        logger.exception(f"[ERROR] Failed to start codegen: {e}")
        return jsonify({
            "status": "error",
            "message": f"コード生成ツール起動中にエラー: {str(e)}",
            'success': False
            }), 500


# --- テスト実行画面起動 (既存のコードをそのまま利用) ---
@crud_views_bp.route('/run', methods=['POST'])
def run_testcase():
    data = request.get_json()
    case_id = data.get('id')
    if not case_id:
        logger.debug("No case_id received.")
        return jsonify({
            'message': 'IDが送信されていません', 'success': False
            }), 400

    testcase = TestCase.query.get(case_id)
    if not testcase or not testcase.code:
        logger.debug(f"Test case {case_id} not found or no code.")
        return jsonify({
            'message': 'テストコードが見つかりません',
            'success': False
            }), 404

    # ファイルパスの安全性を確保
    # case_idをファイル名に含めることで一意性を保ちつつ、悪意のあるパス操作を防ぐ
    safe_case_id = str(case_id)
    temp_file_name = f'test_case_{safe_case_id}.py'
    temp_path = os.path.join('instance', temp_file_name)
    os.makedirs('instance', exist_ok=True)  # instanceディレクトリがなければ作成

    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(testcase.code)

    logger.debug(f"Test code written to: {temp_path}")

    try:
        report_file_name = f'report_case_{safe_case_id}.html'
        report_path = os.path.join('instance', report_file_name)

        # pytestコマンドの構築。os.path.normpath でパスを正規化し、シェルインジェクションのリスクを軽減
        # ただし shell=True を使う場合は常に注意が必要
        command = f"pytest {
            os.path.normpath(temp_path)
            } --html={
                os.path.normpath(report_path)
                } --self-contained-html"

        logger.debug(f"Executing command: {command}")
        logger.debug("Starting subprocess.run...")

        # Pytestの実行結果をキャプチャ
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,  # テキストモードで出力（エンコーディングはシステムデフォルト）
            timeout=180  # タイムアウト
        )

        logger.debug(
            f"Subprocess.run finished. Return code: {result.returncode}"
            )
        logger.debug(f"Subprocess stdout:\n{result.stdout}")
        logger.debug(f"Subprocess stderr:\n{result.stderr}")

        if result.returncode == 0:
            logger.info(f"Test successful for case_id {case_id}.")
            return jsonify({
                'success': True,
                'message': '✅ テスト成功',
                'report_url': url_for(
                    'static', filename=os.path.join(
                        'reports', report_file_name)
                    )  # staticフォルダからの相対パス
            })
        else:
            logger.warning(
                f"Test failed for case_id {case_id}. Return code: {result.returncode}"
                )
            # エラーメッセージから余分なANSIエスケープコードを除去
            clean_stderr = re.sub(r'\x1b\[[0-9;]*m', '', result.stderr)
            clean_stdout = re.sub(r'\x1b\[[0-9;]*m', '', result.stdout)

            return jsonify({
                'success': False,
                'message': f'❌ テスト失敗\n--- stdout ---\n{clean_stdout}\n--- stderr ---\n{clean_stderr}',
                'report_url': url_for('static', filename=os.path.join('reports', report_file_name))
            })

    except subprocess.TimeoutExpired:
        logger.error(f"Test execution timeout for case_id {case_id}.")
        return jsonify({
            'success': False,
            'message': '⏱ 実行がタイムアウトしました。テストプロセスが終了したか確認してください。'
            })
    except Exception as e:
        logger.exception(f"Error running testcase {case_id}: {e}")
        return jsonify({
            'success': False, 'message': f'⚠ エラー: {str(e)}'
            })
