var dataRows = []

function action(actionName, postId) {
    var is_action = false;
    if (actionName == "accept") {
        if (confirm("Bạn có chắc chắn duyệt bài viết?") == true) {
            is_action = true;
        } else {
            is_action = false;
        }
    }
    if (actionName == "hide") {
        if (confirm("Bạn có chắc chắn ẩn bài viết?\nLưu ý: Hành động này chỉ chuyển trạng thái bài viết thành \"Đã bị ẩn\"") == true) {
            is_action = true;
        } else {
            is_action = false;
        }
    }
    if (actionName == "delete") {
        if (confirm("Bạn có chắc chắn xóa bài viết?\nLưu ý: Hành động này sẽ xóa bài viết vĩnh viễn") == true) {
            is_action = true;
        } else {
            is_action = false;
        }
    }
    if (actionName == "recovery") {
        if (confirm("Bạn có chắc chắn phục hồi bài viết?\nLưu ý: Hành động này sẽ khôi phục bài viết về trạng thái \"Đã được duyệt\"") == true) {
            is_action = true;
        } else {
            is_action = false;
        }
    }
    if (is_action) {
        fetch("/api/action_post/" + actionName + "/" + postId, {
            method: "post"
        }).then(res => res.json())
        .then(data => {
            if (data.status == 200) {
                alert("Thành công!");
            }
            else {
                alert("Đã có lỗi xảy ra!\nVui lòng thử lại sau!");
            }
            location.reload();
        }).catch(err => {
            console.error(err);
        });
    }
}

function formatDateString(date){
    let dateStr = date.split("GMT")[0]
    let datetime = new Date(dateStr)
    return datetime.getDate() + "/" + (datetime.getMonth()+1) + "/" + datetime.getFullYear() + " " + datetime.getHours() + ":" + datetime.getMinutes() + ":" + datetime.getSeconds()
}

function loadDataRows(status) {
    fetch("/api/status_posts/" + status, {
        method: "post"
    }).then(res => res.json())
    .then(data => {
        var tableRow = ''
        if (data.data.length > 0) {
            dataRows = data.data
            data.data.forEach(item => {
                console.log(item.created_date)
                var created_date = formatDateString(item.created_date)
                var updated_date = formatDateString(item.updated_date)
                var status = ''
                var action = ''
                if (item.status == "Đã bị ẩn") {
                    status = `<span class="badge text-secondary badge-dot mr-4">
                                  <i class="bg-secondary"></i> ${item.status}
                              </span>`
                    action = `<a style="font-size:15px; margin-left: 7px;" href="/posts/${item.id}" target="_blank" title="Details"> <i class="fas fa-eye"></i></a>
                    <a onclick="action('recovery', ${item.id})" style="color:blue; font-size:15px; margin-left: 7px;" href="javascript:" title="Recovery"> <i class="fas fa-redo"></i></a>
                                    <a onclick="action('delete', ${item.id})" style="color:red; font-size:15px; margin-left: 7px;" href="javascript:" title="Delete"> <i class="fas fa-trash"></i></a>`
                }
                else if (item.status == "Chờ duyệt" || item.status == "Đã chỉnh sửa") {
                    status = `<span class="badge text-success badge-dot mr-4">
                        <i class="bg-success"></i> ${item.status}
                      </span> `
                      action = `<a style="font-size:15px; margin-left: 7px;" href="/posts/${item.id}" target="_blank"  title="Details"> <i class="fas fa-eye"></i></a>
                                    <a onclick="action('accept', ${item.id})" style="color:green; font-size:15px; margin-left: 7px;" href="javascript:" title="Accept Post"> <i class="fas fa-check-square"></i></a>
                                    <a onclick="action('delete', ${item.id})" style="color:red; font-size:15px; margin-left: 7px;" href="javascript:" title="Delete"> <i class="fas fa-trash"></i></a>`
                }
                else if (item.status == "Đã hết hạn") {
                    status = `<span class="badge text-danger badge-dot mr-4">
                        <i class="bg-danger"></i> ${item.status}
                      </span> `
                      action = `<a style="font-size:15px; margin-left: 7px;" href="/posts/${item.id}" target="_blank"  title="Details"> <i class="fas fa-eye"></i></a>
                                    <a style="color:blue; font-size:15px; margin-left: 7px;" href="/edit/${item.id}" target="_blank" title="Post Extension"> <i class="fas fa-pen"></i></a>
                                    <a onclick="action('delete', ${item.id})" style="color:red; font-size:15px; margin-left: 7px;" href="javascript:" title="Delete"> <i class="fas fa-trash"></i></a>`
                } else if (item.status == "Đã cho thuê" || item.status == "Đã bán") {
                    status = `<span class="badge text-dark badge-dot mr-4">
                        <i class='bg-dark'></i> ${item.status}
                      </span> `
                      action = `<a style="font-size:15px; margin-left: 7px;" href="/posts/${item.id}" target="_blank"  title="Details"> <i class="fas fa-eye"></i></a>
                                    <a onclick="action('delete', ${item.id})" style="color:red; font-size:15px; margin-left: 7px;" href="javascript:" title="Delete"> <i class="fas fa-trash"></i></a>`
                } 
                else {
                    status = `<span class="badge text-primary badge-dot mr-4">
                        <i class="bg-info"></i>  ${item.status}
                      </span>`
                      action = `<a style="font-size:15px; margin-left: 7px;" href="/posts/${item.id}" target="_blank"  title="Details"> <i class="fas fa-eye"></i></a>
                                    <a onclick="action('hide', ${item.id})" style="color:grey; font-size:15px; margin-left: 7px;" href="javascript:" title="Hide Post"> <i class="fas fa-eye-slash"></i></a>
                                    <a onclick="action('delete', ${item.id})" style="color:red; font-size:15px; margin-left: 7px;" href="javascript:" title="Delete"> <i class="fas fa-trash"></i></a>`
                }
                tableRow += `<tr>
                                <th scope="row">
                                        <span class="mb-0 text-sm">${item.id}</span>
                                </th>
                                <th scope="row">
                                    <div class="media align-items-center">
                                        <div class="media-body">
                                            <span class="overflow mb-0 text-sm">${item.title}</span>
                                        </div>
                                    </div>
                                </th>
                                <td>
                                    ${created_date}
                                </td>
                                <td>
                                    ${updated_date}
                                </td>
                                <td>
                        ${status}
                                </td>
                                <td scope="row">
                                    <div class="media align-items-center">
                                        <a href="#" class="avatar rounded-circle mr-3">
                                            <img alt="Image placeholder"
                                                 src="${item.avatar}">
                                        </a>
                                        <div class="media-body">
                                            <span class="mb-0 text-sm">${item.username}</span>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    ${action}
                                </td>
                            </tr>`
            })
            $('#tbody').html(tableRow)
        }
        else {            
            tableRow = `<tr><td colspan="7" class="text-center">Không tìm thấy bài viết phù hợp!</td></tr>`

            $('#tbody').html(tableRow)
        }
    }).catch(err => {
        console.error(err);
    });
}

