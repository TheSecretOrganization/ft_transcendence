import { routes } from './routes.js';

const nav = document.querySelector('#nav');

export const renderNavlinks = () => {
  const navFragment = document.createDocumentFragment();
  Object.keys(routes).forEach(route => {
    const { linkLabel } = routes[route];

    const linkElement = document.createElement('a')
    linkElement.href = route;
    linkElement.textContent = linkLabel;
    linkElement.className = 'nav-link';
    navFragment.appendChild(linkElement);
  });

  nav.append(navFragment);
};

export const registerNavLinks = (navigate) => {
  nav.addEventListener('click', (e) => {
    e.preventDefault();
    const { href } = e.target;
    navigate(e);
  });
};
