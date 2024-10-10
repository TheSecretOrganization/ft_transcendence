function subMenuInteractivity(submenu) {
	const submenuLinks = submenu.querySelectorAll('a');

	if (submenu.classList.contains('show')) {
		submenuLinks.forEach(link => {
			link.removeAttribute('tabindex');
		});
	} else {
		submenuLinks.forEach(link => {
			link.setAttribute('tabindex', '-1');
		});
	}
}

function toggleSubMenu(button) {
	const sidebar = document.getElementById('sidebar');
	const submenu = button.nextElementSibling;

	if (sidebar.classList.contains('close')) {
		sidebar.classList.remove('close');
		document.getElementById("toggle-btn").classList.toggle('rotate');

		sidebar.addEventListener("transitionend", () => {
			submenu.classList.toggle('show');
			button.classList.toggle('rotate');
			subMenuInteractivity(submenu);
		}, { once: true });
	} else {
		submenu.classList.toggle('show');
		button.classList.toggle('rotate');
		subMenuInteractivity(submenu);
	}
}
