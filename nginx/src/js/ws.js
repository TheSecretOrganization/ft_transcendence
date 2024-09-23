function wsCreateUrl(url, args = {}) {
	const queryParams = new URLSearchParams(args).toString();
	return `wss://${window.location.host}/ws/${url}?${queryParams}`;
}

function wsConnect(url, onMessageCallBack, onErrorCallBack) {
	let socket = new WebSocket(url);

	socket.onerror = (e) => {
        onErrorCallBack();
	}

	socket.onmessage = (e) => {
		onMessageCallBack(JSON.parse(e.data));
	};

	return socket;
}
