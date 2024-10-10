function toggleSubMenu(button) {
	if (document.getElementById("sidebar").classList.contains('close')) {
		document.getElementById("sidebar").classList.remove('close');
		document.getElementById("toggle-btn").classList.toggle('rotate');

		document.getElementById("sidebar").addEventListener("transitionend", () => {
			button.nextElementSibling.classList.toggle('show')
			button.classList.toggle('rotate')
		}, { once : true });
	} else {
		button.nextElementSibling.classList.toggle('show')
		button.classList.toggle('rotate')
	}
}
