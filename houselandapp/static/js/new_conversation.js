function create(sender, receiver) {
    fetch("/api/check_conversation/" + sender + "/" + receiver, {
        method: "post"
    }).then(res => res.json())
    .then(data => {
        console.info(data);
        href = "/chat/" + data.conversation_id;
        window.open(href,'_blank');
    }).catch(err => {
        console.error(err);
    });
}
