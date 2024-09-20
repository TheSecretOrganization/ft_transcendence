function wsCreateUrl(url, args={}) {
	const queryParams = new URLSearchParams(args).toString();
	return `wss://${window.location.host}/ws/${url}?${queryParams}`;
}

function wsConnect(url, onMessageCallBack) {
	let socket = new WebSocket(url);

	socket.onerror = (e) => {
		throw new Error(`Fail to connect to ${url}`)
	}

	socket.onmessage = (e) => {
		onMessageCallBack(JSON.parse(e.data));
	};

	return socket;
}
