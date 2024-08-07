function route(event) {
    event.preventDefault();
    window.history.pushState({}, "", event.target.href);
    handleLocation();
};

async function fetchPage(pageName) {
    const response = await fetch(`${window.config.apiBaseUrl}/pages/${pageName}/`);
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
    const container = document.getElementById("page");
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

async function handleLocation() {
    let path = window.location.pathname;
    let pageName = path === '/' ? 'index' : path.substring(1);
    let html = await fetchPage(pageName);
    if (html === null) {
        html = await fetchPage('404');
    }

    document.getElementById("page").innerHTML = html;
    loadScripts();
    updateTitle(pageName);
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

async function fetchConfig() {
    const response = await fetch('/config.json');
    if (!response.ok) {
        console.error(`Failed to fetch config: ${response.statusText}`);
        return null;
    }
    return response.json();
}

document.addEventListener("DOMContentLoaded", async () => {
    window.onpopstate = handleLocation;
    window.route = route;
    window.config = await fetchConfig();
    handleLocation();

    document.addEventListener("click", (event) => {
        if (event.target.matches("a[data-route]")) {
            route(event);
        }
    });
});

document.getElementById("menu-toggle").addEventListener("click", function (e) {
    e.preventDefault();
    document.getElementById("wrapper").classList.toggle("toggled");
});
