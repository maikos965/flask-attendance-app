document.addEventListener("DOMContentLoaded", () => {
    const countElement = document.getElementById("count");

    // 入室人数を取得
    fetch('/count')
        .then(res => res.json())
        .then(data => {
            countElement.textContent = `現在の入室人数: ${data.count}人`;
        })
        .catch(err => {
            console.error(err);
            countElement.textContent = 'エラーが発生しました';
        });
});