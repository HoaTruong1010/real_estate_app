const sortUnit = {
  "Mặc định": 0,
  "Giá giảm dần": 1,
  "Giá tăng dần": 2,
  "Diện tích giảm dần": 3,
  "Diện tích tăng dần": 4,
  "Số phòng ngủ giảm dần": 5,
  "Số phòng ngủ tăng dần": 6,
};
const locationInput = document.getElementById("location");
const resultsBox = document.getElementById("autocompleteItems");

const queryString = window.location.search,
  urlParams = new URLSearchParams(queryString);

function submitForm(params) {
  var filteredParams = {},
    baseUrl;
  Object.keys(params).forEach(function (key) {
    if (params[key] !== null && params[key] !== undefined) {
      filteredParams[key] = params[key];
    }
  });

  var queryString = Object.keys(filteredParams)
    .map(function (key) {
      return (
        encodeURIComponent(key) + "=" + encodeURIComponent(filteredParams[key])
      );
    })
    .join("&");
  let issales = $("#issales option:selected").val();
  if (issales == "true") {
    baseUrl = `/sales/${cateId}`;
  } else {
    baseUrl = `/rents/${cateId}`;
  }
  window.location.href = baseUrl + "?" + queryString;
}

var params = {
  page: null,
  sort: null,
  "text-address": null,
  address: null,
  "min-price": null,
  "max-price": null,
  "min-area": null,
  "max-area": null,
  bedrooms: null,
  "type-of": null,
  q: null,
};

window.onload = function () {
  var requestOptions = {
    method: "GET",
  };

  if (locationInput) {
    locationInput.addEventListener("keyup", (e) => {
      let text = locationInput.value;
      if (text.length == 0 && e.key != 8 && e.key != 46) {
        resultsBox.innerHTML = "";
      } else if (text.length) {
        fetch(
          `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(
            text
          )}&format=json&apiKey=0995357a8a7342f49a53bf3405c86f79&lang=vi&limit=5`,
          requestOptions
        )
          .then((response) => response.json())
          .then((result) => {
            if (result.results.length > 0) {
              displayLocation(result.results);
            } else {
              resultsBox.innerHTML = "";
            }
          })
          .catch((error) => console.log("error", error));
      } else {
        resultsBox.innerHTML = "";
      }
    });
  }
  $("html, body").animate(
    {
      scrollTop: 730,
    },
    1000
  );
  $(".ip-a").val((idx, item) => {
    return item.split("Xem")[0];
  });
  $(".p-a").text((idx, item) => {
    return item.split("Xem")[0];
  });
  if (urlParams.has("q")) {
    params["q"] = urlParams.get("q");
  } else {
    params["q"] = null;
  }
  if (urlParams.has("sort")) {
    let sort = urlParams.get("sort");
    params["sort"] = sort;
    selectOptions.forEach((item) => {
      let textOption = item.querySelector("span").outerText;
      if (textOption === sort) {
        item.classList.add("selected");
        item.classList.add("active");
        $(".select-input.form-control[readonly]").val(textOption);
      } else {
        item.classList.remove("selected");
        item.classList.remove("active");
      }
    });
  } else {
    params["sort"] = null;
  }
  if (urlParams.has("text-address") && urlParams.has("address")) {
    let address = urlParams.get("address");
    params["address"] = address;
    locationInput.value = urlParams.get("text-address");
    document.querySelector("#latlon").value = address;
    params["text-address"] = urlParams.get("text-address");
  } else {
    params["address"] = null;
    params["text-address"] = null;
  }
  if (urlParams.has("min-price") && urlParams.has("max-price")) {
    params["min-price"] = urlParams.get("min-price");
    params["max-price"] = urlParams.get("max-price");
  } else {
    params["min-price"] = null;
    params["max-price"] = null;
  }
  if (urlParams.has("min-area") && urlParams.has("max-area")) {
    params["min-area"] = urlParams.get("min-area");
    params["max-area"] = urlParams.get("max-area");
  } else {
    params["min-area"] = null;
    params["max-area"] = null;
  }
  if (urlParams.has("bedrooms")) {
    let bedrooms = urlParams.get("bedrooms");
    params["bedrooms"] = bedrooms;
    bedroomsNum.forEach((item) => {
      let textOption = item.value;
      if (textOption === bedrooms) {
        item.setAttribute("checked", "");
      } else {
        item.removeAttribute("checked");
      }
    });
  } else {
    params["bedrooms"] = null;
  }
  if (urlParams.has("type-of")) {
    let typeOf = urlParams.get("type-of");
    params["type-of"] = typeOf;
    typeOfs.forEach((item) => {
      let textOption = item.value;
      if (textOption === typeOf) {
        item.setAttribute("checked", "");
      } else {
        item.removeAttribute("checked");
      }
    });
  } else {
    params["type-of"] = null;
  }
  if (urlParams.has("page")) {
    let page = urlParams.get("page");
    document.getElementsByClassName("number")[page - 1].classList.add("active");
  }
  $("#select-dropdown-container-60853").hide();
  changePrice();
  changeArea();
};
$("#select-wrapper-101603").on("click", "input", (e) => {
  e.stopPropagation();
  $(".select-input.form-control[readonly]").addClass("active");
  $(".select-input.form-control[readonly]").addClass("focused");
  $("#select-dropdown-container-60853").slideToggle();
});
$(document).on("click", (e) => {
  if (!$(e.target).closest("#select-wrapper-101603").length) {
    $(".select-input.form-control[readonly]").removeClass("active");
    $(".select-input.form-control[readonly]").removeClass("focused");
    if ($("#select-dropdown-container-60853").css("display") === "block") {
      $("#select-dropdown-container-60853").slideToggle();
    }
  }
});

