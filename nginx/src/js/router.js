const route = (event) => {
    event.preventDefault();
    window.history.pushState({}, "", event.target.href);
    handleLocation();
};

const fetchPage = async (pageName) => {
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

const loadScripts = () => {
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

const handleLocation = async () => {
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

const updateTitle = (pageName) => {
    const titles = {
        "index": "Home",
        "pong": "Pong",
        "404": "Page Not Found"
    };
    const title = titles[pageName] || "Page Not Found";
    document.title = title;
};

document.addEventListener("DOMContentLoaded", () => {
    window.onpopstate = handleLocation;
    window.route = route;
    handleLocation();

    document.addEventListener("click", (event) => {
        if (event.target.matches("a[data-route]")) {
            route(event);
        }
    });
});
