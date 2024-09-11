
function submitForm(id, oncomplete, onerror) {
	let form = document.querySelector(`form#${id}`);
	let inputs = document.querySelectorAll(`form#${id} input`);
	let values = {};

	if (form == undefined || inputs == undefined)
		throw new Error(`Unknown form with id ${id}`);

	if (!('url' in form.dataset))
		throw new Error(`Missing data url in form id ${id}`);
	let url = form.dataset.url;

	for (let input of inputs)
		values[input.id] = input.value

	postFetch(url, getCookie('csrftoken'), values)
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
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

function postFetch(url, csrf, body) {
	return fetch(url, {
		method: 'POST',
		headers: {
			'X-CSRFToken': csrf,
			'Content-Type': 'application/json',
		},
		mode: 'same-origin',
		body: JSON.stringify(body),
	});
}
