
const content = document.getElementById('content');

function route(url) {
	window.last_route = window.location.pathname;
	window.history.pushState({}, "", url);
	handleLocation();
}

async function fetchPage(pageName) {
	const response = await fetch(`/api/pages/${pageName}/`);

	if (response.status == 404)
		return null;

	if (response.status != 200) {
		response.json().then(json => {
			if ('redirect' in json)
				route(json.redirect);
		}).catch(error => console.error(error));
		return;
	}

	const data = await response.json();
	if (data.error) {
		console.error(`Failed to fetch ${pageName}: ${data.error}`);
		return null;
	}

	document.title = ('title' in data) ? data.title : "Missing title";

	return data.html;
}

function updateActiveRoute(path) {
	const activeRoute = document.querySelector(`a[href="${path}"]`);
	if (activeRoute) {
		activeRoute.classList.add('active');
	}
}

async function handleLocation() {
	resetEvents();
	content.dispatchEvent(new Event("pagechange"));
	let path = window.location.pathname;
	let pageName = path === '/' ? 'index' : path.substring(1);
	let html = await fetchPage(pageName);
	if (html === null) {
		html = await fetchPage('404');
	}

	content.innerHTML = html;
	content.querySelectorAll('script').forEach(script => eval(script.textContent));
	updateActiveRoute(path);
}

function resetEvents() {
	window.onresize = null;
	document.onkeydown = null;
	document.onmousemove = null;
	document.onpointerlockchange = null;
	document.exitPointerLock();
}

document.addEventListener("DOMContentLoaded", () => {
	window.onpopstate = handleLocation;
	window.route = route;
	handleLocation();
})
