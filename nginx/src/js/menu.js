function showMenu(menuId, menuClass, backBtn=undefined) {
	document.querySelectorAll(`[${menuClass}]`).forEach(menu => {
		menu.getAttribute(`${menuClass}`) === menuId ? menu.classList.remove("hidden") : menu.classList.add("hidden");
	});
	if (backBtn !== undefined)
		menuId === "main" ? backBtn.classList.add("hidden") : backBtn.classList.remove("hidden");
}

function addBtnToMenusEvents(menuClass, backBtn=undefined) {
	document.querySelectorAll('[menu-id]').forEach(element => {
		element.addEventListener("click", (e) => {
			e.preventDefault();
			showMenu(element.getAttribute("menu-id"), menuClass, backBtn);
		});
	});
}

function showBtn(btn) {
	btn.classList.remove("hidden");
	btn.disabled = false;
}

function hideBtn(btn) {
	btn.classList.add("hidden");
	btn.disabled = true;
}
