let devices = {}

function updateDevices() {
    const api_url = "/getdevices";
    fetch(api_url)
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            devices = data;
            populateSelect(data);
        })
        .catch((error) => {
            setState("conerror");
        });
}

function populateSelect(data) {
    const selectElement = document.getElementById("deviceselector");
    if (!selectElement) {
        console.error(`Select element with id "${selectId}" not found.`);
        return;
    }

    // Clear any existing options
    selectElement.innerHTML = '';

    // Add each item as an option
    data.forEach(item => {
        const option = document.createElement('option');
        option.value = item.index;
        option.textContent = item.name;
        selectElement.appendChild(option);
    });
}

function updateState() {
    const api_url = "/getstates";
		fetch(api_url)
			.then((response) => {
				return response.json();
			})
			.then((data) => {
				updateTable(data);
			})
			.catch((error) => {
				console.log(error);
			});
}

function StartStream() {
	let streamurl = document.getElementById("streamurl").value;
    let selectElement = document.getElementById("deviceselector")
    let device = selectElement.value;
    let devicename = selectElement.options[selectElement.selectedIndex].text
	console.log(streamurl);
    console.log(device)
    console.log(devicename)
	const api_url = "/startstream";
	fetch(api_url, {
		method: "POST",
		body: JSON.stringify({
			url: streamurl,
            device: device,
            devicename: devicename
		}),
		headers: {
			"Content-type": "application/json; charset=UTF-8",
		},
	})
		.then((response) => {
			return response.json();
		})
		.then((data) => {
			console.log(data["uid"]);
		});
}

document.getElementById("refreshdevices").addEventListener("click", async () => {
    updateDevices();
})

document.getElementById("startstream").addEventListener("click", async () => {
    console.log("going")
    StartStream();
})

function updateTable(data) {
    const table = document.getElementById("streamTable");
    const tbody = table.querySelector('tbody');

    if (!table || !tbody) {
        console.error(`Table or tbody with ID "${tableId}" not found.`);
        return;
    }

    // Clear existing table body content
    tbody.innerHTML = '';


    data.forEach(device => {
        const row = document.createElement('tr');

        const stopButton = document.createElement('button');
        stopButton.textContent = 'Stop';
        stopButton.addEventListener('click', () => {
            fetch(device.stop)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Request failed: ${response.status}`);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert(`Error sending stop request: ${error.message}`);
                });
        });

        row.innerHTML = `
            <td>${device.id}</td>
            <td>${device.url}</td>
            <td>${device.devicename}</td>
            <td>${device.state}</td>
            <td></td> <!-- placeholder for button -->
        `;

        row.children[4].appendChild(stopButton);

        tbody.appendChild(row);
    });
}

updateDevices();

function updateloop() {
	updateState();
}

setInterval(updateloop, 3 * 1000);