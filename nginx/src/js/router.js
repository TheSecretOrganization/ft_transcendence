
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
		return ;
	}

	const data = await response.json();
	if (data.error) {
		console.error(`Failed to fetch ${pageName}: ${data.error}`);
		return null;
	}

	if ('title' in data)
		document.title = data.title;
	else
		document.title = "Missing title";

	return data.html;
}

function loadScripts() {
	const container = document.getElementById("content");
	const scripts = container.querySelectorAll('script');

	scripts.forEach(script => {
		const newScript = document.createElement('script');
		if (script.src) {
			newScript.src = script.src;
		} else {
			newScript.textContent = script.textContent;
		}
		document.body.appendChild(newScript);
		document.body.removeChild(newScript);
	});
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

	document.getElementById("content").innerHTML = html;
	loadScripts();
	updateActiveRoute(path);
}

document.addEventListener("DOMContentLoaded", () => {
	window.onpopstate = handleLocation;
	window.route = route;
	handleLocation();
})
