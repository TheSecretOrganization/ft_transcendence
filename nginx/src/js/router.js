
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
	return data.html;
};

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
};

function updateTitle(pageName) {
	const titles = {
		"index": "Home",
		"games": "Games",
		"404": "Page Not Found"
	};
	const title = titles[pageName] || "Page Not Found";
	document.title = title;
};

function updateActiveRoute(path) {
	document.querySelectorAll('#sidebar-list .list-group-item').forEach(item => {
		item.classList.remove('active');
	});
	const activeRoute = document.querySelector(`[data-route="${path}"]`);
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
	updateTitle(pageName);
	updateActiveRoute(path);
};

document.addEventListener("DOMContentLoaded", () => {
	window.onpopstate = handleLocation;
	window.route = route;
	handleLocation();
});

document.querySelectorAll('a[data-route]').forEach((el) => {
	el.addEventListener("click", (e) => {
		e.preventDefault();
		route(e.target.getAttribute('href'));
	});
});
