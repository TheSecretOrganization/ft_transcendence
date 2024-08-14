const roomName = "general";
const chatSocket = new WebSocket(`wss://${window.location.host}/ws/chat/${roomName}/`);
const chatLog = document.getElementById('chat-log');
const chatInput = document.getElementById('chat-input');

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    chatLog.value += (data.message + '\n');
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

chatInput.onkeyup = function(e) {
    if (e.key === 'Enter' && chatInput.value.length !== 0) {
        chatSocket.send(JSON.stringify({
            'message': chatInput.value
        }));
        chatInput.value = '';
    }
};

document.addEventListener("DOMContentLoaded", () => {
    chatLog.value = ""
});

/* Chat Toggle */
document.getElementById('chat-toggle').onclick = function(e) {
    e.preventDefault();
    document.getElementById('chat-wrapper').classList.toggle("toggled");
    this.classList.toggle("toggled");
};
