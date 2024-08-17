const chatLog = document.getElementById('chat-log');
const chatInput = document.getElementById('chat-input');
const chatRooms = document.getElementById('chat-list');
let currentRoom = "general";
let chatSocket;
let isClosing = false;

function updateActiveRoom() {
    document.querySelectorAll('#chat-list .list-group-item').forEach(item => {
        item.classList.remove('active');
    });
    const activeRoom = document.querySelector(`[data-room="${currentRoom}"]`);
    if (activeRoom) {
        activeRoom.classList.add('active');
    }
}

function switchRoom(roomName) {
    if (chatSocket) {
        isClosing = true;
        chatSocket.close();
    }

    currentRoom = roomName;
    updateActiveRoom();
    chatLog.value = "";

    chatSocket = new WebSocket(`wss://${window.location.host}/ws/chat/${roomName}/`);

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        chatLog.value += (data.message + '\n');
    };

    chatSocket.onclose = function(e) {
        if (!isClosing) {
            console.error('Chat socket closed unexpectedly');
        }
        isClosing = false;
    };

    chatInput.onkeyup = function(e) {
        if (e.key === 'Enter' && chatInput.value.length !== 0) {
            chatSocket.send(JSON.stringify({
                'message': chatInput.value
            }));
            chatInput.value = '';
        }
    };
}

document.addEventListener("DOMContentLoaded", () => {
    switchRoom(currentRoom);
});

chatRooms.addEventListener('click', (e) => {
    if (e.target && e.target.hasAttribute('data-room')) {
        switchRoom(e.target.getAttribute('data-room'));
    }
});

document.getElementById('chat-toggle').onclick = function(e) {
    e.preventDefault();
    document.getElementById('chat-wrapper').classList.toggle("toggled");
    this.classList.toggle("toggled");
};
