var dataRows = [];

function action(actionName, userId) {
  var is_action = false;
  if (actionName == "accept") {
    if (confirm("Bạn có chắc chắn duyệt cho tài khoản này?") == true) {
      is_action = true;
    } else {
      is_action = false;
    }
  }
  if (actionName == "reset") {
    if (
      confirm("Bạn có chắc chắn khởi tạo lại mật khẩu cho tài khoản này?") ==
      true
    ) {
      is_action = true;
    } else {
      is_action = false;
    }
  }
  if (actionName == "delete") {
    if (
      confirm(
        "Bạn có chắc chắn xóa tài khoản này?\nLưu ý: Hành động này sẽ xóa tài khoản vĩnh viễn"
      ) == true
    ) {
      is_action = true;
    } else {
      is_action = false;
    }
  }
  if (actionName == "restrict") {
    if (
      confirm("Bạn có chắc chắn KHÔNG phê duyệt cho tài khoản này?") == true
    ) {
      is_action = true;
    } else {
      is_action = false;
    }
  }
  if (actionName == "recover") {
    if (confirm("Bạn có chắc chắn khôi phục tài khoản này?") == true) {
      is_action = true;
    } else {
      is_action = false;
    }
  }
  if (is_action) {
    fetch("/api/admin/action_user/" + userId + "/" + actionName, {
      method: "post",
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.code == 200) {
          alert("Hoàn thành!");
          location.reload();
        } else {
          alert("Thất bại!");
        }
      })
      .catch((err) => {
        console.error(err);
      });
  }
}

function replaceAt(origString, replaceChar, type) {
  if (type == "phone") {
    let lastPart = origString.substring(6);

    let newString = "";
    for (let i = 0; i < 6; i++) {
      newString += replaceChar;
    }
    return newString + lastPart;
  } else {
    let beginPart = origString.split("@")[0];
    let lastPart = "@" + origString.split("@")[1];

    let newString = beginPart.substring(0, 3);
    for (let i = 3; i < beginPart.length; i++) {
      newString += replaceChar;
    }
    return newString + lastPart;
  }
}

function display(id, type) {
  if (dataRows) {
    u = dataRows.filter((item) => item.id == id);
    if (type == "phone") {
      document.getElementById("p-" + id).textContent = u[0].phone;
    }
    if (type == "email") {
      document.getElementById("m-" + id).textContent = u[0].email;
    }
  }
}

