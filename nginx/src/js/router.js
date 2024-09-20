
function route(url) {
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
	return data.html;
}

function updateTitle(pageName) {
	const titles = {
		"index": "Home",
		"games": "Games",
		"404": "Page Not Found"
	};
	const title = titles[pageName] || "Page Not Found";
	document.title = title;
}

function updateActiveRoute(path) {
	const activeRoute = document.querySelector(`a[href="${path}"]`);
	if (activeRoute) {
		activeRoute.classList.add('active');
	}
}

async function handleLocation() {
	let path = window.location.pathname;
	let pageName = path === '/' ? 'index' : path.substring(1);
	let html = await fetchPage(pageName);
	if (html === null) {
		html = await fetchPage('404');
	}

	const content = document.getElementById("content");
	content.innerHTML = html;
	content.querySelectorAll('script').forEach(script => eval(script.textContent));
	updateTitle(pageName);
	updateActiveRoute(path);
}

document.addEventListener("DOMContentLoaded", () => {
	window.onpopstate = handleLocation;
	window.route = route;
	handleLocation();
})
