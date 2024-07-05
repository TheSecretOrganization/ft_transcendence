fetch(new Request("django:8000/"))
	.then(r => r.text())
	.then(r => console.log(r))
	.catch(e => console.error(e));

window.onload = function () {
	alert("ahh?");
}
