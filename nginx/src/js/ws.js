function wsCreateUrl(url, args = {}) {
	const queryParams = new URLSearchParams(args).toString();
	return `wss://${window.location.host}/ws/${url}?${queryParams}`;
}

function wsConnect(url, onMessageCallBack=undefined, onErrorCallBack=undefined) {
	let socket = new WebSocket(url);

	if (onErrorCallBack) {
		socket.onerror = (e) => {
			onErrorCallBack();
		}
	}

	if (onMessageCallBack) {
		socket.onmessage = (e) => {
			onMessageCallBack(JSON.parse(e.data));
		};
	}

	return socket;
}
