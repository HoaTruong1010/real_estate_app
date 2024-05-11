let roomId = 0,
  isSeen = false;
var otherRoom = {
  id: undefined,
  senderId: undefined,
};
var roomRecieves = [];

function addClassForATag(conversationId) {
  document.querySelectorAll(".select-room").forEach((a) => {
    a.classList.remove("active");
  });
  $(`.${conversationId}`).addClass("active");
  $(`.${conversationId}`).attr("href", "javascript:;");
}

document.addEventListener("DOMContentLoaded", () => {
  $("#typing").hide();
  let numberBadge = $(`#badge-chat`).text();
  $(`#badge-chat`).text(numberBadge);

  socket.on("message", (data) => {
    if (data.room_id == roomId) {
      if (data.user_send_id == currentUser) {
        $("#history-messages").append(`<div class="media w-50 ml-auto mb-3">
                    <div class="media-body">
                        <div class="bg-primary rounded py-2 px-3 mb-2">
                            <p class="text-small mb-0 text-white">${data.msg}</p>
                        </div>
                        <p class="small text-muted">${data.created_at}</p>
                    </div>
                </div>`);
        $(`.mes-${roomId}`).text(`You: ${data.msg}`);
        $(`.mes-${roomId}`).removeClass("font-weight-bold");
      } else {
        $("#history-messages").append(`<div class="media w-50 mb-3">
                        <img src="${data.user_send_avatar}"
                             alt="user" width="50" class="rounded-circle">
                        <div class="media-body ml-3">
                            <div class="bg-light rounded py-2 px-3 mb-2">
                                <p class="text-small mb-0 text-muted">${data.msg}</p>
                            </div>
                            <p class="small text-muted">${data.created_at}</p>
                        </div>
                    </div>`);
        $(`.mes-${roomId}`).text(`${data.msg}`);
        $(`.mes-${roomId}`).addClass("font-weight-bold");
        otherRoom.id = data.room_id;
        otherRoom.senderId = data.user_send_id;
        if (roomRecieves.length > 0) {
          for (let i = 0; i < roomRecieves.length; i++) {
            if (roomRecieves[i].senderId != currentUser) {
              if (roomRecieves[i].id == otherRoom.id) {
                otherRoom.senderId = data.user_send_id;
              } else {
                roomRecieves.push(otherRoom);
              }
            }
          }
        } else {
          roomRecieves.push(otherRoom);
        }
        if (roomRecieves.length == 0) {
          $(`#badge-chat`).text("");
        } else if (data.receiver == currentUser || data.sender == currentUser) {
          if (numberBadge) {
            $(`#badge-chat`).text(parseInt(numberBadge) + roomRecieves.length);
            $(`#admin-navbar-collapse ul.mr-auto li a`)
              .html(`Tin nhắn <span class="badge text-danger badge-dot pin-header">
            <i class="bg-danger pin__child" ></i>
        </span></a>`);
          } else {
            $(`#badge-chat`).text(roomRecieves.length);
          }
        }
      }
      document.querySelector("#input-message").value = "";
    } else {
      if (data.user_send_id == currentUser) {
        $(`.mes-${data.room_id}`).text(`You: ${data.msg}`);
        $(`.mes-${data.room_id}`).removeClass("font-weight-bold");
      } else {
        $(`.mes-${data.room_id}`).text(`${data.msg}`);
        $(`.mes-${data.room_id}`).addClass("font-weight-bold");
        otherRoom.id = data.room_id;
        otherRoom.senderId = data.user_send_id;
        if (roomRecieves.length > 0) {
          for (let i = 0; i < roomRecieves.length; i++) {
            if (roomRecieves[i].senderId != currentUser) {
              if (roomRecieves[i].id == otherRoom.id) {
                otherRoom.senderId = data.user_send_id;
              } else {
                roomRecieves.push(otherRoom);
              }
            }
          }
        } else {
          roomRecieves.push(otherRoom);
        }
        if (roomRecieves.length == 0) {
          $(`#badge-chat`).text("");
        } else if (data.receiver == currentUser || data.sender == currentUser) {
          if (numberBadge) {
            $(`#badge-chat`).text(parseInt(numberBadge) + roomRecieves.length);
            $(`#admin-navbar-collapse ul.mr-auto li a`)
              .html(`Tin nhắn <span class="badge text-danger badge-dot pin-header">
                    <i class="bg-danger pin__child" ></i>
                </span></a>`);
          } else {
            $(`#badge-chat`).text(roomRecieves.length);
          }
        }
      }
    }
  });

  socket.on("changeBadge", (data) => {
    if (data.receiver == currentUser || data.sender == currentUser) {
      if (numberBadge > 0) {
        $(`#badge-chat`).text(numberBadge);
      } else if (currentUser != data.last_sent_id) {
        $(`#badge-chat`).text("");
      }
    }
  });

  const inputMessage = document.querySelector("#input-message");
  if (inputMessage) {
    inputMessage.addEventListener("keypress", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        document.querySelector("#btn-send").click();
      }
    });
    inputMessage.addEventListener("click", () => {
      changeBadge();
      $(`.active p.text-muted`).removeClass("font-weight-bold");
    });
  }

  const btnSend = document.querySelector("#btn-send");
  if (btnSend) {
    btnSend.onclick = () => {
      let message = document.querySelector("#input-message").value;
      socket.emit("message", {
        msg: message,
        isSeen: isSeen,
        userSendId: userSendId,
        userSendAvatar: userSendAvatar,
        room: roomId,
        receiver: receiver,
        sender: sender,
      });
      document.querySelector("#input-message").value = "";
    };
  }
});

