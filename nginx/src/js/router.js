// Route handler
const route = (event) => {
    event.preventDefault();
    window.history.pushState({}, "", event.target.href);
    handleLocation();
};

// Fetch page content with caching
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

// Handle location changes
const handleLocation = async () => {
    let path = window.location.pathname;
    let pageName = path === '/' ? 'index' : path.substring(1);
    let html = await fetchPage(pageName);
    if (html === null) {
        html = await fetchPage('404');
    }

    document.getElementById("page").innerHTML = html;
    updateTitle(pageName);
};

// Update the document title based on the path
const updateTitle = (pageName) => {
    const titles = {
        "index": "Home",
        "about": "About",
        "test": "Test",
        "404": "Page Not Found"
    };
    const title = titles[pageName] || "Page Not Found";
    document.title = title;
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
