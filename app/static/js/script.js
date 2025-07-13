// static/js/script.js

// DOMContentLoaded イベントリスナーの追加
// これにより、HTMLの全ての要素が読み込まれてからJavaScriptが実行されます。
document.addEventListener('DOMContentLoaded', function() {

    // --- テストコード生成ボタンの処理 ---
    const generateCodeButton = document.getElementById('generateCodeButton');
    const generateUrlInput = document.getElementById('generateUrl');
    const generatingStatusDiv = document.getElementById('generatingStatus');

    // ボタンの初期テキストを保存しておく（処理終了後に戻すため）
    const originalButtonText = generateCodeButton ? generateCodeButton.innerHTML : '';

    if (generateCodeButton) { // ボタンが存在するか確認
        generateCodeButton.addEventListener('click', async function() {
            const url = generateUrlInput.value || "https://google.com"; // デフォルトURLを設定

            // 処理開始時のUI状態変化
            generateCodeButton.disabled = true; // ボタンを無効化
            generateCodeButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 生成中...'; // スピナーとテキストを表示
            generatingStatusDiv.classList.remove('d-none'); // 処理中メッセージを表示

            try {
                const response = await fetch('/crud_views/start_codegen', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `url=${encodeURIComponent(url)}` // URLエンコードして送信
                });
                const data = await response.json();
                alert(data.message || "処理が完了しました。");
            } catch (error) {
                console.error('Error starting codegen:', error);
                alert('テストコード生成中にエラーが発生しました。');
            } finally {
                // 処理終了時のUI状態変化（成功・失敗問わず）
                generateCodeButton.disabled = false; // ボタンを有効化
                generateCodeButton.innerHTML = originalButtonText; // ボタンのテキストを元に戻す
                generatingStatusDiv.classList.add('d-none'); // 処理中メッセージを非表示
            }
        });
    }

    // --- 新規アイテム追加ボタンの処理 ---
    const openAddModalButton = document.getElementById('openAddModalButton');
    const commonModal = new bootstrap.Modal(document.getElementById('commonModal'));
    const commonModalLabel = document.getElementById('commonModalLabel');
    const commonModalBody = document.getElementById('commonModalBody');
    const commonModalFooter = document.getElementById('commonModalFooter');

    if (openAddModalButton) {
        openAddModalButton.addEventListener('click', function() {
            commonModalLabel.textContent = '新規テストケースを追加';
            commonModalBody.innerHTML = `
                <form id="addEditForm">
                    <div class="mb-3">
                        <label for="caseName" class="form-label">名前</label>
                        <input type="text" class="form-control" id="caseName" name="name" required>
                    </div>
                    <div class="mb-3">
                        <label for="caseUrl" class="form-label">URL</label>
                        <input type="url" class="form-control" id="caseUrl" name="url" required>
                    </div>
                    <div class="mb-3">
                        <label for="caseCode" class="form-label">テストコード</label>
                        <textarea class="form-control" id="caseCode" name="code" rows="10"></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">保存</button>
                </form>
            `;
            commonModalFooter.innerHTML = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">閉じる</button>`;

            // フォームの送信処理
            const addEditForm = document.getElementById('addEditForm');
            addEditForm.addEventListener('submit', async function(event) {
                event.preventDefault(); // デフォルトのフォーム送信を防止

                const formData = new FormData(addEditForm); // フォームデータを取得

                try {
                    const response = await fetch('/crud_views/add-case', { // 新規追加APIエンドポイント
                        method: 'POST',
                        body: formData // FormDataを直接bodyに渡す
                    });
                    const data = await response.json();

                    if (data.success) {
                        alert(data.message);
                        commonModal.hide(); // モーダルを閉じる
                        location.reload(); // ページをリロードしてリストを更新
                    } else {
                        alert('エラー: ' + data.message);
                    }
                } catch (error) {
                    console.error('Error adding case:', error);
                    alert('テストケースの追加中にエラーが発生しました。');
                }
            });

            commonModal.show(); // モーダルを表示
        });
    }


    // --- テストケース一覧の操作 ---
    const itemListTable = document.getElementById('itemListTable');
    const deleteSelectedButton = document.getElementById('deleteSelectedButton');
    const executeSelectedButton = document.getElementById('executeSelectedButton');

    if (itemListTable) {
        // --- 行クリックでチェックボックスを切り替え ---
        itemListTable.addEventListener('click', function(event) {
            const target = event.target;
            const row = target.closest('tr.selectable-row');

            // クリックされた要素がチェックボックス、ボタン、またはリンクでない場合のみ処理
            // ★ここを変更します★
            // ボタンまたはリンクがクリックされた場合は、何もしない（イベントを伝播させる）
            if (target.closest('.btn') || target.tagName.toLowerCase() === 'a' || target.closest('a')) {
                return; // ボタンやリンクがクリックされた場合は処理を中断
            }

            // 行がクリックされ、それがチェックボックス自体でなければ、チェックボックスをトグル
            if (row && !target.classList.contains('form-check-input')) {
                const checkbox = row.querySelector('.item-checkbox');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked; // チェックボックスの状態を反転
                    updateActionButtonStates(); // ボタンの状態を更新
                }
            }
            // チェックボックス自体がクリックされた場合は、ブラウザのデフォルト動作に任せる（ここで改めてトグルしない）
        });

        // --- チェックボックスの状態変更時にボタンの状態を更新 (これは変更なし) ---
        itemListTable.addEventListener('change', function(event) {
            if (event.target.classList.contains('item-checkbox')) {
                updateActionButtonStates();
            }
        });

        // --- 編集ボタンの処理 ---
        itemListTable.addEventListener('click', async function(event) {
            if (event.target.classList.contains('edit-button') || event.target.closest('.edit-button')) {
                const button = event.target.closest('.edit-button');
                const caseId = button.dataset.id; // data-id からIDを取得

                commonModalLabel.textContent = 'テストケースを編集';
                commonModalFooter.innerHTML = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">閉じる</button>`;

                try {
                    // 既存データを取得
                    const response = await fetch(`/crud_views/get-case/${caseId}`);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const caseData = await response.json();

                    commonModalBody.innerHTML = `
                        <form id="addEditForm">
                            <div class="mb-3">
                                <label for="caseName" class="form-label">名前</label>
                                <input type="text" class="form-control" id="caseName" name="name" value="${caseData.name || ''}" required>
                            </div>
                            <div class="mb-3">
                                <label for="caseUrl" class="form-label">URL</label>
                                <input type="url" class="form-control" id="caseUrl" name="url" value="${caseData.url || ''}" required>
                            </div>
                            <div class="mb-3">
                                <label for="caseCode" class="form-label">テストコード</label>
                                <textarea class="form-control" id="caseCode" name="code" rows="10">${caseData.code || ''}</textarea>
                            </div>
                            <button type="submit" class="btn btn-primary">更新</button>
                        </form>
                    `;

                    commonModal.show(); // モーダルを表示

                    // フォームの送信処理 (編集用)
                    const addEditForm = document.getElementById('addEditForm');
                    addEditForm.addEventListener('submit', async function(e) {
                        e.preventDefault();
                        const formData = new FormData(addEditForm);

                        try {
                            const updateResponse = await fetch(`/crud_views/edit-case/${caseId}`, {
                                method: 'POST',
                                body: formData
                            });
                            const updateData = await updateResponse.json();

                            if (updateData.success) {
                                alert(updateData.message);
                                commonModal.hide();
                                location.reload(); // ページをリロードしてリストを更新
                            } else {
                                alert('エラー: ' + updateData.message);
                            }
                        } catch (err) {
                            console.error('Error updating case:', err);
                            alert('テストケースの更新中にエラーが発生しました。');
                        }
                    });

                } catch (error) {
                    console.error('Error fetching case data:', error);
                    alert('テストケースデータの取得中にエラーが発生しました。');
                }
            }
        });

        // --- 削除ボタンの処理（個別削除用） ---
        itemListTable.addEventListener('click', async function(event) {
            if (event.target.classList.contains('delete-button') || event.target.closest('.delete-button')) {
                const button = event.target.closest('.delete-button');
                const caseId = button.dataset.id;

                if (confirm('本当にこのテストケースを削除しますか？')) {
                    try {
                        const response = await fetch('/crud_views/delete_multiple', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ ids: [parseInt(caseId)] }) // IDを配列として送信
                        });
                        const data = await response.json();

                        if (data.success) {
                            alert(data.message);
                            location.reload(); // ページをリロードしてリストを更新
                        } else {
                            alert('エラー: ' + data.message);
                        }
                    } catch (error) {
                        console.error('Error deleting case:', error);
                        alert('テストケースの削除中にエラーが発生しました。');
                    }
                }
            }
        });

        // --- 実行ボタンの処理（個別実行用） ---
        itemListTable.addEventListener('click', async function(event) {
            if (event.target.classList.contains('execute-button') || event.target.closest('.execute-button')) {
                const button = event.target.closest('.execute-button');
                const caseId = button.dataset.id;

                if (confirm('このテストケースを実行しますか？')) {
                    try {
                        const response = await fetch('/crud_views/run', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ id: parseInt(caseId) })
                        });
                        const data = await response.json();

                        alert(data.message); // 結果メッセージを表示

                        if (data.report_url) {
                            // レポートURLがあれば新しいタブで開く
                            window.open(data.report_url, '_blank');
                        }
                    } catch (error) {
                        console.error('Error executing test case:', error);
                        alert('テストケースの実行中にエラーが発生しました。');
                    }
                }
            }
        });

        // --- 「続きを見る」ボタンの処理 (テストコード全文表示) ---
        itemListTable.addEventListener('click', function(event) {
            if (event.target.classList.contains('read-more-code')) {
                const button = event.target;
                const previewDiv = button.closest('.test-code-preview');
                const fullCode = previewDiv.dataset.fullCode; // data-full-codeから全文を取得

                commonModalLabel.textContent = 'テストコード全文';
                commonModalBody.innerHTML = `<pre><code>${fullCode}</code></pre>`;
                commonModalFooter.innerHTML = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">閉じる</button>`;
                commonModal.show();
            }
        });
    } // End of if (itemListTable)


    // --- 複数選択削除ボタンの処理 ---
    if (deleteSelectedButton) {
        deleteSelectedButton.addEventListener('click', async function() {
            const selectedIds = getSelectedCaseIds();
            if (selectedIds.length === 0) {
                alert('削除するテストケースを選択してください。');
                return;
            }

            if (confirm(`${selectedIds.length}件のテストケースを本当に削除しますか？`)) {
                try {
                    const response = await fetch('/crud_views/delete_multiple', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ ids: selectedIds })
                    });
                    const data = await response.json();

                    if (data.success) {
                        alert(data.message);
                        location.reload();
                    } else {
                        alert('エラー: ' + data.message);
                    }
                } catch (error) {
                    console.error('Error deleting multiple cases:', error);
                    alert('複数テストケースの削除中にエラーが発生しました。');
                }
            }
        });
    }

    // --- 複数選択実行ボタンの処理 ---
    if (executeSelectedButton) {
        executeSelectedButton.addEventListener('click', async function() {
            const selectedIds = getSelectedCaseIds();
            if (selectedIds.length === 0) {
                alert('実行するテストケースを選択してください。');
                return;
            }

            if (confirm(`${selectedIds.length}件のテストケースを本当に実行しますか？`)) {
                // 複数実行の場合は、個別に実行APIを呼び出すか、新しい一括実行APIを作る必要があります
                // ここでは簡易的に、選択された各テストケースに対して実行APIを呼び出す例
                for (const caseId of selectedIds) {
                    try {
                        const response = await fetch('/crud_views/run', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ id: caseId })
                        });
                        const data = await response.json();
                        alert(`ID ${caseId} のテスト結果: ${data.message}`);
                        if (data.report_url) {
                            window.open(data.report_url, '_blank');
                        }
                    } catch (error) {
                        console.error(`Error executing test case ${caseId}:`, error);
                        alert(`ID ${caseId} のテスト実行中にエラーが発生しました。`);
                    }
                }
                location.reload(); // 完了後にリロード（必要に応じて）
            }
        });
    }


    // --- ヘルパー関数 ---

    // 選択されたテストケースのIDを取得する関数
    function getSelectedCaseIds() {
        const checkboxes = document.querySelectorAll('.item-checkbox:checked');
        return Array.from(checkboxes).map(cb => parseInt(cb.id.replace('checkbox-', '')));
    }

    // 複数選択/実行ボタンの有効/無効を切り替える関数
    function updateActionButtonStates() {
        const selectedCount = getSelectedCaseIds().length;
        if (deleteSelectedButton) {
            deleteSelectedButton.disabled = selectedCount === 0;
        }
        if (executeSelectedButton) {
            executeSelectedButton.disabled = selectedCount === 0;
        }
    }

    // 初期ロード時にボタンの状態を更新 (ページ遷移でリセットされるため)
    updateActionButtonStates();

}); // End of DOMContentLoaded