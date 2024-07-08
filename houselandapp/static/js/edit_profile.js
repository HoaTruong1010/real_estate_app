var delAvatarPrimary = document.querySelector("button[name='delete-avatar']");
var delAvatarSecondary = document.querySelector("button[name='delete-avatar-btn']");
var delAccount = document.querySelector("button[name='delete-account']");
var registerBtn = document.querySelector("button[name='pre-register']");

if (delAvatarSecondary){
    delAvatarSecondary.addEventListener('click', ()=>{
        let content = 'Xóa avatar này, avatar mặc định sẽ thay thế.\nBạn có đồng ý?';
        if(confirm(content) == true) {
            delAvatarPrimary.click();
        }
    });
}

if (delAccount){
    delAccount.addEventListener('click', ()=>{
        let content = 'Bạn có chắc chắn xóa tài khoản này không?';
        if(confirm(content) == true) {
            let submitDeleteAcc = document.getElementById("del-acc");
            if (submitDeleteAcc) {
                submitDeleteAcc.submit();
            }
            socket.emit("handle_notify", {
                'type': 'delete'
            });
        }
    });
}

if (registerBtn){
    registerBtn.addEventListener('click', ()=>{
        socket.emit("handle_notify", {
            'type': 'register'
        });
        document.querySelector("button[name='register']").click();
    });
}

setTimeout(function() {
    $('.alert-success').fadeOut('fast');
}, 6000);

var editAvatarBtn = document.querySelector("button[name='edit-avatar-btn']");
var editAvatarInput = document.querySelector("input[name='edit-avatar']");
var formAvatar = document.querySelector("form.col-4");

if( editAvatarInput) {
    editAvatarInput.addEventListener('change', ()=>{
        editAvatarBtn.click();
        formAvatar.submit();
    });
}

const myInput = document.getElementsByName("new-password")[0];
if(myInput){
    myInput.addEventListener("keyup", (e) => {
    
        var letter = document.getElementById("letter");
        var capital = document.getElementById("capital");
        var number = document.getElementById("number");
        var length = document.getElementById("length");
        // Validate lowercase letters
        var lowerCaseLetters = /[a-z]/g;
        var count = 0;
        if (myInput.value.match(lowerCaseLetters)) {
            letter.classList.remove("invalid");
            letter.classList.add("valid");
            count++;
        } else {
            letter.classList.remove("valid");
            letter.classList.add("invalid");
            count--;
        }
    
        // Validate capital letters
        var upperCaseLetters = /[A-Z]/g;
        if (myInput.value.match(upperCaseLetters)) {
            capital.classList.remove("invalid");
            capital.classList.add("valid");
            count++;
        } else {
            capital.classList.remove("valid");
            capital.classList.add("invalid");
            count--;
        }
    
        // Validate numbers
        var numbers = /[0-9]/g;
        if (myInput.value.match(numbers)) {
            number.classList.remove("invalid");
            number.classList.add("valid");
            count++;
        } else {
            number.classList.remove("valid");
            number.classList.add("invalid");
            count--;
        }
    
        // Validate length
        if (myInput.value.length >= 8) {
            length.classList.remove("invalid");
            length.classList.add("valid");
            count++;
        } else {
            length.classList.remove("valid");
            length.classList.add("invalid");
            count--;
        }
    })
}

var callAPI = (api) => {
    return axios.get(api).then((response) => {
        renderData(response.data.results, "province");
    });
}
var renderData = (array, select) => {
    let rows = document.getElementById(select), row;
    if (rows) {
        row = rows.selectedOptions[0];
        row.setAttribute("selected", "");
        row = row.outerHTML.toString();
        array.forEach(item => {
            row += `<option value="${item.province_name}">${item.province_name}</option>`
        });
        document.querySelector('#'+select).innerHTML = row;
    }    
}

callAPI('https://vapi.vnappmob.com/api/province/');