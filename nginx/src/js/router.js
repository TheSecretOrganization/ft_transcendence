// Route handler
const route = (event) => {
    event.preventDefault();
    window.history.pushState({}, "", event.target.href);
    handleLocation();
};

// Route definitions
const routes = {
    404: { url: "pages/404.html", title: "Page Not Found" },
    "/": { url: "pages/index.html", title: "Home" },
    "/about": { url: "pages/about.html", title: "About" },
    "/test": { url: "pages/test.html", title: "Test" },
};

// Page cache to store fetched pages
const pageCache = {};

// Fetch page content with caching
const fetchPage = async (url) => {
    if (pageCache[url]) {
        return pageCache[url];
    }

    const response = await fetch(url);
    if (!response.ok) {
        console.error(`Failed to fetch ${url}: ${response.statusText}`);
        return null;
    }
    const text = await response.text();
    pageCache[url] = text;
    return text;
};

// Handle location changes
const handleLocation = async () => {
    let path = window.location.pathname;

    let route = routes[path];
    if (!route) {
        route = routes[404];
        path = "404";
    }

    let html = await fetchPage(route.url);
    if (html === null) {
        html = await fetchPage(routes[404].url);
        path = "404";
    }

    document.getElementById("page").innerHTML = html;
    document.title = routes[path].title;
};

// Initialize routing
document.addEventListener("DOMContentLoaded", () => {
    window.onpopstate = handleLocation;
    window.route = route;
    handleLocation();

    // Event delegation for links
    document.addEventListener("click", (event) => {
        if (event.target.matches("a[data-route]")) {
            route(event);
        }
    });
});
