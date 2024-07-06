import { routes } from './routes.js';

const app = document.querySelector('#app');

export const renderContent = route => app.innerHTML = routes[route].content;