function loadDataRows(user_role) {
  fetch("/api/load_user_by_user_role/" + user_role, {
    method: "post",
  })
    .then((res) => res.json())
    .then((data) => {
      var tableRow = "";
      document.getElementById("total").textContent = data.data.length;
      if (data.data.length > 0) {
        dataRows = data.data;
        data.data.forEach((item, index) => {
          var created_date = new Date(item.date_created);
          var phone = item.phone;
          var email = item.email;
          var user_role = "";
          var action = "";
          var id = item.id;
          var active;
          if (item.active) {
            active = `<span class='text-primary'>Đã kích hoạt</span>`
          } else {
            active = `<span class='text-danger'>Chưa kích hoạt</span>`
          }

          if (phone == null) {
            phone = ``;
          } else {
            phone = replaceAt(phone, "*", "phone");
          }
          if (email == null) {
            email = ``;
          } else {
            email = replaceAt(email, "*", "email");
          }
          if (item.user_role == "ADMIN") {
            user_role = `<span class="badge text-danger badge-dot mr-4">
                                  <i class="bg-danger"></i> ${item.user_role}
                              </span>`;
            action = ``;
          } else if (item.user_role == "USER") {
            user_role = `<span class="badge text-secondary badge-dot mr-4">
                        <i class="bg-secondary"></i> ${item.user_role}
                      </span> `;
            action = `<a onclick="action('reset', '${id}')" style="color:yellow; font-size:15px; margin-left: 7px;" href="javascript:" title="Reset Password"> <i class="fas fa-key"></i></a> 
                      <a style="font-size:15px; margin-left: 7px;" target="_blank" href="/profile/edit_profile/${id}" title="Edit Account"> <i class="fas fa-edit"></i></a>`;
            if (!item.active) {
              action += `<a onclick="action('delete', '${id}')" style="color:red; font-size:15px; margin-left: 7px;" href="javascript:" title="Delete"> <i class="fas fa-trash"></i></a>`;
            }
          } else if (item.user_role == "HALF_PUBLISHER") {
            user_role = `<span class="badge text-primary badge-dot mr-4">
                        <i class="bg-info"></i>  ${item.user_role}
                      </span>`;
            action = `<a style="font-size:15px; margin-left: 7px;" href="/profile/edit_profile/${id}" target="_blank" title="Review"> <i class="fas fa-eye"></i></a>`;
          } else if (item.user_role == "PUBLISHER") {
            user_role = `<span class="badge text-success badge-dot mr-4">
                        <i class="bg-success"></i>  ${item.user_role}
                      </span>`;
            action = `
                      <a onclick="action('reset', '${id}')" style="color:yellow; font-size:15px; margin-left: 7px;" href="javascript:" title="Reset Password"> <i class="fas fa-key"></i></a>
                      <a style="font-size:15px; margin-left: 7px;" target="_blank" href="/profile/edit_profile/${id}" title="Edit Account"> <i class="fas fa-edit"></i></a>`;
          } else if (item.user_role == "RESTRICTED") {
            user_role = `<span class="badge text-danger badge-dot mr-4">
                        <i class="bg-danger"></i>  ${item.user_role}
                      </span>`;
            action = `
                      <a onclick="action('reset', '${id}')" style="color:yellow; font-size:15px; margin-left: 7px;" href="javascript:" title="Reset Password"> <i class="fas fa-key"></i></a>
                      <a style="font-size:15px; margin-left: 7px;" target="_blank" href="/profile/edit_profile/${id}" title="Edit Account"> <i class="fas fa-edit"></i></a>`;
          } else {
            user_role = `<span class="badge text-warning badge-dot mr-4">
                        <i class="bg-warning"></i>  ${item.user_role}
                      </span>`;
            action = `
                      <a onclick="action('recover', '${id}')" style="color:blue; font-size:15px; margin-left: 7px;" href="javascript:" title="Recover"> <i class="fas fa-redo"></i></a>
                      <a onclick="action('delete', '${id}')" style="color:red; font-size:15px; margin-left: 7px;" href="javascript:" title="Delete"> <i class="fas fa-trash"></i></a>`;
          }
          tableRow += `<tr>
                <td>
                    ${action}
                </td>
                <th scope="row">
                    <div class="media align-items-center">
                        <div class="media-body">
                            <span class="overflow mb-0 text-sm">${
                              item.name
                            }</span>
                        </div>
                    </div>
                </th>
                <td>
                    <a style="color:rgb(73, 80, 87);" id="p-${id}" onclick="display( '${id}', 'phone')" href="javascript:" title="Display Full"> ${phone} </a>                                
                </td>
                <td>
                <a style="color:rgb(73, 80, 87);" id="m-${id}" onclick="display( '${id}', 'email')" href="javascript:" title="Display Full"> ${email} </a>                                

                </td>
                <td>
                    ${user_role}
                </td>
                <td>
                    ${active}
                </td>
                <td>
                    ${created_date.toLocaleString("en-US")}
                </td>
                <td>
                    ${item.number_bad_report}
                </td>
            </tr>`;
        });
        $("#tbody").html(tableRow);
      } else {
        tableRow = `<tr><td colspan="7" class="text-center">Không tìm thấy tài khoản phù hợp!</td></tr>`;
        $("#tbody").html(tableRow);
      }
    })
    .catch((err) => {
      console.error(err);
    });
}

$("#all").click(function () {
  loadDataRows("all");
  $(this).addClass("a-active");
  $("#waiting-register").removeClass("a-active");
  $("#waiting-delete").removeClass("a-active");
});

$("#waiting-register").click(function () {
  loadDataRows("waiting");
  $(this).addClass("a-active");
  $("#all").removeClass("a-active");
  $("#waiting-delete").removeClass("a-active");
});

$("#waiting-delete").click(function () {
  loadDataRows("delete");
  $(this).addClass("a-active");
  $("#all").removeClass("a-active");
  $("#waiting-register").removeClass("a-active");
});

