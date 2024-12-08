async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('processContainer').style.display = 'block';
            loadProcesses();
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during login');
    }
}

async function loadProcesses() {
    try {
        const response = await fetch('/processes');
        const processes = await response.json();

        const processList = document.getElementById('processList');
        processList.innerHTML = ''; // Clear existing list

        processes.forEach(process => {
            processList.appendChild(createProcessItem(process));
        });
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while loading processes');
    }
}

function createProcessItem(process) {
    const li = document.createElement('li');
    li.className = 'process-item';
    li.innerHTML = `
        <div class="process-name">${process.name}</div>
        <div class="process-options">
            <button onclick="runProcess(${process.id})">Run Process</button>
            <button onclick="showLogs(${process.id})">Show Logs</button>
        </div>
    `;
    li.addEventListener('click', (event) => toggleOptions(event, li));
    return li;
}

function toggleOptions(event, li) {
    if (event.target.tagName !== 'BUTTON') {
        const options = li.querySelector('.process-options');
        options.style.display = options.style.display === 'none' ? 'block' : 'none';
    }
}

function runProcess(id) {
    console.log(`Running process ${id}`);
    alert(`Process ${id} started`);
}

function showLogs(id) {
    console.log(`Showing logs for process ${id}`);
    alert(`Logs for process ${id}:\n\nSample log entry 1\nSample log entry 2`);
}
