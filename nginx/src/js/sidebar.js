function toggleSubMenu(button) {
	button.nextElementSibling.classList.toggle('show')
	button.classList.toggle('rotate')

	if (sidebar.classList.contains('close')) {
		sidebar.classList.toggle('close')
		toggleButton.classList.toggle('rotate')
	}
}