$("#search").keyup(function () {
  var kw = $(this).val();
  if (dataRows) {
    document.getElementById('total').textContent = dataRows.length;
    var tableRow = "";
    rows = dataRows.filter(function (item) {
      if (item.phone == null) {
        return item.email.includes(kw);
      } else if (item.email == null) {
        return item.phone.includes(kw);
      } else {
        return item.phone.includes(kw) || item.email.includes(kw);
      }
    });    
    if (kw.length == 0) {
      loadDataRows("all");
    } else if (rows.length > 0) {
      rows.forEach((item, index) => {
        var created_date = new Date(item.date_created);
        var phone = item.phone;
        var email = item.email;
        var user_role = "";
        var action = "";
        var id = item.id;

        if (phone == null) {
          phone = ``;
        } else {
          phone = replaceAt(phone, "*", "phone");
        }
        if (email == null) {
          email = ``;
        } else {
          email = replaceAt(email, "*", "email");
        }
        if (item.user_role == "ADMIN") {
          user_role = `<span class="badge text-danger badge-dot mr-4">
                                  <i class="bg-danger"></i> ${item.user_role}
                              </span>`;
          action = ``;
        } else if (item.user_role == "USER") {
          user_role = `<span class="badge text-secondary badge-dot mr-4">
                        <i class="bg-secondary"></i> ${item.user_role}
                      </span> `;
          action = `<a onclick="action('reset', '${id}')" style="color:yellow; font-size:15px; margin-left: 7px;" href="javascript:" title="Reset Password"> <i class="fas fa-key"></i></a>`;
        } else if (item.user_role == "HALF_PUBLISHER") {
          user_role = `<span class="badge text-primary badge-dot mr-4">
                        <i class="bg-info"></i>  ${item.user_role}
                      </span>`;
          action = `<a style="font-size:15px; margin-left: 7px;" href="/profile/edit_profile/${id}" target="_blank" title="Review"> <i class="fas fa-eye"></i></a>`;
        } else if (item.user_role == "PUBLISHER") {
          user_role = `<span class="badge text-success badge-dot mr-4">
                        <i class="bg-success"></i>  ${item.user_role}
                      </span>`;
          action = `
                      <a onclick="action('reset', '${id}')" style="color:yellow; font-size:15px; margin-left: 7px;" href="javascript:" title="Reset Password"> <i class="fas fa-key"></i></a>
                      <a style="font-size:15px; margin-left: 7px;" href="/profile/edit_profile/${id}" target="_blank" title="Edit Account"> <i class="fas fa-edit"></i></a>`;
        } else {
          user_role = `<span class="badge text-warning badge-dot mr-4">
                        <i class="bg-warning"></i>  ${item.user_role}
                      </span>`;
          action = `
                      <a onclick="action('recover', '${id}')" style="color:blue; font-size:15px; margin-left: 7px;" href="javascript:" title="Recover"> <i class="fas fa-redo"></i></a>
                      <a onclick="action('delete', '${id}')" style="color:red; font-size:15px; margin-left: 7px;" href="javascript:" title="Delete"> <i class="fas fa-trash"></i></a>`;
        }
        tableRow += `<tr>
                                <th scope="row">
                                        <span class="mb-0 text-sm">${
                                          index + 1
                                        }</span>
                                </th>
                                <th scope="row">
                                    <div class="media align-items-center">
                                        <div class="media-body">
                                            <span class="overflow mb-0 text-sm">${
                                              item.name
                                            }</span>
                                        </div>
                                    </div>
                                </th>
                                <td>
                                    <a style="color:rgb(73, 80, 87);" id="p-${id}" onclick="display( '${id}', 'phone')" href="javascript:" title="Display Full"> ${phone} </a>                                
                                </td>
                                <td>
                                <a style="color:rgb(73, 80, 87);" id="m-${id}" onclick="display( '${id}', 'email')" href="javascript:" title="Display Full"> ${email} </a>                                

                                </td>
                                <td>
                                    ${user_role}
                                </td>
                                <td>
                                    ${created_date.toLocaleString("en-US")}
                                </td>
                                <td>
                                    ${action}
                                </td>
                            </tr>`;
      });
      $("#tbody").html(tableRow);
    } else {
      tableRow = `<tr><td colspan="7" class="text-center">Không tìm thấy tài khoản phù hợp!</td></tr>`;
      $("#tbody").html(tableRow);
    }
  }
});
