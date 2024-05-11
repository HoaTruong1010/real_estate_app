
let chart;

function loadChart(ctx, labels, data, type, colors, borderColors, text) {
    chart = new Chart(ctx, {
        type: type,
        data: {
          labels: labels,
          datasets: [{
            label: 'Number of Posts per ' + text,
            data: data,
            borderWidth: 1,
            backgroundColor: borderColors
          }]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
}

function statistic(month, text, text2) {
    fetch("/api/stats_post/" + month, {
        method: "post"
    }).then(res => res.json())
    .then(data => {
        var ctx = document.getElementById('myChart').getContext("2d");
        let labels = []
        let data_stats = []
        let colors = []
        let borderColors = []
        let r, g, b

        if (data.data.length > 0) {
            data.data.forEach(item => {
                labels.push(text + item.param_1)
                data_stats.push(item.param_2)
                r = parseInt(Math.random() * 255)
                g = parseInt(Math.random() * 255)
                b = parseInt(Math.random() * 255)

                colors.push(`rgba(${r}, ${g}, ${b}, 0.2)`)
                borderColors.push(`rgba(${r}, ${g}, ${b}, 0.4)`)
            })
            if (chart) {
                chart.destroy();
            }
            loadChart(ctx, labels, data_stats, 'bar', colors, borderColors, text2)
        }

    }).catch(err => {
        console.error(err);
    });
}

$('#select_month').change(function(){
    if($(this).val() == 0) {
        statistic($(this).val(), "Tháng ", "Month");
    }
    else {
        statistic($(this).val(), 'Ngày ', "Day");
    }
})


window.onload = () => {
    const ctx = document.getElementById('myChart').getContext('2d');

    statistic(0, "Tháng ", "Month");
}
