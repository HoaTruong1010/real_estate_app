const host = "https://dev-online-gateway.ghn.vn/shiip/public-api/master-data";
var city = "";
var district = "";
var ward = "";
var map;
var marker;

var callAPI = (api) => {
  return fetch(api, {
    headers: {
      token: `c0859386-0c40-11ef-8bfa-8a2dda8ec551`,
      "Content-Type": "application/json",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      renderData(data.data, "province");
    })
    .catch((err) => console.log(err));
};

callAPI(
  "https://dev-online-gateway.ghn.vn/shiip/public-api/master-data/province"
);

var callApiDistrict = (api) => {
  return fetch(api, {
    headers: {
      token: `c0859386-0c40-11ef-8bfa-8a2dda8ec551`,
      "Content-Type": "application/json",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      renderData(data.data, "district");
    })
    .catch((err) => console.log(err));
};

var callApiWard = (api) => {
  return fetch(api, {
    headers: {
      token: `c0859386-0c40-11ef-8bfa-8a2dda8ec551`,
      "Content-Type": "application/json",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      renderData(data.data, "ward");
    })
    .catch((err) => console.log(err));
};

var renderData = (array, select) => {
  let selectObj = document.querySelector("#" + select);
  if (selectObj != null) {
    let row = $(`#${select} option:selected`)[0].outerHTML;
    if (select == "province") {
      array.forEach((item) => {
        row += `<option value="${item.ProvinceID}">${item.NameExtension[1]}</option>`;
      });
    } else if (select == "district") {
      array.forEach((item) => {
        if (
          item.DistrictID != 3715 &&
          item.DistrictID != 3713 &&
          item.DistrictID != 1463 &&
          item.DistrictID != 1443 &&
          item.DistrictID != 1451
        ) {
          if (item.DistrictID == 3695) {
            row += `<option value="${
              item.DistrictID
            }">${item.DistrictName.split("1")[0].trim()}</option>`;
          } else {
            row += `<option value="${item.DistrictID}">${item.DistrictName}</option>`;
          }
        }
      });
    } else if (select == "ward") {
      array.forEach((item) => {
        row += `<option value="${item.WardCode}">${item.WardName}</option>`;
      });
    } else if (select == "cate-prop") {
      array.forEach((item) => {
        row += `<option value="${item.category_name}">${item.category_name}</option>`;
      });
    }
    selectObj.innerHTML = row;
  }
};

$("#province").change(() => {
  city = $("#province option:selected").text();
  district = "";
  ward = "";
  $("#street").val("");
  callApiDistrict(host + "/district?province_id=" + $("#province").val());
  $("#district").html(`<option selected value="">----Chọn----</option>`);
  $("#ward").html(`<option selected value="">----Chọn----</option>`);
  $("#district").attr("required", true);
  $("#address").css("display", "block");
  showAddess();
});

$("#district").change(() => {
  district = $("#district option:selected").text();
  ward = "";
  $("#street").val("");
  $("#ward").html(`<option selected value="">----Chọn----</option>`);
  callApiWard(host + "/ward?district_id=" + $("#district").val());
  showAddess();
});

$("#ward").change(() => {
  ward = $("#ward option:selected").text();
  $("#street").val("");
  showAddess();
});

var showAddess = () => {
  let w_temp = "";
  let d_temp = "";
  let p_temp = "",
    wa = "";
  if (city != "") {
    p_temp = city.replace('.', " ");
  }
  if (district != "") {
    d_temp = district + ", ";
  }
  if (ward != "") {
    w_temp = ward + ", ";
    wa = ward.split("Xã").reverse();
    getLocation(wa[0] + ", " + d_temp + p_temp, wa[0], undefined);
  }
  wdp = w_temp + d_temp + p_temp;
  $("#address").val(wdp);
};

function getLocation(query, wardSplit, streetQuery) {
  console.log(query);
  fetch(
    `https://api.geoapify.com/v1/geocode/search?text=${encodeURIComponent(
      query
    )}&format=json&apiKey=0995357a8a7342f49a53bf3405c86f79&lang=vi`
  )
    .then((res) => res.json())
    .then((results) => {
      if (results.results.length > 0) {
        let data = results.results,
          item;
        if (wardSplit) {
          for (let i = 0; i < data.length; i++) {
            if ((data[i].quarter && data[i].quarter.toLowerCase().includes(wardSplit.toLowerCase())) || (data[i].name && data[i].name.toLowerCase().includes(wardSplit.toLowerCase())))
            {
              item = data[i];
              break;
            }
          }
        }
        if (streetQuery) {
          for (let i = 0; i < data.length; i++) {
            if (
              data[i].street &&
              data[i].street.toLowerCase().includes(wardSplit.toLowerCase())
            ) {
              item = data[i];
              break;
            }
          }
        }
        if (item == undefined) {
          item = results.results[0];
        }
        document.getElementById("map").style.display = "block";
        if (marker) {
          map.removeLayer(marker);
        }
        marker = L.marker([item.lat, item.lon]).addTo(map);
        map.setView(marker.getLatLng(), 13);
        document.getElementById("location").value = item.lat + ", " + item.lon;
      }
    })
    .catch((error) => console.log("error", error));
}

const inputs = document.querySelectorAll(".number");

inputs.forEach((input) => {
  input.addEventListener("keydown", (e) => {
    if (e.key == "-" || e.key == "e" || e.key == "+") {
      e.preventDefault();
    }
  });
});

var input = document.getElementById("address");
if (input != null) {
  input.addEventListener("keydown", (e) => {
    e.preventDefault();
  });
}

var streetInput = document.getElementById("street");
if (streetInput) {
  streetInput.addEventListener("blur", () => {
    let q = streetInput.value + ", " + input.value.split("Xã").reverse()[0].trim();
    getLocation(q, ward.split("Xã").reverse()[0], streetInput.value);
  });
}

var callApiCategory = (api) => {
  return axios({
    method: "post",
    url: `${api}`,
    responseType: "json",
  }).then((response) => {
    renderData(response.data.data, "cate-prop");
  });
};

function load_type_by_category(category_id) {
  if (category_id == "DMD00" || category_id == "DMVP0") {
    $(".col-f").hide();
    $(".col-p").removeClass("col-md-5");
    $(".col-p").addClass("col-md-8");
    $(".col-d").removeClass("col-md-2");
    $(".col-d").addClass("col-md-4");
    $(".row-change-2").hide();
  } else {
    if (category_id == "T0001") {
      $("label[for='btnradio1']").removeClass("btn-primary");
      $("label[for='btnradio1']").addClass("btn-outline-secondary");
      $("label[for='btnradio2']").addClass("btn-primary");
      $("label[for='btnradio2']").removeClass("btn-outline-primary");
      $("#btnradio2").attr("checked", "");
      $("#btnradio1").attr("disabled", "");
    }
    $(".col-f").show();
    $(".col-p").removeClass("col-md-8");
    $(".col-p").addClass("col-md-5");
    $(".col-d").removeClass("col-md-4");
    $(".col-d").addClass("col-md-2");
    $(".row-change-2").show();
  }
  var url = "/api/category/" + category_id;
  callApiCategory(url);
}

$("#category-post").change(() => {
  var category_id = $("#category-post").val();
  load_type_by_category(category_id);
});



$("input[type=radio][name=is_sale]").change(() => {
  let value = $("input[type=radio][name=is_sale]:checked").val();
  if (value == "no") {
    $("label[for='btnradio2']").removeClass("btn-outline-primary");
    $("label[for='btnradio2']").addClass("btn-primary");
    $("label[for='btnradio1']").addClass("btn-outline-primary");
    $("label[for='btnradio1']").removeClass("btn-primary");
  } else {
    $("label[for='btnradio1']").removeClass("btn-outline-primary");
    $("label[for='btnradio1']").addClass("btn-primary");
    $("label[for='btnradio2']").addClass("btn-outline-primary");
    $("label[for='btnradio2']").removeClass("btn-primary");
  }
});

$("input[type=checkbox][name=status]").change(() => {
  if ($("label[for='defaultCheck1']").hasClass("btn-outline-primary")) {
    $("label[for='defaultCheck1']").removeClass("btn-outline-primary");
    $("label[for='defaultCheck1']").addClass("btn-primary");
  } else {
    $("label[for='defaultCheck1']").removeClass("btn-primary");
    $("label[for='defaultCheck1']").addClass("btn-outline-primary");
  }
});

$("button[name='validate']").on("click", (event) => {
  const category = $("select[name='category']");
  if (category.length != 0) {
    const category_id = $("select[name='category'] option:selected").val();
    const issales = $("input[name='is_sale']:checked").val();
    const address = $("input[name='address']").val();
    const street = $("input[name='street']").val();
    const type = $("select[name='cate-prop'] option:selected").val();
    const area = $("input[name='area']").val();
    const price = $("input[name='price']").val();
    const policy = $("input[name='policy']").val();
    const title = $("input[name='title']").val();
    const expire_at = $("input[name='expire-at']").val();
    const description = $("textarea[name='description']").val();
    const bedrooms = $("input[name='bedrooms']").val();
    const bathrooms = $("input[name='bathrooms']").val();
    const images = $("input[name='images']").prop("files");
    var url = $(location).attr("href").split("/");
    var post_id = -1;
    if (url[3] == "edit") {
      post_id = url[4];
    }
    fetch("/api/post/check_properties", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        category: category_id,
        is_sale: issales,
        address: address,
        street: street,
        "cate-prop": type,
        area: area,
        price: price,
        policy: policy,
        title: title,
        "expire-at": expire_at,
        description: description,
        bedrooms: bedrooms,
        bathrooms: bathrooms,
        images: images,
        post_id: post_id,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        if (data.is_true) {
          $("button[name='submit']").click();
          socket.emit('handle_notify', {
            'type': 'post'
          })
        } else {
          $("p").css("display", "none");
          let element = data.for.split("_")[1];
          $(`p#err-msg-${element}`).text(data.content);
          $(`p#err-msg-${element}`).css("display", "block");
          event.preventDefault();
        }
      })
      .catch((err) => {
        console.log(err);
      });
  } else {
    const expire_at = $("input[name='expire-at']").val();
    var url = $(location).attr("href").split("/");
    var post_id = -1;
    if (url[3] == "edit") {
      post_id = url[4];
    }
    fetch("/api/post/check_properties", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        "expire-at": expire_at,
        post_id: post_id,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        if (data.is_true) {
          $("button[name='submit']").click();
        } else {
          $("p").css("display", "none");
          let element = data.for.split("_")[1];
          $(`p#err-msg-${element}`).text(data.content);
          $(`p#err-msg-${element}`).css("display", "block");
          event.preventDefault();
        }
      })
      .catch((err) => {
        console.log(err);
      });
  }
});