$('#all').click(function(){
    loadDataRows("All")
    $(this).addClass("a-active")
    $('#waiting').removeClass("a-active")
    $('#accepted').removeClass("a-active")
    $('#deleted').removeClass("a-active")
    $('#expired').removeClass("a-active")
    $('#rented').removeClass("a-active")
    $('#sold').removeClass("a-active")
})

$('#waiting').click(function(){
    loadDataRows("Chờ duyệt")
    $(this).addClass("a-active")
    $('#all').removeClass("a-active")
    $('#accepted').removeClass("a-active")
    $('#deleted').removeClass("a-active")
    $('#expired').removeClass("a-active")
    $('#rented').removeClass("a-active")
    $('#sold').removeClass("a-active")
})

$('#accepted').click(function(){
    loadDataRows("Đã đăng")
    $(this).addClass("a-active")
    $('#all').removeClass("a-active")
    $('#waiting').removeClass("a-active")
    $('#deleted').removeClass("a-active")
    $('#expired').removeClass("a-active")
    $('#rented').removeClass("a-active")
    $('#sold').removeClass("a-active")
})

$('#deleted').click(function(){
    loadDataRows("Đã bị ẩn")
    $(this).addClass("a-active")
    $('#all').removeClass("a-active")
    $('#accepted').removeClass("a-active")
    $('#waiting').removeClass("a-active")
    $('#expired').removeClass("a-active")
    $('#rented').removeClass("a-active")
    $('#sold').removeClass("a-active")
})

$('#expired').click(function(){
    loadDataRows("Đã hết hạn")
    $(this).addClass("a-active")
    $('#all').removeClass("a-active")
    $('#accepted').removeClass("a-active")
    $('#deleted').removeClass("a-active")
    $('#waiting').removeClass("a-active")
    $('#rented').removeClass("a-active")
    $('#sold').removeClass("a-active")
})

$('#rented').click(function(){
    loadDataRows("Đã cho thuê")
    $(this).addClass("a-active")
    $('#all').removeClass("a-active")
    $('#accepted').removeClass("a-active")
    $('#deleted').removeClass("a-active")
    $('#waiting').removeClass("a-active")
    $('#expired').removeClass("a-active")
    $('#sold').removeClass("a-active")
})

$('#sold').click(function(){
    loadDataRows("Đã bán")
    $(this).addClass("a-active")
    $('#all').removeClass("a-active")
    $('#accepted').removeClass("a-active")
    $('#deleted').removeClass("a-active")
    $('#waiting').removeClass("a-active")
    $('#expired').removeClass("a-active")
    $('#rented').removeClass("a-active")
})

window.onload = () => {
    loadDataRows("All");
}

