function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');







function createCAdESFromBase64Call() {
    $.blockUI();
    const userConfirmed = confirm("Вы уверены, что хотите согласовать График?");
    if (userConfirmed) {
        var selectedStorage = $('#storageSelect').val();
        var flag = $("#flagForBase64").is(':checked');
        var base64ToSign = $("#base64ToSign").val();
        if (base64ToSign !== null && base64ToSign !== "") {
            
            createCAdESFromBase64(selectedStorage, "SIGNATURE", base64ToSign, flag, "createCAdESFromBase64Back");
        } else {
            alert("Нет данных для подписи!");
        }
    }
}




function createCAdESFromBase64Back(result) {
	$.unblockUI();
    // if (result['code'] === "500") {
    //     alert(result['message']);
    // } else if (result['code'] === "200") {
        var res = result['responseObject'];
        $("#createdCMSforBase64").val(res);
        fetch(tabelAdminUrl, {
            method: "POST",
            headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ cms: res })
        })
    }
// }
function getKeyInfoCall() {
    blockScreen();
    var selectedStorage = $('#storageSelect').val();
    var flag = $("#flagForBase64").is(':checked');
    var base64ToSign = $("#base64ToSign").val();
    var selectedStorage = $('#storageSelect').val();
    // getKeyInfo(selectedStorage, "getKeyInfoBack");
    // createCAdESFromBase64(selectedStorage, "SIGNATURE", base64ToSign, flag, "createCAdESFromBase64Back");
}
// const graphAdminUpdateChangeList = "{%url 'admin:tabel_tabel_changelist' %}"

function getKeyInfoBack(result) {
    unblockScreen();
    
    if (result['code'] === "500") {
        // alert(result['message']+'');
        alert('Ошибка при получении информации о ключе!');
    } else if (result['code'] === "200") {
        var res = result['responseObject'];
        var subjectDn = res['subjectDn'];
        $("#subjectDn").val(subjectDn);
        
        // Send the subjectDn value to the server
        fetch(graphAdminUrl, {
            method: "POST",
            headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify({ subjectDn: subjectDn })
        }).then(response => {
            var selectedStorage = $('#storageSelect').val();
            var flag = $("#flagForBase64").is(':checked');
            var base64ToSign = $("#base64ToSign").val();
            if (base64ToSign !== null && base64ToSign !== "") {
                
                // $.blockUI();
                createCAdESFromBase64(selectedStorage, "SIGNATURE", base64ToSign, flag, "createCAdESFromBase64Back");
            } else {
                alert("Нет данных для подписи!");
            }
        })

    }
}











function getActiveTokensCall() {
    blockScreen();
	getActiveTokens("getActiveTokensBack");
}

function getActiveTokensBack(result) {
    unblockScreen();
    if (result['code'] === "500") {
        alert(result['message']);
    } else if (result['code'] === "200") {
        var listOfTokens = result['responseObject'];        
        $('#storageSelect').empty();
        $('#storageSelect').append('<option value="PKCS12">PKCS12</option>');
        for (var i = 0; i < listOfTokens.length; i++) {
            $('#storageSelect').append('<option value="' + listOfTokens[i] + '">' + listOfTokens[i] + '</option>');
        }
    }
}
// function signXmlCall() {
//     var xmlToSign = $("#xmlToSign").val();
//     var selectedStorage = $('#storageSelect').val();
// 	blockScreen();
//     signXml(selectedStorage, "SIGNATURE", xmlToSign, "signXmlBack");
// }

// function signXmlBack(result) {
// 	unblockScreen();
//     if (result['code'] === "500") {
//         alert(result['message']);
//     } else if (result['code'] === "200") {
//         var res = result['responseObject'];
//         $("#signedXml").val(res);
//     }
// }

// function signXmlsCall() {
//     var xmlToSign1 = $("#xmlToSign1").val();
// 	var xmlToSign2 = $("#xmlToSign2").val();
// 	var xmlsToSign = new Array(xmlToSign1, xmlToSign2);
// 	var selectedStorage = $('#storageSelect').val();
// 	blockScreen();
// 	signXmls(selectedStorage, "SIGNATURE", xmlsToSign, "signXmlsBack");
// }

// function signXmlsBack(result) {
// 	unblockScreen();
//     if (result['code'] === "500") {
//         alert(result['message']);
//     } else if (result['code'] === "200") {
//         var res = result['responseObject'];
//         $("#signedXml1").val(res[0]);
// 		$("#signedXml2").val(res[1]);
//     }
// }

