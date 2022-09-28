var myCloseWindow;
function openWin() {
    myCloseWindow = window.open( url , "myWindow", "width=200, height=100");
    setTimeout(closeWin, 1000);
}

function closeWin() {
    myCloseWindow.close();
}