const selectOptions = document.querySelectorAll(".select-option");
if (selectOptions) {
  selectOptions.forEach((item, index) => {
    item.addEventListener("click", () => {
      $(".select-option").removeClass("active");
      $(".select-option").removeClass("selected");
      $(".select-input.form-control[readonly]").val(item.outerText);
      item.classList.add("active");
      item.classList.add("selected");
      params["sort"] = item.outerText;
      if (priceRanges[0].value != 0 || priceRanges[1].value != 200) {
        params["min-price"] = priceRanges[0].value;
        params["max-price"] = priceRanges[1].value;
      } else {
        params["min-price"] = null;
        params["max-price"] = null;
      }
      let adrs = document.querySelector("input#latlon").value;
      if (adrs) {
        params["address"] = adrs;
        params["text-address"] = document.querySelector("#location").value;
      } else {
        params["address"] = null;
        params["text-address"] = null;
      }
      if (areaRanges[0].value != 0 || areaRanges[1].value != 200) {
        params["min-area"] = areaRanges[0].value;
        params["max-area"] = areaRanges[1].value;
      } else {
        params["min-area"] = null;
        params["max-area"] = null;
      }
      if (bedroomsNum) {
        bedroomsNum.forEach((item) => {
          if (item.checked && item.value != 0) {
            params["bedrooms"] = item.value;
          } else {
            params["bedrooms"] = null;
          }
        });
      } else {
        params["bedrooms"] = null;
      }
      if (typeOfs) {
        typeOfs.forEach((item) => {
          if (item.checked && item.value != "all") {
            params["type-of"] = item.value;
          } else {
            params["type-of"] = null;
          }
        });
      } else {
        params["type-of"] = null;
      }
      submitForm(params);
      console.log(params);
    });
  });
}

const locationBtn = document.querySelector("#div__location button");
if (locationBtn) {
  locationBtn.addEventListener("click", () => {
    params["address"] = document.querySelector("input#latlon").value;
    params["text-address"] = document.querySelector("input#location").value;
    if ($(".select-input.form-control[readonly]").val() != "Mặc định") {
      params["sort"] = $(".select-input.form-control[readonly]").val();
    } else {
      params["sort"] = null;
    }
    if (priceRanges[0].value != 0 || priceRanges[1].value != 200) {
      params["min-price"] = priceRanges[0].value;
      params["max-price"] = priceRanges[1].value;
    } else {
      params["min-price"] = null;
      params["max-price"] = null;
    }
    if (areaRanges[0].value != 0 || areaRanges[1].value != 200) {
      params["min-area"] = areaRanges[0].value;
      params["max-area"] = areaRanges[1].value;
    } else {
      params["min-area"] = null;
      params["max-area"] = null;
    }
    if (bedroomsNum) {
      bedroomsNum.forEach((item) => {
        if (item.checked && item.value != 0) {
          params["bedrooms"] = item.value;
        } else {
          params["bedrooms"] = null;
        }
      });
    } else {
      params["bedrooms"] = null;
    }
    if (typeOfs) {
      typeOfs.forEach((item) => {
        if (item.checked && item.value != "all") {
          params["type-of"] = item.value;
        } else {
          params["type-of"] = null;
        }
      });
    } else {
      params["type-of"] = null;
    }
    submitForm(params);
    console.log(params);
  });
}

