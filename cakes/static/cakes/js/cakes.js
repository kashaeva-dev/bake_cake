let tg = window.Telegram.WebApp;

tg.expand();

tg.MainButton.textColor = "#FFFFFF";
tg.MainButton.color = "#2cab37";

let selectedCake = "";

console.log('js is working 3');

document.addEventListener('DOMContentLoaded', function() {

    const selectButtons = document.querySelectorAll('.select-button');

    selectButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const cakeId = button.dataset.cakeId;
            if (tg.MainButton.isVisible) {
                tg.MainButton.hide();
            }
            else {
                tg.MainButton.setText("Продолжить оформление заказа");
                tg.MainButton.show();
            }
            selectedCake = cakeId;
            console.log('Selected cake:', selectedCake);
        });
    });

});

Telegram.WebApp.onEvent("mainButtonClicked", function(){
    tg.sendData(selectedCake);
});
