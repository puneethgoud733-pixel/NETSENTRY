let devices = [];


// ==================================================
// LOAD DEVICES
// ==================================================

async function loadDevices() {

    try {

        const response =
            await fetch("/devices");


        if (!response.ok) {

            throw new Error(
                "Failed to load devices"
            );

        }


        devices =
            await response.json();


        renderDevices();

        updateStatistics();


    } catch (error) {

        console.error(
            "Error loading devices:",
            error
        );


        showError(
            "Unable to load devices."
        );

    }

}


// ==================================================
// RENDER DEVICES
// ==================================================

function renderDevices(
    list = devices
) {

    const tableBody =
        document.getElementById(
            "deviceTableBody"
        );


    if (!tableBody) {

        return;

    }


    if (list.length === 0) {

        tableBody.innerHTML = `

            <tr>

                <td
                    colspan="8"
                    class="empty"
                >

                    No devices found.

                </td>

            </tr>

        `;

        return;

    }


    tableBody.innerHTML =
        list.map(device => {


            const statusClass =
                device.status === "Online"
                    ? "status-online"
                    : "status-offline";


            const responseClass =
                device.response === "Reachable"
                    ? "response-good"
                    : "response-bad";


            return `

                <tr>

                    <td>
                        ${device.id}
                    </td>


                    <td>

                        <strong>
                            ${escapeHtml(
                                device.hostname
                            )}
                        </strong>

                    </td>


                    <td>
                        ${escapeHtml(
                            device.ip_address
                        )}
                    </td>


                    <td>
                        ${escapeHtml(
                            device.device_type
                        )}
                    </td>


                    <td>

                        <span
                            class="status
                            ${statusClass}"
                        >

                            ${
                                device.status === "Online"
                                    ? "● Online"
                                    : "● Offline"
                            }

                        </span>

                    </td>


                    <td>

                        <span
                            class="${responseClass}"
                        >

                            ${escapeHtml(
                                device.response ||
                                "Unknown"
                            )}

                        </span>

                    </td>


                    <td>

                        ${
                            device.last_checked ||
                            "Never"
                        }

                    </td>


                    <td class="actions">


                        <button
                            class="check-btn"
                            onclick="checkDevice(
                                ${device.id}
                            )"
                        >

                            Check

                        </button>


                        <button
                            class="delete-btn"
                            onclick="deleteDevice(
                                ${device.id}
                            )"
                        >

                            Delete

                        </button>


                    </td>

                </tr>

            `;

        }).join("");

}


// ==================================================
// STATISTICS
// ==================================================

function updateStatistics() {

    const total =
        devices.length;


    const online =
        devices.filter(
            device =>
                device.status === "Online"
        ).length;


    const offline =
        devices.filter(
            device =>
                device.status === "Offline"
        ).length;


    document.getElementById(
        "totalDevices"
    ).textContent = total;


    document.getElementById(
        "onlineDevices"
    ).textContent = online;


    document.getElementById(
        "offlineDevices"
    ).textContent = offline;


    document.getElementById(
        "activeAlerts"
    ).textContent = offline;


    document.getElementById(
        "healthOnline"
    ).textContent = online;


    document.getElementById(
        "healthOffline"
    ).textContent = offline;

}


// ==================================================
// CHECK ONE DEVICE
// ==================================================

async function checkDevice(id) {

    try {

        const response =
            await fetch(
                `/devices/${id}/check`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Device check failed"
            );

        }


        const updatedDevice =
            await response.json();


        const index =
            devices.findIndex(
                device =>
                    device.id === id
            );


        if (index !== -1) {

            devices[index] =
                updatedDevice;

        }


        renderDevices();

        updateStatistics();

        loadHistory();


    } catch (error) {

        console.error(
            "Error checking device:",
            error
        );


        alert(
            "Failed to check device."
        );

    }

}


// ==================================================
// CHECK ALL DEVICES
// ==================================================

async function checkAllDevices() {

    const button =
        document.getElementById(
            "checkAllBtn"
        );


    try {

        button.disabled = true;

        button.textContent =
            "Checking...";


        const response =
            await fetch(
                "/devices/check-all",
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Check all failed"
            );

        }


        devices =
            await response.json();


        renderDevices();

        updateStatistics();

        loadHistory();


    } catch (error) {

        console.error(
            "Error checking all devices:",
            error
        );


        alert(
            "Failed to check all devices."
        );


    } finally {

        button.disabled = false;

        button.textContent =
            "↻ Check All Devices";

    }

}


// ==================================================
// ADD DEVICE
// ==================================================

