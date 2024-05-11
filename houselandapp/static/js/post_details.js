function compactMoney(money) {
    const unit = ['VNĐ', 'nghìn đồng', 'triệu đồng', 'tỷ đồng'];
    var price = parseFloat(money);
    let i = 0;
    while (price >= 1000) {
        if (i == 3) {
            break;
        }
        i = i + 1;
        price = price / 1000;
    }
    return ` ${price} ${unit[i]}`;
}



var localData = {
    "values": [],
    "index": 0,

}

function createHintPosts(postId) {
    fetch(`/api/load_hint_post/${postId}`)
    .then(res => res.json())
    .then(data => {
        if (data.length > 0) {
            $('#similar').show();
            localData.values = data;
            showLimitCards(localData, data.length, 4);
            showPagination(postId, localData.index, data.length, 4);
        }
        else {
            $('#similar').hide();
        }
    })
}

function backHintPosts(postId) {
    fetch(`/api/load_hint_post/${postId}`)
    .then(res => res.json())
    .then(data => {
        if (data.length > 0) {
            $('#similar').show();
            localData.values = data;
            backLimitCards(localData, data.length, 4);
            showPagination(postId, localData.index, data.length, 4);
        }
        else {
            $('#similar').hide();
        }
    })
}

function showLimitCards(data, length, limit) {
    let cardList = "";
    let img = "";
    let minus = length - data.index;
    if ( minus <= limit) {
        limit = minus;
    }
    for (let i = 0; i < limit; i++) {
        let aTag = `<a href="/posts/${data.values[data.index].id}" class="btn btn-primary">Xem bài viết</a>`
        if (data.values[data.index].image != "") {
            img = `<img class="card-img-top" src="${data.values[data.index].image}" alt="Card image cap">`
        }
        else {
            img = `<img class="card-img-top"
                     src="https://res.cloudinary.com/doaux2ndg/image/upload/v1670076213/FlightMangement/icon-web_fgxmmq.png"
                     alt="Card image cap">`
        }
        cardList += `<div class="card hint-card">
            <div class="card-image">${img}</div>
            <div class="hint-address">
                <p><i class='fas fa-map-marker-alt'></i> ${data.values[data.index].address}</p>
            </div>
            <div class="card-body">
                <h5 class="card-title">${data.values[data.index].title}</h5>
                <p><i class="fab fa-windows"></i> <b>Diện tích:</b>
                    ${(data.values[data.index].area).toLocaleString("en-US")}
                    m<sup>2</sup></p>
                <p><i class="fas fa-dollar-sign"></i> <b>Giá:</b> ${compactMoney(data.values[i].price)}
                </p>
                ${aTag}
            </div>
        </div>`;
        data.index++;
    }

    $("#cards").html(cardList);
}

function backLimitCards(data, length, limit) {
    let currentPage = Math.floor(data.index/limit);
    let cardList = "";
    let img = "";
    let idx, bin;
    if (((data.index - limit*currentPage) % limit) != 0) {
        bin =  data.index - limit*currentPage;
        idx = data.index - bin - limit;
        data.index -= bin;
    }
    else {
        idx = data.index - limit*2;
        data.index -= limit;
    }
    limit = idx + limit;

    for (let i = idx; i < limit; i++) {
        let aTag = `<a href="/posts/${data.values[i].id}" class="btn btn-primary">Xem chi tiết</a>`
        img = `<img class="card-img-top" src="${data.values[i].image}" alt="Card image cap">`
        cardList += `<div class="card hint-card">
            <div class="card-image">${img}</div>
            <div class="hint-address">
                <p><i class='fas fa-map-marker-alt'></i> ${data.values[i].address}</p>
            </div>
            <div class="card-body">
                <h5 class="card-title">${data.values[i].title}</h5>
                <p><i class="fas fa-mountain"></i> <b>Diện tích:</b>
                    ${(data.values[i].area).toLocaleString("en-US")}
                    m<sup>2</sup></p>
                <p><i class="fas fa-dollar-sign"></i> <b>Giá:</b> ${compactMoney(data.values[i].price)}
                </p>
                ${aTag}
            </div>
        </div>`;
    }
    $("#cards").html(cardList);
}

function showPagination(pId, index, length, limit) {
    let pageNum = Math.floor(length/limit)
    let pageNavigation = ''
    if(length > limit) {
        if (index <= limit) {
            pageNavigation = `<li class="page-item">
                    <button class="page-link" id="next" aria-label="Next" onclick="createHintPosts(${pId})">
                        <span aria-hidden="true">&raquo;</span>
                    </button>
                </li>`
        }
        else if (index > (limit*pageNum)) {
            pageNavigation = ` <li class="page-item">
                    <button class="page-link" id="previous" aria-label="Previous" onclick="backHintPosts(${pId})">
                        <span aria-hidden="true">&laquo;</span>
                    </button>
                </li>`
        }
        else {
            pageNavigation = `<li class="page-item">
                    <button class="page-link" id="previous" aria-label="Previous" onclick="backHintPosts(${pId})">
                        <span aria-hidden="true">&laquo;</span>
                    </button>
                </li>
            <li class="page-item">
                    <button class="page-link" id="next" aria-label="Next" onclick="createHintPosts(${pId})">
                        <span aria-hidden="true">&raquo;</span>
                    </button>
                </li>`
        }
    }
    $("#hint").html(pageNavigation);
}

function action(userReportId, actionName, postId) {
    var is_action = false;
    
    if (actionName == "hide") {
        if (confirm("Bạn có chắc chắn ẩn bài viết?\nLưu ý: Hành động này chỉ chuyển trạng thái bài viết thành \"Đã bị ẩn\"") == true) {
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
        fetch("/api/handle_report/" + userReportId + "/" + actionName + "/" + postId, {
            method: "post"
        }).then(res => res.json())
        .then(data => {
            if (data.status == 200) {
                alert("Thành công!");
            }
            else {
                alert("Đã có lỗi xảy ra!\nVui lòng thử lại sau!");
            }
            location.href = '/admin/report/';
        }).catch(err => {
            console.error(err);
        });
    }
}