// function createCAdESFromFileCall() {
//     var selectedStorage = $('#storageSelect').val();
//     var flag = $("#flag").is(':checked');
//     var filePath = $("#filePath").val();
//     if (filePath !== null && filePath !== "") {
// 		blockScreen();
//         createCAdESFromFile(selectedStorage, "SIGNATURE", filePath, flag, "createCAdESFromFileBack");
//     } else {
//         alert("Не выбран файл для подписи!");
//     }
// }

// function createCAdESFromFileBack(result) {
// 	unblockScreen();
//     if (result['code'] === "500") {
//         alert(result['message']);
//     } else if (result['code'] === "200") {
//         var res = result['responseObject'];
//         $("#createdCMS").val(res);
//     }
// }




// function createCAdESFromBase64HashCall() {
//     var selectedStorage = $('#storageSelect').val();
//     var base64ToSign = $("#base64HashToSign").val();
//     if (base64ToSign !== null && base64ToSign !== "") {
// 		$.blockUI();
//         createCAdESFromBase64Hash(selectedStorage, "SIGNATURE", base64ToSign, "createCAdESFromBase64HashBack");
//     } else {
//         alert("Нет данных для подписи!");
//     }
// }

// function createCAdESFromBase64HashBack(result) {
// 	$.unblockUI();
//     if (result['code'] === "500") {
//         alert(result['message']);
//     } else if (result['code'] === "200") {
//         var res = result['responseObject'];
//         $("#createdCMSforBase64Hash").val(res);
//     }
// }

// function applyCAdESTCall() {
//     var selectedStorage = $('#storageSelect').val();
//     var cmsForTS = $("#CMSForTS").val();
//     if (cmsForTS !== null && cmsForTS !== "") {
// 		$.blockUI();
//         applyCAdEST(selectedStorage, "SIGNATURE", cmsForTS, "applyCAdESTBack");
//     } else {
//         alert("Нет данных для подписи!");
//     }
// }

// function applyCAdESTBack(result) {
// 	$.unblockUI();
//     if (result['code'] === "500") {
//         alert(result['message']);
//     } else if (result['code'] === "200") {
//         var res = result['responseObject'];
//         $("#createdCMSWithAppliedTS").val(res);
//     }
// }

function showFileChooserCall() {
    blockScreen();
    showFileChooser("ALL", "", "showFileChooserBack");
}

function showFileChooserBack(result) {
    unblockScreen();
    if (result['code'] === "500") {
        alert(result['message']);
    } else if (result['code'] === "200") {
        var res = result['responseObject'];
        $("#filePath").val(res);
    }
}

// function showFileChooserForTSCall() {
//     blockScreen();
//     showFileChooser("ALL", "", "showFileChooserForTSBack");
// }

// function showFileChooserForTSBack(result) {
//     unblockScreen();
//     if (result['code'] === "500") {
//         alert(result['message']);
//     } else if (result['code'] === "200") {
//         var res = result['responseObject'];
//         $("#filePathWithTS").val(res);
//     }
// }

// function changeLocaleCall() {
//     var selectedLocale = $('#localeSelect').val();
//     changeLocale(selectedLocale);
// }

function createCMSSignatureFromFileCall() {
    var selectedStorage = $('#storageSelect').val();
    var flag = $("#flagForCMSWithTS").is(':checked');
    var filePath = $("#filePathWithTS").val();
    if (filePath !== null && filePath !== "") {
		blockScreen();
        createCMSSignatureFromFile(selectedStorage, "SIGNATURE", filePath, flag, "createCMSSignatureFromFileBack");
    } else {
        alert("Не выбран файл для подписи!");
    }
}

function createCMSSignatureFromFileBack(result) {
	unblockScreen();
    if (result['code'] === "500") {
        alert(result['message']);
    } else if (result['code'] === "200") {
        var res = result['responseObject'];
        $("#createdCMSWithTS").val(res);
    }
}

function createCMSSignatureFromBase64Call() {
    var selectedStorage = $('#storageSelect').val();
    var flag = $("#flagForBase64WithTS").is(':checked');
    var base64ToSign = $("#base64ToSignWithTS").val();
    if (base64ToSign !== null && base64ToSign !== "") {
		$.blockUI();
        createCMSSignatureFromBase64(selectedStorage, "SIGNATURE", base64ToSign, flag, "createCMSSignatureFromBase64Back");
    } else {
        alert("Нет данных для подписи!");
    }
}

function createCMSSignatureFromBase64Back(result) {
	$.unblockUI();
    if (result['code'] === "500") {
        alert(result['message']);
    } else if (result['code'] === "200") {
        var res = result['responseObject'];
        $("#createdCMSforBase64WithTS").val(res);
    }
}

