function route(e) {
    e.preventDefault();
    window.history.pushState({}, "", e.target.getAttribute('data-route'));
    handleLocation();
};

async function fetchPage(pageName) {
    const response = await fetch(`/api/pages/${pageName}/`);
    if (!response.ok) {
        console.error(`Failed to fetch ${pageName}: ${response.statusText}`);
        return null;
    }
    const data = await response.json();
    if (data.error) {
        console.error(`Failed to fetch ${pageName}: ${data.error}`);
        return null;
    }
    return data.html;
};

function loadScripts() {
    const container = document.getElementById("page-container");
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
        "404": "Page Not Found",
        "index": "Home",
        "games": "Games",
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

    document.getElementById("page-container").innerHTML = html;
    loadScripts();
    updateTitle(pageName);
    updateActiveRoute(path);
};

document.addEventListener("DOMContentLoaded", () => {
    window.onpopstate = handleLocation;
    window.route = route;
    handleLocation();
});

document.addEventListener("click", (e) => {
    if (e.target && e.target.hasAttribute('data-route')) {
        route(e);
    }
});

document.getElementById("sidebar-toggle").addEventListener("click", function (e) {
    e.preventDefault();
    document.getElementById("sidebar-wrapper").classList.toggle("toggled");
    this.classList.toggle("toggled");
});
