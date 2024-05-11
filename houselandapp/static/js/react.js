function reactPost(postId) {
    fetch("/api/react_post/" + postId, {
        method: "post"
    }).then(res => res.json())
    .then(data => {
        console.info(data);
        var pId = data.data.post_id;
        var result = data.data.result;
        if (result == 1) {
            $("."+pId).removeClass("btn-outline-danger");
            $("."+pId).addClass("btn-danger");
        }
        else {
            $("."+pId).addClass("btn-outline-danger");
            $("."+pId).removeClass("btn-danger");
        }
    }).catch(err => {
        console.error(err);
    });
}
