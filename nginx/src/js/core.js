function submitForm(id, oncomplete, onerror) {
	let form = document.querySelector(`form#${id}`);
	let inputs = document.querySelectorAll(`form#${id} input`);
	let values = {};

	if (form == undefined || inputs == undefined)
		throw new Error(`Unknown form with id ${id}`);

	if (!('url' in form.dataset))
		throw new Error(`Missing data url in form id ${id}`);
	let url = form.dataset.url;

	for (let input of inputs) {
		if (input.type == 'hidden') continue;
		if ('ignore' in input.dataset) continue;
		values[input.id] = input.value
	}

	postFetch(url, values)
		.then((response) => {
			if (response.status == 200)
				oncomplete();
			else
				response.json()
					.then(json => onerror(json))
					.catch(error => console.error(error));
		}).catch(error => console.error(error));
}

function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';').map(cookie => cookie.trim());
		for (let cookie of cookies) {
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

function postFetch(url, body) {
	return fetch(url, {
		method: 'POST',
		headers: {
			'X-CSRFToken': getCookie('csrftoken'),
			'Content-Type': 'application/json',
		},
		mode: 'same-origin',
		body: JSON.stringify(body),
	});
}

function logout() {
	fetch('/api/auth/logout/')
		.then(r => {
			if (r.status == 200) route('/');
			else r.json().then(json => console.error(json.error));
		}).catch(error => console.error(error));
}

function displayToast(message) {
	const toastContentElement = document.getElementById('toast-content');
	toastContentElement.textContent = message;
	const toastElement = document.getElementById('toast');
	const toast = new bootstrap.Toast(toastElement);
	toast.show();
}

function getFont() {
	return "Poppins";
}

function copyElementText(elementId) {
	const copyText = document.getElementById(elementId);

	navigator.clipboard.writeText(copyText.innerText);
}
