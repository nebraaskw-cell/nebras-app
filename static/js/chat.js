let activeRoomId = null;
let lastMessageId = 0;
let pollingInterval = null;
const currentUserId = window.nebrasChatConfig?.currentUserId;

document.addEventListener("DOMContentLoaded", () => {
    loadRooms();
    document.getElementById("messageForm")?.addEventListener("submit", sendMessage);
});

async function loadRooms() {
    try {
        const res = await fetch("/api/v1/chat/rooms/");
        const rooms = await res.json();
        const container = document.getElementById("roomList");
        if (!container) return;
        container.innerHTML = "";

        rooms.forEach((room) => {
            const div = document.createElement("div");
            div.className = "chat-room-item p-3 border-bottom d-flex align-items-center gap-3";
            div.onclick = () => selectRoom(room.id, room.type === "global" ? "العامة" : room.circle_name, div);

            const icon = room.type === "global" ? "bi-globe-americas" : "bi-people-fill";
            const color = room.type === "global" ? "text-info" : "text-success";

            div.innerHTML = `
                <div class="bg-light p-2 rounded-circle ${color}">
                    <i class="bi ${icon} fs-4"></i>
                </div>
                <div>
                    <div class="fw-bold">${room.type === "global" ? "الغرفة العامة" : room.circle_name}</div>
                    <small class="text-muted">${room.type === "global" ? "جميع المستخدمين" : "حلقة خاصة"}</small>
                </div>
            `;
            container.appendChild(div);
        });
    } catch (err) {
        console.error(err);
    }
}

function selectRoom(roomId, name, element) {
    activeRoomId = roomId;
    lastMessageId = 0;

    document.querySelectorAll(".chat-room-item").forEach((el) => el.classList.remove("active"));
    element.classList.add("active");
    document.getElementById("activeRoomName").innerText = name;
    document.getElementById("noChatSelected")?.classList.add("d-none");
    document.getElementById("messageContainer").innerHTML = "";
    document.getElementById("inputArea")?.classList.remove("d-none");

    if (pollingInterval) clearInterval(pollingInterval);
    loadMessages();
    pollingInterval = setInterval(loadMessages, 3000);
}

async function loadMessages() {
    if (!activeRoomId) return;
    try {
        const res = await fetch(`/api/v1/chat/rooms/${activeRoomId}/messages/?after_id=${lastMessageId}`);
        const messages = await res.json();
        if (messages.length === 0) return;

        const container = document.getElementById("messageContainer");
        messages.forEach((msg) => {
            const isSent = msg.sender === currentUserId;
            const bubble = document.createElement("div");
            bubble.className = `message-bubble ${isSent ? "message-sent" : "message-received"}`;
            bubble.innerHTML = `
                ${!isSent ? `<div class="fw-bold small mb-1">${msg.sender_name}</div>` : ""}
                <div>${msg.body}</div>
                <div class="message-info text-end">
                    ${new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </div>
            `;
            container.appendChild(bubble);
            lastMessageId = msg.id;
        });
        container.scrollTop = container.scrollHeight;
    } catch (err) {
        console.error(err);
    }
}

async function sendMessage(e) {
    e.preventDefault();
    const input = document.getElementById("messageInput");
    const body = input?.value.trim();
    if (!body || !activeRoomId) return;

    input.value = "";
    try {
        const res = await fetch(`/api/v1/chat/rooms/${activeRoomId}/messages/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")?.value || "",
            },
            body: JSON.stringify({ body }),
        });

        if (res.ok) loadMessages();
    } catch (err) {
        console.error(err);
    }
}
