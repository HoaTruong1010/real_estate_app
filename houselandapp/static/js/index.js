function create_news() {
  fetch("/api/load_images")
    .then((res) => res.json())
    .then((data) => {
      data.forEach((item) => {
        var image = `<img class="img" src="${item.images.url}" alt="${item.images.date_update}"/>`;
        $(`.item${item.id}-c3`).html(image);
      });
    });
}

function fill_blank_images() {
  const images = document.querySelectorAll("div.handbook-img");
  for (let i = 0; i < images.length; i++) {
    if (images[i].getAttribute("src") != "") {
      var image = `<img src="https://res.cloudinary.com/doaux2ndg/image/upload/v1670076213/FlightMangement/icon-web_fgxmmq.png" alt=""/>`;
      $(`#${images[i].getAttribute("id")}`).html(image);
    }
  }
}

function diffTimes(dateStr) {
  const unit = ["giây", "phút", "giờ", "ngày", "tháng", "năm"];
  const date1 = new Date(dateStr);
  const date2 = new Date();
  var diffTime = Math.abs(date2 - date1) / 1000;
  let i = 0;
  while (true) {
    if (i < 2) {
      diffTime = diffTime / 60;
      i++;
      if (diffTime < 60) {
        break;
      }
    } else if (i == 2) {
      diffTime = diffTime / 24;
      i++;
      if (diffTime < 24) {
        break;
      }
    } else if (i == 3) {
      diffTime = diffTime / 30;
      i++;
      if (diffTime < 30) {
        break;
      }
    } else if (i == 4) {
      diffTime = diffTime / 12;
      i++;
      if (diffTime < 12) {
        break;
      }
    }
    if (i >= 5) {
      break;
    }
  }
  return `${Math.floor(diffTime)} ${unit[i]} trước`;
}

$(document).ready(function () {
  create_news();
  fill_blank_images();
  var times = document.getElementsByClassName("publish_date");
  if (times.length > 0) {
    for (let i = 0; i < times.length; i++) {
      let money = times[i].textContent;
      times[i].textContent = diffTimes(money);
    }
  }

  const address = encodeURIComponent(
    "Quận 2, Hồ Chí Minh"
  );

  fetch(`https://nominatim.openstreetmap.org/search?q=${address}&format=json`)
    .then((response) => response.json())
    .then((data) => {
      if (data.length > 0) {
        const latitude = data[0].lat;
        const longitude = data[0].lon;
      } else {
        console.error("No results found");
      }
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
});