function historyChat(conversationId, currentUserId, userReceive) {
  $("#history-messages").css("display", "block");
  $("#history-messages").html("");
  $("#none-conservation").show();
  addClassForATag(conversationId);
  fetch("/api/conversations/" + conversationId, {
    method: "post",
  })
    .then((res) => res.json())
    .then((data) => {
      data.forEach((item) => {
        $(`.mes-${conversationId}`).removeClass("font-weight-bold");
        var created_date = new Date(item.time);
        $("#none-conservation").hide();
        if (item.sent_from == currentUserId) {
          $("#history-messages").append(`<div class="media w-50 ml-auto mb-3">
                    <div class="media-body">
                        <div class="bg-primary rounded py-2 px-3 mb-2">
                            <p class="text-small mb-0 text-white">${
                              item.message
                            }</p>
                        </div>
                        <p class="small text-muted">${created_date.toLocaleString(
                          "en-GB"
                        )}</p>
                    </div>
                </div>`);
        } else if (item.sent_from == userReceive) {
          $("#history-messages").append(`<div class="media w-50 mb-3">
                    <img src="${item.sender_avatar}"
                         alt="user" width="50" class="rounded-circle">
                    <div class="media-body ml-3">
                        <div class="bg-light rounded py-2 px-3 mb-2">
                            <p class="text-small mb-0 text-muted">${
                              item.message
                            }</p>
                        </div>
                        <p class="small text-muted">${created_date.toLocaleString(
                          "en-GB"
                        )}</p>
                    </div>
                </div>`);
        } else {
          $(`.a-${conversationId}`).removeClass("active");
          $("#none-conservation").show();
        }
      });
      $("#typing").show();
      if (conversationId == roomId) {
        let msg = `You are already in room.`;
        printSysMsg(msg);
      } else {
        leaveRoom(roomId);
        joinRoom(conversationId);
        roomId = conversationId;
      }
    })
    .catch((err) => {
      console.error(err);
    });

  function printSysMsg(msg) {
    $("#history-messages").append(`<div class="media w-50 ml-auto mb-3">
            <div class="media-body">
                <div class="bg-primary rounded py-2 px-3 mb-2">
                    <p class="text-small mb-0 text-white">${msg}</p>
                </div>
                <p class="small text-muted"> </p>
            </div>
        </div>`);
  }

  function leaveRoom(roomId) {
    socket.emit("leave", {
      userId: userSendId,
      userSendAvatar: userSendAvatar,
      room: roomId,
    });
  }

  function joinRoom(roomId) {
    socket.emit("join", {
      userId: userSendId,
      userSendAvatar: userSendAvatar,
      room: roomId,
    });
  }
}

const currentCvst = document.querySelector("a.active");
if (currentCvst) {
  currentCvst.addEventListener("click", changeBadge);
}

function changeBadge() {
  socket.emit("changeBadge", {
    currentUser: currentUser,
    conversationId: document.querySelector("a.active").classList[1],
  });
}
