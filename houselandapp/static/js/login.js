const container = document.getElementById("container");
const overlayCon = document.getElementById("overlayCon");
const overlayBtn = document.getElementById("overlayBtn");
const inputs = document.querySelectorAll("input.enter-otp"),
  button = document.querySelector("button.verify");
const getOTPBtn = document.getElementsByName("send-otp");
const phoneIp = document.getElementById("phone");
var value = "";
const myInput = document.getElementsByName("r_password")[0];
var letter = document.getElementById("letter");
var capital = document.getElementById("capital");
var number = document.getElementById("number");
const lPhone = document.getElementById("l_phone");
var length = document.getElementById("length");
var step1 = document.getElementById("step-1");
var step2 = document.getElementById("step-2");
var step3 = document.getElementById("step-3");
const backBtn = document.getElementById("back");
const registerBtn = document.getElementsByName("register")[0];
var temp = 1;

overlayBtn.addEventListener("click", () => {
  container.classList.toggle("right-panel-active");

  overlayBtn.classList.remove("btnScaled");
  window.requestAnimationFrame(() => {
    overlayBtn.classList.add("btnScaled");
  });
});
phoneIp.addEventListener("keypress", (e) => {
  if (phoneIp.value.length > 9) {
    e.preventDefault();
  }
  if (e.key == "-" || e.key == "+" || e.key == "e") {
    e.preventDefault();
  }
  if (phoneIp.value.length == 10) {
    document.getElementById("err-phone").innerHTML = ``;
  }
});

lPhone.addEventListener("keypress", (e) => {
  if (lPhone.value.length > 9) {
    e.preventDefault();
  }
  if (e.key == "-" || e.key == "+" || e.key == "e") {
    e.preventDefault();
  }
});

inputs.forEach((input, index1) => {
  input.addEventListener("keyup", (e) => {
    const currentInput = input,
      nextInput = input.nextElementSibling,
      prevInput = input.previousElementSibling;
    if (currentInput.value.length > 1) {
      currentInput.value = "";
      return;
    }
    if (
      nextInput &&
      nextInput.hasAttribute("disabled") &&
      currentInput.value !== ""
    ) {
      nextInput.removeAttribute("disabled");
      nextInput.focus();
    }
    if (e.key == "Backspace") {
      inputs.forEach((input, index2) => {
        if (index1 <= index2 && prevInput) {
          input.setAttribute("disabled", true);
          currentInput.value = "";
          prevInput.focus();
        }
      });
    }
    if (!inputs[5].disabled && inputs[5].value !== "") {
      button.classList.add("active");
      button.disabled = false;
      return;
    }
    button.classList.remove("active");
    button.disabled = true;
  });
});

myInput.addEventListener("keyup", (e) => {
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

  if (count == 4) {
    getOTPBtn[0].disabled = false;
    getOTPBtn[0].classList.add("active");
  } else {
    getOTPBtn[0].disabled = true;
    getOTPBtn[0].classList.remove("active");
  }
});

getOTPBtn[0].addEventListener("click", () => {
  const password = document.getElementsByName("r_password")[0];
  const r_password = document.getElementsByName("rr_password")[0];

  if (phoneIp.value.length != 10) {
    document.getElementById(
      "err-phone"
    ).innerHTML = `<i class='bx bxs-error'> Lỗi: Số điện thoại không hợp lệ!</i>`;
  } else if (password.value != r_password.value) {
    document.getElementById("err-re-pass").innerHTML = ``;
    document.getElementById("err-pass").innerHTML = ``;
    document.getElementById(
      "err-re-pass"
    ).innerHTML = `<i class='bx bxs-error'> Lỗi: Mật khẩu không khớp!</i>`;
  } else if (password.value == "" || r_password.value == "") {
    document.getElementById("err-phone").innerHTML = ``;
    document.getElementById(
      "err-pass"
    ).innerHTML = `<i class='bx bxs-error'> Lỗi: Mật khẩu trống!</i>`;
  } else if (phoneIp.value.length == 10 && password.value == r_password.value) {
    //aD12dgfgf
    fetch("/api/register/" + phoneIp.value, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        "phone-number": phoneIp.value,
        password: password.value,
        re_password: r_password.value,
        status: 200,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status == 200) {
          temp = 1;
          document.getElementById("err-phone").innerHTML = ``;
          document.getElementById("err-re-pass").innerHTML = ``;
          step1.style.transform = "translateX(-120%)";
          step1.style.opacity = "0";
          step2.style.transform = "translateX(0%)";
          step2.style.opacity = "1";
          step3.style.transform = "translateX(120%)";
          step3.style.opacity = "0";
          inputs[0].focus();
        } else if (data.status == 401) {
          document.getElementById(
            "err-re-pass"
          ).innerHTML = `<i class='bx bxs-error'> Lỗi: Số điện thoại đã tồn tại!</i>`;
        } else if (data.status == 402) {
          document.getElementById(
            "err-re-pass"
          ).innerHTML = `<i class='bx bxs-error'> Mật khẩu không khớp hoặc không đúng định dạng!</i>`;
        } else {
          document.getElementById(
            "err-re-pass"
          ).innerHTML = `<i class='bx bxs-error'> Đã có lỗi xảy ra, vui lòng thử lại!</i>`;
        }
      })
      .catch((err) => {
        console.log(err);
      });
  }
});