const priceRanges = document.querySelectorAll(".input-price input");
if (priceRanges) {
  priceRanges.forEach((item, index) => {
    item.addEventListener("mouseup", () => {
      params["min-price"] = priceRanges[0].value;
      params["max-price"] = priceRanges[1].value;
      if ($(".select-input.form-control[readonly]").val() != "Mặc định") {
        params["sort"] = $(".select-input.form-control[readonly]").val();
      } else {
        params["sort"] = null;
      }
      let adrs = document.querySelector("input#latlon").value;
      if (adrs) {
        params["address"] = adrs;
        params["text-address"] = document.querySelector("#location").value;
      } else {
        params["address"] = null;
        params["text-address"] = null;
      }
      if (areaRanges[0].value != 0 || areaRanges[1].value != 200) {
        params["min-area"] = areaRanges[0].value;
        params["max-area"] = areaRanges[1].value;
      } else {
        params["min-area"] = null;
        params["max-area"] = null;
      }
      if (bedroomsNum) {
        bedroomsNum.forEach((item) => {
          if (item.checked && item.value != 0) {
            params["bedrooms"] = item.value;
          } else {
            params["bedrooms"] = null;
          }
        });
      } else {
        params["bedrooms"] = null;
      }
      if (typeOfs) {
        typeOfs.forEach((item) => {
          if (item.checked && item.value != "all") {
            params["type-of"] = item.value;
          } else {
            params["type-of"] = null;
          }
        });
      } else {
        params["type-of"] = null;
      }
      submitForm(params);
      console.log(params);
    });
  });
}

const areaRanges = document.querySelectorAll(".input-area input");
if (areaRanges) {
  areaRanges.forEach((item, index) => {
    item.addEventListener("mouseup", () => {
      params["min-area"] = areaRanges[0].value;
      params["max-area"] = areaRanges[1].value;
      if ($(".select-input.form-control[readonly]").val() != "Mặc định") {
        params["sort"] = $(".select-input.form-control[readonly]").val();
      } else {
        params["sort"] = null;
      }
      let adrs = document.querySelector("input#latlon").value;
      if (adrs) {
        params["address"] = adrs;
        params["text-address"] = document.querySelector("#location").value;
      } else {
        params["address"] = null;
        params["text-address"] = null;
      }
      if (priceRanges[0].value != 0 || priceRanges[1].value != 200) {
        params["min-price"] = priceRanges[0].value;
        params["max-price"] = priceRanges[1].value;
      } else {
        params["min-price"] = null;
        params["max-price"] = null;
      }
      if (bedroomsNum) {
        bedroomsNum.forEach((item) => {
          if (item.checked && item.value != 0) {
            params["bedrooms"] = item.value;
          } else {
            params["bedrooms"] = null;
          }
        });
      } else {
        params["bedrooms"] = null;
      }
      if (typeOfs) {
        typeOfs.forEach((item) => {
          if (item.checked && item.value != "all") {
            params["type-of"] = item.value;
          } else {
            params["type-of"] = null;
          }
        });
      } else {
        params["type-of"] = null;
      }
      submitForm(params);
      console.log(params);
    });
  });
}

const bedroomsNum = document.querySelectorAll("input[name='bedrooms']");
if (bedroomsNum) {
  bedroomsNum.forEach((item, index) => {
    item.addEventListener("click", () => {
      params["bedrooms"] = item.value;
      if ($(".select-input.form-control[readonly]").val() != "Mặc định") {
        params["sort"] = $(".select-input.form-control[readonly]").val();
      } else {
        params["sort"] = null;
      }
      if (priceRanges[0].value != 0 || priceRanges[1].value != 200) {
        params["min-price"] = priceRanges[0].value;
        params["max-price"] = priceRanges[1].value;
      } else {
        params["min-price"] = null;
        params["max-price"] = null;
      }
      if (areaRanges[0].value != 0 || areaRanges[1].value != 200) {
        params["min-area"] = areaRanges[0].value;
        params["max-area"] = areaRanges[1].value;
      } else {
        params["min-area"] = null;
        params["max-area"] = null;
      }
      let adrs = document.querySelector("input#latlon").value;
      if (adrs) {
        params["address"] = adrs;
        params["text-address"] = document.querySelector("#location").value;
      } else {
        params["address"] = null;
        params["text-address"] = null;
      }
      if (typeOfs) {
        typeOfs.forEach((item) => {
          if (item.checked && item.value != "all") {
            params["type-of"] = item.value;
          } else {
            params["type-of"] = null;
          }
        });
      } else {
        params["type-of"] = null;
      }
      submitForm(params);
      console.log(params);
    });
  });
}

