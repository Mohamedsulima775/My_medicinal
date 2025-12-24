frappe.realtime.on("new_chat_message", (data) => {
    if (cur_frm.doc.name === data.room) {
        render_new_message(data);
    }
});

function render_new_message(data) {
    let container = document.getElementById("messages_container");

    let bubble = document.createElement("div");
    bubble.className = data.sender === frappe.session.user ?
                       "bubble me" : "bubble them";

    bubble.innerHTML = <p>${data.content}</p>;

    container.appendChild(bubble);

    container.scrollTop = container.scrollHeight;
}