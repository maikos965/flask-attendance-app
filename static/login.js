function getDeviceId() {
    let id = localStorage.getItem('deviceId');
    if (!id) {
        id = crypto.randomUUID();
        localStorage.setItem('deviceId', id);
    }
    return id;
}

document.addEventListener("DOMContentLoaded", () => {
    const status = document.getElementById("status");
    const accessButton = document.getElementById("accessButton"); // ボタンを取得
    const deviceId = getDeviceId();

    // ボタンを押したときに処理を実行
    accessButton.addEventListener("click", () => {
        accessButton.disabled = true;  // ボタンを一時的に無効化
        
        fetch('/access', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ deviceId: deviceId })
        })
        .then(res => res.json())
        .then(data => {
            status.textContent = `${data.message}`;
            status.style.color = data.status === 'login' ? 'green' : 'red';
        })
        .catch(err => {
            console.error(err);
            status.textContent = 'エラーが発生しました';
        });
        .finally(() => {
            accessButton.disabled = false;  // 処理が終わったら再有効化
        });
    });

    // ページ読み込み時に自動で処理を行う部分をコメントアウト
    /*
    fetch('/access', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ deviceId: deviceId })
    })
        .then(res => res.json())
        .then(data => {
            status.textContent = `${data.message}`;
            status.style.color = data.status === 'login' ? 'green' : 'red';
        })
        .catch(err => {
            console.error(err);
            status.textContent = 'エラーが発生しました';
        });
    */
});
