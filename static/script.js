
document.addEventListener("DOMContentLoaded", () => {
    const socket = io();
    const form = document.getElementById("chat-form");
    const input = document.getElementById("message");
    const messages = document.getElementById("messages");
    const room = "{{ room_code }}";

    socket.emit("join", { room: room });

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        socket.emit("message", { msg: input.value, room: room });
        input.value = "";
    });

    socket.on("message", (data) => {
        const container = document.createElement("li");
        container.classList.add("message", "flex", "flex-col", "max-w-xs", "md:max-w-md");

        const username = data.username || "";
        if (!username) {
            // System message
            container.classList.add("text-center", "text-gray-500", "mx-auto");
            container.innerHTML = `<p>${data.msg}</p>`;
        } else if (username === "{{ username }}") {
            // User's message
            container.classList.add("self-end", "bg-blue-500", "text-white", "rounded-lg", "px-4", "py-2", "mr-4");
            container.innerHTML = `<p>${data.msg}</p>`;
        } else {
            // Other user's message
            const name = document.createElement("p");
            name.textContent = username;
            name.classList.add("text-sm", "text-gray-500", "mb-1", "ml-4");

            const bubble = document.createElement("div");
            bubble.textContent = data.msg;
            bubble.classList.add("bg-gray-200", "text-gray-800", "rounded-lg", "px-4", "py-2", "ml-4");

            container.appendChild(name);
            container.appendChild(bubble);
            container.classList.add("self-start");
        }

        messages.appendChild(container);
        messages.scrollTop = messages.scrollHeight;
    });

    socket.on("update_online_users", (data) => {
        document.getElementById(
            "online-users"
        ).textContent = `Online Users: ${data.online_users}`;
    });

    document.getElementById("leave-room").addEventListener("click", () => {
        socket.emit("leave", { room: room });
        window.location.href = "{{ url_for('app.dashboard') }}";
    });
});