const typeOfs = document.querySelectorAll("input[name='type-of']");
if (typeOfs) {
  typeOfs.forEach((item, index) => {
    item.addEventListener("click", () => {
      params["type-of"] = item.value;
      if ($(".select-input.form-control[readonly]").val() != "Mặc định") {
        params["sort"] = $(".select-input.form-control[readonly]").val();
      } else {
        params["sort"] = null;
      }
      if (priceRanges[0].value != 0 || priceRanges[1].value != 200) {
        params["min-price"] = priceRanges[0].value;
        params["max-price"] = priceRanges[1].value;
      } else {
        params["min-price"] = null;
        params["max-price"] = null;
      }
      if (areaRanges[0].value != 0 || areaRanges[1].value != 200) {
        params["min-area"] = areaRanges[0].value;
        params["max-area"] = areaRanges[1].value;
      } else {
        params["min-area"] = null;
        params["max-area"] = null;
      }
      let adrs = document.querySelector("input#latlon").value;
      if (adrs) {
        params["address"] = adrs;
        params["text-address"] = document.querySelector("#location").value;
      } else {
        params["address"] = null;
        params["text-address"] = null;
      }
      if (bedroomsNum) {
        bedroomsNum.forEach((item) => {
          if (item.checked && item.value != 0) {
            params["bedrooms"] = item.value;
          } else {
            params["bedrooms"] = null;
          }
        });
      } else {
        params["bedrooms"] = null;
      }

      submitForm(params);
      console.log(params);
    });
  });
}

const pages = document.querySelectorAll("a.page-number");
if (pages) {
  pages.forEach((item, index) => {
    item.addEventListener("click", () => {
      params['page'] = parseInt(item.classList[0]);
      if (typeOfs) {
        typeOfs.forEach((item) => {
          if (item.checked && item.value != "all") {
            params["type-of"] = item.value;
          } else {
            params["type-of"] = null;
          }
        });
      } else {
        params["type-of"] = null;
      }
      if ($(".select-input.form-control[readonly]").val() != "Mặc định") {
        params["sort"] = $(".select-input.form-control[readonly]").val();
      } else {
        params["sort"] = null;
      }
      if (priceRanges[0].value != 0 || priceRanges[1].value != 200) {
        params["min-price"] = priceRanges[0].value;
        params["max-price"] = priceRanges[1].value;
      } else {
        params["min-price"] = null;
        params["max-price"] = null;
      }
      if (areaRanges[0].value != 0 || areaRanges[1].value != 200) {
        params["min-area"] = areaRanges[0].value;
        params["max-area"] = areaRanges[1].value;
      } else {
        params["min-area"] = null;
        params["max-area"] = null;
      }
      let adrs = document.querySelector("input#latlon").value;
      if (adrs) {
        params["address"] = adrs;
        params["text-address"] = document.querySelector("#location").value;
      } else {
        params["address"] = null;
        params["text-address"] = null;
      }
      if (bedroomsNum) {
        bedroomsNum.forEach((item) => {
          if (item.checked && item.value != 0) {
            params["bedrooms"] = item.value;
          } else {
            params["bedrooms"] = null;
          }
        });
      } else {
        params["bedrooms"] = null;
      }
      submitForm(params);
      console.log(params);
    });
  });
}

function compactMoney(money) {
  const unit = ["VNĐ", "nghìn đồng", "triệu đồng", "tỷ đồng"];
  var price = parseFloat(money);
  let i = 0;
  while (price >= 1000) {
    if (i == 3) {
      break;
    }
    i = i + 1;
    price = price / 1000;
  }
  return ` ${price.toFixed(1)} ${unit[i]}`;
}

function displayLocation(result) {
  const content = result.map((list) => {
    return `<li class="${list.lat} ${list.lon}" onclick=selectInput(this)>${list.formatted}</li>`;
  });
  resultsBox.innerHTML = `<ul>${content.join("")}</ul>`;
}

function selectInput(list) {
  locationInput.value = list.innerHTML;
  document.querySelector("input#latlon").value = list.className;
  resultsBox.innerHTML = "";
}