backBtn.addEventListener("click", () => {
  step1.style.transform = "translateX(0%)";
  step1.style.opacity = "1";
  step2.style.transform = "translateX(110%)";
  step2.style.opacity = "0";
});

button.addEventListener("click", () => {
  var otpCode = "";
  let action = "back";
  inputs.forEach((input) => {
    otpCode += input.value;
  });
  if (backBtn.textContent == "Hủy") {
    action = "cancel";
    let email = document.getElementsByName("r_email")[0].value;
    const name = document.getElementsByName("r_name")[0].value;
    fetch("/api/verify_otp_code/" + action, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        "phone-number": phoneIp.value,
        email: email,
        name: name,
        "typed-otp": otpCode,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status == 201) {
          document.getElementById(
            "notify"
          ).innerHTML = `<div class="alert alert-success" id="success">
                                                                    Đăng ký thành công! Vui lòng đăng nhập để tiếp tục!
                                                                </div>`;
          socket.emit("handle_notify", {
            type: "register_user",
          });
          setTimeout(function () {
            window.location.reload();
          }, 2000);
        } else {
          document.getElementById(
            "err-otp"
          ).innerHTML = `<i class='bx bxs-error'> Lỗi: Mã xác thực không đúng!</i>`;
        }
      })
      .catch((err) => {
        console.log(err);
      });
  }
  if (backBtn.textContent == "Quay lại") {
    action = "back";
    fetch("/api/verify_otp_code/" + action, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        "phone-number": phoneIp.value,
        "typed-otp": otpCode,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status == 200) {
          step2.style.transform = "translateX(-120%)";
          step2.style.opacity = "0";
          step3.style.transform = "translateX(0%)";
          step3.style.opacity = "1";
          step3.style.zIndex = "2";
        } else {
          document.getElementById(
            "err-otp"
          ).innerHTML = `<i class='bx bxs-error'> Lỗi: Mã xác thực không đúng!</i>`;
        }
      })
      .catch((err) => {
        console.log(err);
      });
  }
});

registerBtn.addEventListener("click", () => {
  const name = document.getElementsByName("r_name")[0].value;
  const email = document.getElementsByName("r_email")[0].value;
  const city = document.getElementById("province");
  fetch("/api/register", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      phone: phoneIp.value,
      name: name,
      email: email,
      city: city.selectedOptions[0].text,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status == 200) {
        step2.style.transform = "translateX(0)";
        step2.style.opacity = "1";
        step3.style.zIndex = "3";
        step3.style.transform = "translateX(120%)";
        step3.style.opacity = "1";
        step3.style.zIndex = "2";
        inputs.forEach((item) => {
          item.value = "";
        });
        document.querySelector("h4").textContent =
          "Xin chào, nhập mã xác thực được gửi vào email của bạn vào ô bên dưới!";
        backBtn.textContent = "Hủy";
        backBtn.name = "cancel";
        backBtn.setAttribute("type", "submit");
        document.getElementById("notify").innerHTML = "";
        document.getElementById("err-otp").innerHTML = "";
      } else {
        document.getElementById(
          "notify"
        ).innerHTML = `<div class="alert alert-danger" id="failed">
                                                                    ${data.message.content}
                                                                </div>`;
      }
    })
    .catch((err) => {
      console.log(err);
    });
});

$(document).keypress(function (event) {
  if (event.which == "13") {
    event.preventDefault();
  }
});

var callAPI = (api) => {
  return axios.get(api).then((response) => {
    renderData(response.data.results, "province");
  });
};
var renderData = (array, select) => {
  let row = `<option selected value="">Chọn khu vực</option>`;
  array.forEach((item) => {
    row += `<option value="${item.province_name}">${item.province_name}</option>`;
  });
  document.querySelector("#" + select).innerHTML = row;
};

callAPI("https://vapi.vnappmob.com/api/province/");

const socket = io({ autoConnect: false });
socket.connect();
socket.on("connect", () => {
    socket.emit("user_join", "I'm connected!");
});