let chart, chart2;
const ctx = document.getElementById("myChart").getContext("2d");
const ctx2 = document.getElementById("myChart2").getContext("2d");

function loadChart(ctx, labels, data, type, colors, borderColors, text, year) {
  if (ctx.canvas.getAttribute("id").includes("2")) {
    chart2 = new Chart(ctx, {
      type: type,
      data: {
        labels: labels,
        datasets: [
          {
            label: "Number of Accounts per " + text,
            data: data,
            borderWidth: 1,
            backgroundColor: borderColors,
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
          },
        },
        plugins: {
          title: {
            display: true,
            text: "Năm " + year,
          },
        }
      },
    });
  } else {
    chart = new Chart(ctx, {
      type: type,
      data: {
        labels: labels,
        datasets: [
          {
            label: "Number of Posts per " + text,
            data: data,
            borderWidth: 1,
            backgroundColor: borderColors,
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
          },
        },
        plugins: {
          title: {
            display: true,
            text: "Năm " + year,
          },
        }
      },
    });
  }
}

function statistic(api, text, text2, context, year, type) {
  fetch(api, {
    method: "post",
  })
    .then((res) => res.json())
    .then((data) => {
      var ctx = context;
      let labels = [];
      let data_stats = [];
      let colors = [];
      let borderColors = [];
      let r, g, b;

      if (data.data.length > 0) {
        data.data.forEach((item) => {
          labels.push(text + item.param_1);
          data_stats.push(item.param_2);
          
          r = parseInt(Math.random() * 255);
          g = parseInt(Math.random() * 255);
          b = parseInt(Math.random() * 255);

          colors.push(`rgba(${r}, ${g}, ${b}, 0.2)`);
          borderColors.push(`rgba(${r}, ${g}, ${b}, 0.4)`);
        });
      }
      if (chart && !ctx.canvas.getAttribute("id").includes("2")) {
        chart.destroy();
      }
      if (chart2 && ctx.canvas.getAttribute("id").includes("2")) {
        chart2.destroy();
      }
      loadChart(ctx, labels, data_stats, type, colors, borderColors, text2, year);
    })
    .catch((err) => {
      console.error(err);
    });
}

$("#select_month").change(function () {
    let value = $(this).val();
  let api = "/api/stats_post/" + value;
  if (!value) {
    statistic(api, "Tháng ", "Month", ctx, '2024', 'bar');
  } else {
    statistic(api, "Ngày ", "Day", ctx, value.split("-")[0], 'bar');
  }
});

$("#select-month-2").change(function () {
  let value = $(this).val();
  let api = "/api/stats_acc/" + value;
  if (!value) {
    statistic(api, "Tháng ", "Month", ctx2, '2024', 'pie');
  } else {
    statistic(api, "Ngày ", "Day", ctx2, value.split("-")[0], 'pie');
  }
});

window.onload = () => {
  let api = "/api/stats_post/2024-00";
  let api2 = "/api/stats_acc/2024-00";

  statistic(api, "Tháng ", "Month", ctx, '2024', "bar");
  statistic(api2, "Tháng ", "Month", ctx2, '2024', 'pie');
};
