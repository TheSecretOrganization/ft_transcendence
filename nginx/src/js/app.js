import { renderNavlinks, registerNavLinks } from './navigation.js';
import { renderContent } from './content.js';

const navigate = e => {
    const route = e.target.pathname;
    history.pushState({}, "", route);
    renderContent(route);
};

const registerBrowserBackAndForth = () => {
    window.onpopstate = function (e) {
      const route = location.pathname;
      renderContent(route);
    };
};

const renderInitialPage = () => {
    const route = location.pathname;
    renderContent(route);
};

(function bootup() {
    renderNavlinks();
    registerNavLinks(navigate);
    registerBrowserBackAndForth();
    renderInitialPage();
})();
