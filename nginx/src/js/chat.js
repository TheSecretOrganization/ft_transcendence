let currentUser = document.getElementById('current-user').getAttribute("value");
let roomId = "General";
let chatSocket = wsConnect(wsCreateUrl("chat/" + roomId), handleOnMessage, handleOnError);

document.getElementById("chat-button").addEventListener("click", function () {
	const chatContainer = document.getElementById("chat-container");
	if (chatContainer.style.display === "none" || chatContainer.style.display === "") {
		chatContainer.style.display = "flex";
	} else {
		chatContainer.style.display = "none";
	}
});

function wsCreateUrl(path) {
	const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
	const url = protocol + window.location.host + '/ws/' + path + '/';
	return url;
}


function wsConnect(url, onMessage, onError) {
	const socket = new WebSocket(url);
	socket.onopen = function () {
		console.log('WebSocket connection opened to ' + url);

		const roomNameElement = document.getElementById('room-name');
		if (roomNameElement) {
			roomNameElement.innerText = 'Salle: ' + roomId;
		}
	};

	socket.onclose = function (e) {
		console.log('WebSocket connection closed:', e);
		setTimeout(function () {
			chatSocket = wsConnect(url, onMessage, onError);
		}, 5000);
	};

	socket.onmessage = onMessage;
	socket.onerror = onError;
	return socket;
}


function handleOnMessage(e) {
	const data = JSON.parse(e.data);
	if (data.type === 'active_users') {
		updateActiveUsers(data.users);
	} else {
		let message = data.message;
		let username = data.username;

		const chatLog = document.getElementById('chat-log');
		const newMessageDiv = document.createElement('div');
		console.log("current :", currentUser);
		console.log("username :", username);

		if (username === currentUser) {
			newMessageDiv.classList.add('message', 'self');
		} else {
			newMessageDiv.classList.add('message', 'other');
		}


		newMessageDiv.innerHTML = `<strong>${username}:</strong> ${message}`;
		chatLog.appendChild(newMessageDiv);


		chatLog.scrollTop = chatLog.scrollHeight;
	}
}


function handleOnError(error) {
	console.error('WebSocket Error:', error);
}


function updateActiveUsers(users) {
	const userList = document.getElementById('user-list');
	userList.innerHTML = '';

	users.forEach(user => {
		const userItem = document.createElement('li');
		userItem.classList.add('user-item');
		userItem.textContent = user;
		userList.appendChild(userItem);
	});
}


document.getElementById("send-form").addEventListener("submit", e => {
	e.preventDefault();
	const messageInput = document.getElementById('message-input');
	const message = messageInput.value.trim();
	if (chatSocket && chatSocket.readyState === WebSocket.OPEN && message) {
		chatSocket.send(JSON.stringify({
			'message': message,
			'username': currentUser || 'Anonyme',
		}));
	}
	messageInput.value = '';
});
