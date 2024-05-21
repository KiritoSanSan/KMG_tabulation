// console.log('hello world')

// const spinnerBox = document.getElementById('spinner-box')
// const dataBox = document.getElementById('data-box')

// console.log(spinnerBox)
// console.log(dataBox)

//ncalayer.js
var webSocket = new WebSocket('wss://127.0.0.1:13579/');
var callback = null;

function blockScreen() {
    $.blockUI({
        message: '<img src="js/loading.gif" /><br/>Подождите, выполняется операция в NCALayer...',
        css: {
            border: 'none',
            padding: '15px',
            backgroundColor: '#000',
            '-webkit-border-radius': '10px',
            '-moz-border-radius': '10px',
            opacity: .5,
            color: '#fff'
        }
    });
}

function openDialog() {
    if (confirm("Ошибка при подключении к NCALayer. Запустите NCALayer и нажмите ОК") === true) {
        location.reload();
    }
}
function unblockScreen() {
    $.unblockUI();
}
webSocket.onopen = function (event) {
    console.log("Connection opened");
};

webSocket.onclose = function (event) {
    if (event.wasClean) {
        console.log('connection has been closed');
    } else {
        console.log('Connection error');
        openDialog();
    }
    console.log('Code: ' + event.code + ' Reason: ' + event.reason);
};

function createCAdESFromBase64(storageName, keyType, base64ToSign, flag, callBack) {
    var createCAdESFromBase64 = {
		"module": "kz.gov.pki.knca.commonUtils",
        "method": "createCAdESFromBase64",
        "args": [storageName, keyType, base64ToSign, flag]
    };
    callback = callBack;
    webSocket.send(JSON.stringify(createCAdESFromBase64));
}