async function addDevice() {

    const hostname =
        prompt(
            "Enter hostname:"
        );


    if (!hostname) {

        return;

    }


    const ipAddress =
        prompt(
            "Enter IP address:"
        );


    if (!ipAddress) {

        return;

    }


    const deviceType =
        prompt(
            "Enter device type:",
            "Computer"
        );


    if (!deviceType) {

        return;

    }


    try {

        const response =
            await fetch(
                "/devices",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            hostname:
                                hostname,

                            ip_address:
                                ipAddress,

                            device_type:
                                deviceType

                        })

                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Failed to add device"
            );

        }


        devices.push(data);


        renderDevices();

        updateStatistics();


        alert(
            "Device added successfully."
        );


    } catch (error) {

        console.error(
            "Error adding device:",
            error
        );


        alert(
            error.message ||
            "Failed to add device."
        );

    }

}


// ==================================================
// DELETE DEVICE
// ==================================================

async function deleteDevice(id) {

    const confirmed =
        confirm(
            "Are you sure you want to delete this device?"
        );


    if (!confirmed) {

        return;

    }


    try {

        const response =
            await fetch(
                `/devices/${id}`,
                {
                    method: "DELETE"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Delete failed"
            );

        }


        devices =
            devices.filter(
                device =>
                    device.id !== id
            );


        renderDevices();

        updateStatistics();

        loadHistory();


    } catch (error) {

        console.error(
            "Error deleting device:",
            error
        );


        alert(
            "Failed to delete device."
        );

    }

}


// ==================================================
// SEARCH
// ==================================================

function filterDevices() {

    const input =
        document.getElementById(
            "searchInput"
        );


    const search =
        input.value
            .toLowerCase()
            .trim();


    const filtered =
        devices.filter(device =>

            device.hostname
                .toLowerCase()
                .includes(search)

            ||

            device.ip_address
                .toLowerCase()
                .includes(search)

            ||

            device.device_type
                .toLowerCase()
                .includes(search)

        );


    renderDevices(
        filtered
    );

}


// ==================================================
// MONITORING HISTORY
// ==================================================

async function loadHistory() {

    try {

        const response =
            await fetch(
                "/history"
            );


        if (!response.ok) {

            throw new Error(
                "Failed to load history"
            );

        }


        const history =
            await response.json();


        renderHistory(
            history
        );


    } catch (error) {

        console.error(
            "Error loading history:",
            error
        );


        const tableBody =
            document.getElementById(
                "historyTableBody"
            );


        if (tableBody) {

            tableBody.innerHTML = `

                <tr>

                    <td
                        colspan="5"
                        class="error"
                    >

                        Unable to load
                        monitoring history.

                    </td>

                </tr>

            `;

        }

    }

}


// ==================================================
// RENDER HISTORY
// ==================================================

function renderHistory(
    history
) {

    const tableBody =
        document.getElementById(
            "historyTableBody"
        );


    if (!tableBody) {

        return;

    }


    if (history.length === 0) {

        tableBody.innerHTML = `

            <tr>

                <td
                    colspan="5"
                    class="empty"
                >

                    No monitoring history yet.

                </td>

            </tr>

        `;

        return;

    }


    tableBody.innerHTML =
        history.map(item => {


            const statusClass =
                item.status === "Online"
                    ? "status-online"
                    : "status-offline";


            const responseClass =
                item.response === "Reachable"
                    ? "response-good"
                    : "response-bad";


            return `

                <tr>


                    <td>

                        <strong>

                            ${escapeHtml(
                                item.hostname
                            )}

                        </strong>

                    </td>


                    <td>

                        ${escapeHtml(
                            item.ip_address
                        )}

                    </td>


                    <td>

                        <span
                            class="
                                status
                                ${statusClass}
                            "
                        >

                            ${
                                item.status === "Online"
                                    ? "● Online"
                                    : "● Offline"
                            }

                        </span>

                    </td>


                    <td>

                        <span
                            class="${responseClass}"
                        >

                            ${escapeHtml(
                                item.response
                            )}

                        </span>

                    </td>


                    <td>

                        ${escapeHtml(
                            item.checked_at
                        )}

                    </td>


                </tr>

            `;

        }).join("");

}


// ==================================================
// HTML SECURITY
// ==================================================

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


// ==================================================
// ERROR
// ==================================================

function showError(
    message
) {

    const tableBody =
        document.getElementById(
            "deviceTableBody"
        );


    if (tableBody) {

        tableBody.innerHTML = `

            <tr>

                <td
                    colspan="8"
                    class="error"
                >

                    ${escapeHtml(
                        message
                    )}

                </td>

            </tr>

        `;

    }

}


// ==================================================
// START APPLICATION
// ==================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadDevices();

        loadHistory();

    }
);