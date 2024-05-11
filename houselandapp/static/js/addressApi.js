function create_news() {
    fetch("/api/load_images")
    .then(res => res.json())
    .then(data => {
        data.forEach(item => {
            var image = `<img class="img" src="${item.images.url}" alt="${item.images.date_update}"/>`;
            $(`.item${item.id}-c3`).html(image);
        })
    })
}

function fill_blank_images() {
    const images = document.querySelectorAll("div.handbook-img");
    for (let i = 0; i < images.length; i++) {
      if(images[i].getAttribute('src') != '') {
        var image = `<img src="https://res.cloudinary.com/doaux2ndg/image/upload/v1670076213/FlightMangement/icon-web_fgxmmq.png" alt=""/>`;
        $(`#${images[i].getAttribute('id')}`).html(image);
      }
    }
}

const host = "https://vapi.vnappmob.com";
var city = '';
var district = '';
var ward = '';

var callAPI = (api) => {
    return axios.get(api).then((response) => {
        renderData(response.data.results, "province");
    });
}

var callApiDistrict = (api) => {
    return axios.get(api).then((response) => {
        renderData(response.data.results, "district");
    });
}
var callApiWard = (api) => {
    return axios.get(api).then((response) => {
        renderData(response.data.results, "ward");
    });
}
var renderData = (array, select) => {
  let row = ``;  
  if (select == 'province') {        
      array.forEach(item => {
          row += `<button type="button" value="${item.province_id}" style="cursor: pointer;" class="dropdown-item">${item.province_name}</button>`
      })
  }
  else if (select == 'district') {        
      array.forEach(item => {
          row +=`<button type="button" value="${item.district_id}" style="cursor: pointer;" class="dropdown-item">${item.district_name}</button>`
      })
  }
  else if (select == 'ward') {        
      array.forEach(item => {
          row += `<button type="button" value="${item.ward_id}" style="cursor: pointer;" class="dropdown-item">${item.ward_name}</button>`
      })
  }
  document.querySelector('#'+select).innerHTML = row
}
var showAddess = () => {
    let w_temp = '';
    let d_temp = '';
    let p_temp = '';
    if (ward != "") {
        w_temp = ward + ", ";
    }
    if (district != "") {
        d_temp = district + ", ";
    }
    if (city != "") {
        p_temp = city;
    }

    $("#dropdownMenu2").val(w_temp+d_temp+p_temp);
}

$(document).ready(function() {
    $('.search_select_box select').selectpicker();
    create_news();
    fill_blank_images();
    callAPI('https://vapi.vnappmob.com/api/province/');
})

$("#province").on('click', 'button',(function(e){
  e.stopPropagation();
  if ($('.area-show').find('.area-menu-show').is(":hidden")){
    $('.dropdown-toggle').dropdown('toggle');
  }
  city = $(this).text();
  $("#city").text(city);
  $("#district").text("");
  $("#ward").text("");
  $(this).parent().css('display', 'none');
  callApiDistrict(host + "/api/province/district/" + $(this).val());
  showAddess();
}));

$("#district").on('click', 'button',(function(e){
  e.stopPropagation();
  if ($('.area-show').find('.area-menu-show').is(":hidden")){
    $('.dropdown-toggle').dropdown('toggle');
  }
  district = $(this).text();
  $("#dtt").text(district);
  $(this).parent().css('display', 'none');
  callApiWard(host + "/api/province/ward/" + $(this).val());
  showAddess();
}));

$("#ward").on('click', 'button',(function(e){
  e.stopPropagation();
  if ($('.area-show').find('.area-menu-show').is(":hidden")){
    $('.dropdown-toggle').dropdown('toggle');
  }
  ward = $(this).text();
  $("#wd").text(ward);
  $(this).parent().css('display', 'none');
  showAddess();
}));

$("#city").on('click',(function(e){
  e.stopPropagation();
  $("#province").css('display', 'block').addClass("right");
  $("#district").css('display', 'none').removeClass("right");
  $("#ward").css('display', 'none').removeClass("right");
}));

$("#dtt").on('click',(function(e){
  e.stopPropagation();
  $("#province").css('display', 'none').removeClass("right");
  $("#district").css('display', 'block').addClass("right");
  $("#ward").css('display', 'none').removeClass("right");
}));

$("#wd").on('click',(function(e){
  e.stopPropagation();
  $("#province").css('display', 'none').removeClass("right");
  $("#district").css('display', 'none').removeClass("right");
  $("#ward").css('display', 'block').addClass("right");
}));

$('input.address').keydown(function(e) {
   e.preventDefault();
   return false;
});
