// 依據目前 body 上的 data-language，替語言切換按鈕補上目前狀態 class。
// 主要是讓前台畫面在切換後能更明確地顯示現在使用的是 EN 還是 TH。
document.addEventListener("DOMContentLoaded", () => {
    const currentLanguage = document.body.dataset.language;
    const languageButtons = document.querySelectorAll("[data-lang-button]");

    languageButtons.forEach((button) => {
        if (button.dataset.lang === currentLanguage) {
            button.classList.add("is-active");
        } else {
            button.classList.remove("is-active");
        }
    });
});
