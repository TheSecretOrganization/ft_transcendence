document.addEventListener('DOMContentLoaded', function () {
    const appDiv = document.getElementById('app');

    fetch('/api/mymodels/')
        .then(response => response.json())
        .then(data => {
            appDiv.innerHTML = '<h1>My Models</h1>';
            data.forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.textContent = item.name;
                appDiv.appendChild(itemDiv);
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            appDiv.innerHTML = '<p>Error loading data</p>';
        });
});
