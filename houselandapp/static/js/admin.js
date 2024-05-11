document.addEventListener("DOMContentLoaded", () => {
  var li, span, newNumber;
  const menu = document.querySelectorAll(
    "#admin-navbar-collapse ul.mr-auto li"
  );
  const socket = io({ autoConnect: false });
  if (userBadge == "False") {
    li = menu[1];
    span = li.querySelector("span");
    if (!span) {
      aTag = li.querySelector("a");
      aTag.classList.add("pin__parent");
      aTag.innerHTML = `Tài khoản <span class="badge text-danger badge-dot pin-header">
                                <i class="bg-danger pin__child" ></i>
                            </span></a>`;
    }
  } else {
    li = menu[1];
    span = li.querySelector("span");
    if (span) {
      aTag = li.querySelector("a");
      aTag.innerHTML = `Tài khoản`;
    }
  }

  if (postsBadge > 0) {
    li = menu[2];
    span = li.querySelector("span");
    if (!span) {
      aTag = li.querySelector("a");
      aTag.classList.add("pin__parent");
      aTag.innerHTML = `Tin đăng <span class="badge text-danger badge-dot pin-header">
                                <i class="bg-danger pin__child" ></i>
                            </span></a>`;
    }
  } else {
    li = menu[2];
    span = li.querySelector("span");
    if (span) {
      aTag = li.querySelector("a");
      aTag.innerHTML = `Tin đăng`;
    }
  }

  if (reportBadge > 0) {
    li = menu[3];
    span = li.querySelector("span");
    if (!span) {
      aTag = li.querySelector("a");
      aTag.classList.add("pin__parent");
      aTag.innerHTML = `Báo cáo <span class="badge text-danger badge-dot pin-header">
                                <i class="bg-danger pin__child" ></i>
                            </span></a>`;
    }
  } else {
    li = menu[3];
    span = li.querySelector("span");
    if (span) {
      aTag = li.querySelector("a");
      aTag.innerHTML = `Báo cáo`;
    }
  }

  if (chatBadge > 0) {
    li = menu[4];
    span = li.querySelector("span");
    if (!span) {
      aTag = li.querySelector("a");
      aTag.classList.add("pin__parent");
      aTag.innerHTML = `Tin nhắn <span class="badge text-danger badge-dot pin-header">
                                <i class="bg-danger pin__child" ></i>
                            </span></a>`;
    }
  } else {
    li = menu[4];
    span = li.querySelector("span");
    if (span) {
      aTag = li.querySelector("a");
      aTag.innerHTML = `Tin nhắn`;
    }
  }

  socket.connect();
  socket.on("connect", () => {
    socket.emit("user_join", "I'm connected!");
  });

  socket.on("handle_notify", (data) => {
    if (data.type == "delete") {
      li = menu[1];
      span = li.querySelector("span");
      if (!span) {
        aTag = li.querySelector("a");
        aTag.classList.add("pin__parent");
        aTag.innerHTML = ` Tài khoản <span class="badge text-danger badge-dot pin-header">
        <i class="bg-danger pin__child" ></i>
    </span></a>`;
      }

      watingSpan = document.querySelector("#waiting-delete span");
      if (!watingSpan) {
        document.querySelector("#waiting-delete").classList.add("pin__parent");
        document.querySelector("#waiting-delete").innerHTML = `Chờ duyệt xóa tài
        khoản
        <span class="badge text-danger badge-dot pin">
            <i class="bg-danger pin__child"></i>
        </span>`;
      }
    }
    else if (data.type == "register") {
      li = menu[1];
      span = li.querySelector("span");
      if (!span) {
        aTag = li.querySelector("a");
        aTag.classList.add("pin__parent");
        aTag.innerHTML = `Tài khoản <span class="badge text-danger badge-dot pin-header">
        <i class="bg-danger pin__child" ></i>
    </span></a>`;
      }

      watingSpan = document.querySelector("#waiting-register span");
      if (!watingSpan) {
        document
          .querySelector("#waiting-register")
          .classList.add("pin__parent");
        document.querySelector(
          "#waiting-register"
        ).innerHTML = `Chờ duyệt đăng ký nhà môi giới <span class="badge text-danger badge-dot pin">
        <i class="bg-danger pin__child"></i>
    </span>`;
      }
    }
    else if (data.type == "post") {
      li = menu[2];
      span = li.querySelector("span");
      if (!span) {
        aTag = li.querySelector("a");
        aTag.classList.add("pin__parent");
        aTag.innerHTML = `Tin đăng <span class="badge text-danger badge-dot pin-header">
        <i class="bg-danger pin__child" ></i>
    </span></a>`;
      }
      newNumber = documen.querySelector('#new-posts');
      if (newNumber) {
        newNumber.textContent = data.new_posts;
      }
      waitingAcceptPosts = document.querySelector("#waiting span");
      if (!waitingAcceptPosts) {
        document
          .querySelector("#waiting-register")
          .classList.add("pin__parent");
        document.querySelector(
          "#waiting-register"
        ).innerHTML = `Chờ duyệt <span class="badge text-danger badge-dot pin">
        <i class="bg-danger pin__child"></i>
    </span>`;
      }
    }
    else if (data.type == "report") {
      li = menu[3];
      span = li.querySelector("span");
      if (!span) {
        aTag = li.querySelector("a");
        aTag.classList.add("pin__parent");
        aTag.innerHTML = `Báo cáo <span class="badge text-danger badge-dot pin-header">
            <i class="bg-danger pin__child" ></i>
        </span></a>`;
      }      
      newNumber = document.querySelector('#new-reports');
      if (newNumber) {
        newNumber.textContent = data.new_reports;
      }
    } else if (data.type == "register_user") {
      newNumber = document.querySelector('#new-user');
      if (newNumber) {
        newNumber.textContent = data.new_users;
      }
    }
    
  });

  socket.on("message", (data) => {
    if (data.user_send_id != currentUser) {
      if (data.receiver == currentUser || data.sender == currentUser) {
        li = menu[4];
        span = li.querySelector("span");
        if (!span) {
          aTag = li.querySelector("a");
          aTag.classList.add("pin__parent");
          aTag.innerHTML = `Tin nhắn <span class="badge text-danger badge-dot pin-header">
                                <i class="bg-danger pin__child" ></i>
                            </span></a>`;
        }
      }
    }
  });

  socket.on("changeBadge", (data) => {
    if (data.receiver == currentUser || data.sender == currentUser) {
      if (data.numberBadges > 0) {
        li = menu[4];
        span = li.querySelector("span");
        if (!span) {
          aTag = li.querySelector("a");
          aTag.classList.add("pin__parent");
          aTag.innerHTML = `Tin nhắn <span class="badge text-danger badge-dot pin-header">
                                <i class="bg-danger pin__child" ></i>
                            </span></a>`;
        }
      } else if (currentUser != data.last_sent_id) {
        li = menu[4];
        span = li.querySelector("span");
        if (span) {
          aTag = li.querySelector("a");
          aTag.classList.remove("pin__parent");
          aTag.innerHTML = `Tin nhắn`;
        }
      }
    }
  });
});
