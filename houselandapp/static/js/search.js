var localSearchData = {
    "values": [],
    "index": 0,
}

function search() {
    const isSales = document.querySelector("select[name='category-posts']").selectedOptions[0].value,
        kw = document.querySelector("input[name='kw']").value,
        address = document.querySelector("input[name='address']").value,
        price = document.querySelectorAll("span[class='price-value']")[0].textContent + " - " + document.querySelectorAll("span[class='price-value']")[1].textContent
    var content = document.getElementById("content");
    fetch("/api/search", {
        method: 'POST',
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ 
            "issales": isSales, 
            "kw": kw, 
            "address": address, 
            'price': price
        })
    })
    .then(res => res.json())
    .then(data => {
        localSearchData.index = 0;
        localSearchData.values = []
        if (data.status == 400) {
            alert(data.message);
            content.classList.remove("d-flex");
            content.classList.add("d-none");
        }
        else {
            content.classList.remove('d-none');
            content.classList.add("d-flex");
            data.results.forEach(item => {
                localSearchData.values.push(item);
            })
            console.log(localSearchData)
            showLimitCards(localSearchData, data.results.length, 6, "#handbook-items");
            showSearchPagination(localSearchData.index, data.results.length, 6, "#paginationSearch");
        }
    })
}

function nextSearchPosts(limit) {
    showLimitCards(localSearchData, localSearchData.values.length, limit, "#handbook-items");
    showSearchPagination(localSearchData.index, localSearchData.values.length, limit, "#paginationSearch");
}

function backSearchPosts(limit) {
    backLimitCards(localSearchData, localSearchData.values.length, limit, "#handbook-items");
    showSearchPagination(localSearchData.index, localSearchData.values.length, limit, "#paginationSearch");
}


function showLimitCards(data, length, limit, position) {
    let cardList = "";

    let minus = length - data.index;
    if ( minus <= limit) {
        limit = minus;
    }
    for (let i = 0; i < limit; i++) {
        let aTag = `<a href="/posts/${data.values[data.index].id}" class="btn btn-primary"
                           style="font-size: 13px; width: 100px; height: 30px; margin-top: 10px;">
                            Xem chi tiết
                        </a>`
        cardList += `<div class="flex1 handbook-item" style="width: 100% !important;">
                    <div class="col30 handbook-img item${data.values[data.index].id}-c3 flex" id="${data.values[data.index].id}">
                        <img class="img" src="${data.values[data.index].image}" alt="Represent Image"/>
                    </div>
                    <div class="col70 handbook-info item-c7">
                        <p class="overflow" style="color: blue; font-size: 12px; height: 28px;"><i
                                class='fas fa-map-marker-alt'> </i>
                            ${data.values[data.index].address}</p>
                        <h3 class="overflow" style="font-size:15px;">${data.values[data.index].title}</h3>
                        <p class='date' style="font-size:13px;"><i class="fab fa-windows"></i> Diện tích:
                            ${(data.values[data.index].area).toLocaleString("en-US")}
                            m<sup>2</sup></p>
                        <p class='date' style="color: red;font-size:13px;"><i class="fas fa-dollar-sign"></i>
                        Giá: <span class="display-price">${compactMoney(data.values[data.index].price)}</span>
                        </p>
                        ${aTag}
                        <a class="btn btn-outline-warning" href="#" title="Report"
                           style="font-size: 13px; width: 40px; height: 30px; margin: 10px 0 0 210px;">
                            <i class="far fa-flag"></i>
                        </a>
                        <a class="btn btn-outline-danger" href="#" title="Save"
                           style="font-size: 13px; width: 40px; height: 30px; margin: 10px 0 0 10px;">
                            <i class="fas fa-archive"></i>
                        </a>
                    </div>
                </div>`;
        data.index++;
    }

    $(position).html(cardList);
}

function backLimitCards(data, length, limit, position) {
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
        let aTag = `<a href="/posts/${data.values[i].id}" class="btn btn-primary"
                           style="font-size: 13px; width: 100px; height: 30px; margin-top: 10px;">
                            Xem chi tiết
                        </a>`
        cardList += `<div class="flex1 handbook-item" style="width: 100% !important;">
                    <div class="col30 handbook-img item${data.values[i].id}-c3 flex" id="${data.values[i].id}">
                        <img class="img" src="${data.values[i].image}" alt="Represent Image"/>
                    </div>
                    <div class="col70 handbook-info item-c7">
                        <p class="overflow" style="color: blue; font-size: 12px; height: 28px;"><i
                                class='fas fa-map-marker-alt'> </i>
                            ${data.values[i].address}</p>
                        <h3 class="overflow" style="font-size:15px;">${data.values[i].title}</h3>
                        <p class='date' style="font-size:13px;"><i class="fab fa-windows"></i> Diện tích:
                            ${(data.values[i].area).toLocaleString("en-US")}
                            m<sup>2</sup></p>
                        <p class='date' style="color: red;font-size:13px;"><i class="fas fa-dollar-sign"></i>
                        Giá: <span class="display-price">${compactMoney(data.values[i].price)}</span>
                        </p>
                        ${aTag}
                        <a class="btn btn-outline-warning" href="#" title="Report"
                           style="font-size: 13px; width: 40px; height: 30px; margin: 10px 0 0 210px;">
                            <i class="far fa-flag"></i>
                        </a>
                        <a class="btn btn-outline-danger" href="#" title="Save"
                           style="font-size: 13px; width: 40px; height: 30px; margin: 10px 0 0 10px;">
                            <i class="fas fa-archive"></i>
                        </a>
                    </div>
                </div>`;
    }

    $(position).html(cardList);
    console.log(data.index);
}

function showSearchPagination(index, length, limit, position) {
    let pageNum = Math.floor(length/limit)
    let pageNavigation = ''
    if(length > limit) {
        if (index <= limit) {
            pageNavigation = `<li class="page-item">
                    <button class="page-link" id="next" aria-label="Next"
                    onclick="nextSearchPosts(6)">
                        <span aria-hidden="true">&raquo;</span>
                    </button>
                </li>`
        }
        else if (index > (limit*pageNum)) {
            pageNavigation = ` <li class="page-item">
                    <button class="page-link" id="previous" aria-label="Previous" onclick="backSearchPosts(6)">
                        <span aria-hidden="true">&laquo;</span>
                    </button>
                </li>`
        }
        else {
            pageNavigation = `<li class="page-item">
                    <button class="page-link" id="previous" aria-label="Previous" onclick="backSearchPosts(6)">
                        <span aria-hidden="true">&laquo;</span>
                    </button>
                </li>
            <li class="page-item">
                    <button class="page-link" id="next" aria-label="Next" onclick="nextSearchPosts(6)">
                        <span aria-hidden="true">&raquo;</span>
                    </button>
                </li>`
        }
    }
    $(position).html(pageNavigation);
}