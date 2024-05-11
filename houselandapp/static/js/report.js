function report(postId) {
    let content;
    do {
       content = prompt("Bài viết này vi phạm điều gì?", "Nội dung sai sự thật!");
    }
    while(content == "")
    if (content != null && content != "") {
      fetchReport(postId, content);
    }
    else {
        return;
    }
}

function fetchReport(postId, content) {
    fetch("/api/report_post/" + postId + "/" + content, {
            method: "post"
        }).then(res => res.json())
        .then(data => {
            if (data.status == 200) {
                alert("Afforda cảm ơn sự góp ý của bạn!");
                socket.emit('handle_notify', {
                    'type': 'report'
                  })
            }
            else {
                alert("Bạn đã báo cáo bài viết này!");
            }
            document.location.href = '/';
        }).catch(err => {
            console.error(err);
        });
}