$('#search').keyup(function() {
    var kw = $(this).val();
    if (dataRows) {
        var tableRow = ''
        rows = dataRows.filter(item => item.id == kw)
        if (rows.length > 0) {
            rows.forEach(item => {
                var created_date = formatDateString(item.created_date)
                var updated_date = formatDateString(item.updated_date)
                var status = ''
                var action = ''
                if (item.status == "Đã bị ẩn") {
                    status = `<span class="badge text-secondary badge-dot mr-4">
                                  <i class="bg-secondary"></i> ${item.status}
                              </span>`
                    action = `<a style="font-size:15px; margin-left: 7px;" href="/posts/${item.id}" target="_blank" title="Details"> <i class="fas fa-eye"></i></a>
                    <a onclick="action('recovery', ${item.id})" style="color:blue; font-size:15px; margin-left: 7px;" href="javascript:" title="Recovery"> <i class="fas fa-redo"></i></a>
                                    <a onclick="action('delete', ${item.id})" style="color:red; font-size:15px; margin-left: 7px;" href="javascript:" title="Delete"> <i class="fas fa-trash"></i></a>`
                }
                else if (item.status == "Chờ duyệt" || item.status == "Đã chỉnh sửa") {
                    status = `<span class="badge text-success badge-dot mr-4">
                        <i class="bg-success"></i> ${item.status}
                      </span> `
                      action = `<a style="font-size:15px; margin-left: 7px;" href="/posts/${item.id}" target="_blank"  title="Details"> <i class="fas fa-eye"></i></a>
                                    <a onclick="action('accept', ${item.id})" style="color:green; font-size:15px; margin-left: 7px;" href="javascript:" title="Accept Post"> <i class="fas fa-check-square"></i></a>
                                    <a onclick="action('delete', ${item.id})" style="color:red; font-size:15px; margin-left: 7px;" href="javascript:" title="Delete"> <i class="fas fa-trash"></i></a>`
                }
                else if (item.status == "Đã hết hạn") {
                    status = `<span class="badge text-danger badge-dot mr-4">
                        <i class="bg-danger"></i> ${item.status}
                      </span> `
                      action = `<a style="font-size:15px; margin-left: 7px;" href="/posts/${item.id}" target="_blank"  title="Details"> <i class="fas fa-eye"></i></a>
                                    <a style="color:blue; font-size:15px; margin-left: 7px;" href="/edit/${item.id}" target="_blank" title="Post Extension"> <i class="fas fa-pen"></i></a>
                                    <a onclick="action('delete', ${item.id})" style="color:red; font-size:15px; margin-left: 7px;" href="javascript:" title="Delete"> <i class="fas fa-trash"></i></a>`
                } else if (item.status == "Đã cho thuê" || item.status == "Đã bán") {
                    status = `<span class="badge text-dark badge-dot mr-4">
                        <i class='bg-dark'></i> ${item.status}
                      </span> `
                      action = `<a style="font-size:15px; margin-left: 7px;" href="/posts/${item.id}" target="_blank"  title="Details"> <i class="fas fa-eye"></i></a>
                                    <a onclick="action('delete', ${item.id})" style="color:red; font-size:15px; margin-left: 7px;" href="javascript:" title="Delete"> <i class="fas fa-trash"></i></a>`
                } 
                else {
                    status = `<span class="badge text-primary badge-dot mr-4">
                        <i class="bg-info"></i>  ${item.status}
                      </span>`
                      action = `<a style="font-size:15px; margin-left: 7px;" href="/posts/${item.id}" target="_blank"  title="Details"> <i class="fas fa-eye"></i></a>
                                    <a onclick="action('hide', ${item.id})" style="color:grey; font-size:15px; margin-left: 7px;" href="javascript:" title="Hide Post"> <i class="fas fa-eye-slash"></i></a>
                                    <a onclick="action('delete', ${item.id})" style="color:red; font-size:15px; margin-left: 7px;" href="javascript:" title="Delete"> <i class="fas fa-trash"></i></a>`
                }
                tableRow += `<tr>
                                <th scope="row">
                                        <span class="mb-0 text-sm">${item.id}</span>
                                </th>
                                <th scope="row">
                                    <div class="media align-items-center">
                                        <div class="media-body">
                                            <span class="overflow mb-0 text-sm">${item.title}</span>
                                        </div>
                                    </div>
                                </th>
                                <td>
                                    ${created_date}
                                </td>
                                <td>
                                    ${updated_date}
                                </td>
                                <td>
                        ${status}
                                </td>
                                <td scope="row">
                                    <div class="media align-items-center">
                                        <a href="#" class="avatar rounded-circle mr-3">
                                            <img alt="Image placeholder"
                                                 src="${item.avatar}">
                                        </a>
                                        <div class="media-body">
                                            <span class="mb-0 text-sm">${item.username}</span>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    ${action}
                                </td>
                            </tr>`
            })
        }
        else {
            tableRow = `<tr><td colspan="7" class="text-center">Không tìm thấy bài viết phù hợp!</td></tr>`
        }
        $('#tbody').html(tableRow)
    }
})


