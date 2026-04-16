const DEFAULT_TASKS = [
    { tid: 1, name: "SensorRead", arrival_time: 0, burst_time: 3, deadline: 8 },
    { tid: 2, name: "MotorControl", arrival_time: 0, burst_time: 6, deadline: 12 },
    { tid: 3, name: "DataLog", arrival_time: 2, burst_time: 10, deadline: 30 },
    { tid: 4, name: "CommTx", arrival_time: 3, burst_time: 4, deadline: 15 },
    { tid: 5, name: "ImageProc", arrival_time: 5, burst_time: 12, deadline: 35 }
];

let tasks = [...DEFAULT_TASKS];

// Initialize UI
document.addEventListener('DOMContentLoaded', () => {
    // Initial setup
        renderTasksTable();
        document.getElementById('cfg-queues').value = 3;
        document.getElementById('cfg-quanta').value = "2, 4, 8";
        updateDvfsLegend(3); // Sync legend with default num_queues 

    document.getElementById('add-task-btn').addEventListener('click', () => {
        const nextId = tasks.length > 0 ? Math.max(...tasks.map(t => t.tid)) + 1 : 1;
        tasks.push({
            tid: nextId,
            name: `Task_${nextId}`,
            arrival_time: 0,
            burst_time: 5,
            deadline: 20
        });
        renderTasksTable();
    });

    // Dynamic Queue Logic
    const queueInput = document.getElementById('cfg-queues');
    const quantaInput = document.getElementById('cfg-quanta');
    
    queueInput.addEventListener('change', () => {
        const num = parseInt(queueInput.value, 10);
        // Regenerate default quanta: 2, 4, 8, 16, 32
        const defaults = [2, 4, 8, 16, 32].slice(0, num);
        quantaInput.value = defaults.join(', ');
        updateDvfsLegend(num);
    });

    document.getElementById('config-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await runSimulation();
    });

    // Tab switching logic
    const tabSim = document.getElementById('tab-sim');
    const tabLive = document.getElementById('tab-live');
    const viewSim = document.getElementById('view-simulation');
    const viewLive = document.getElementById('view-live');

    let activeTab = 'sim';
    let livePollInterval = null;

    function switchTab(target) {
        if (target === 'sim') {
            activeTab = 'sim';
            tabSim.classList.add('active');
            tabLive.classList.remove('active');
            viewSim.classList.add('active');
            viewLive.classList.remove('active');
            
            tabSim.textContent = 'Simulator Mode';
            tabLive.textContent = 'Switch to Live';
            
            // Stop live polling
            if (livePollInterval) {
                clearInterval(livePollInterval);
                livePollInterval = null;
            }
        } else {
            activeTab = 'live';
            tabLive.classList.add('active');
            tabSim.classList.remove('active');
            viewLive.classList.add('active');
            viewSim.classList.remove('active');
            
            tabSim.textContent = 'Switch to Simulator';
            tabLive.textContent = 'Live System';
            
            // Start live polling
            pollSystemProcessView();
            livePollInterval = setInterval(pollSystemProcessView, 5000);
        }
    }

    tabSim.addEventListener('click', () => switchTab('sim'));
    tabLive.addEventListener('click', () => switchTab('live'));

    // Chatbot logic
    const chatInput = document.getElementById('chat-input');
    const sendChatBtn = document.getElementById('send-chat-btn');
    const chatDisplay = document.getElementById('chat-display');

    async function sendChatMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        appendMessage('user', message);
        chatInput.value = '';

        // Show typing indicator
        const typingId = appendMessage('system', 'AI is thinking...');

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            const data = await res.json();
            
            // Remove typing indicator
            document.getElementById(typingId).remove();

            if (data.response) {
                appendMessage('bot', data.response);
            } else {
                appendMessage('system', 'Error: ' + (data.error || 'Unknown error'));
            }
        } catch (e) {
            if (document.getElementById(typingId)) document.getElementById(typingId).remove();
            appendMessage('system', 'Failed to connect to AI service.');
            console.error(e);
        }
    }

    let messageCounter = 0;
    function appendMessage(role, text) {
        const msgDiv = document.createElement('div');
        const id = 'chat-msg-' + (messageCounter++); 
        msgDiv.id = id;
        msgDiv.className = `chat-message ${role}`;
        
        if (role === 'bot') {
            // Render Markdown for AI responses
            msgDiv.innerHTML = marked.parse(text);
        } else {
            msgDiv.textContent = text;
        }

        chatDisplay.appendChild(msgDiv);
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
        document.querySelector('.ai-chatbot').classList.add('expanded');
        return id;
    }

    sendChatBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });

});

async function pollSystemProcessView() {
    try {
        // Fetch OS & Algorithm info
        const osRes = await fetch('/api/os-algorithm');
        if (osRes.ok) {
            const data = await osRes.json();
            document.getElementById('os-name').textContent = data.os;
            document.getElementById('os-algorithm').textContent = data.algorithm;
        }

        // Fetch Top Processes
        const processRes = await fetch('/api/top-processes');
        if (processRes.ok) {
            const processData = await processRes.json();
            const tbody = document.getElementById('process-tbody');
            tbody.innerHTML = '';

            processData.forEach(proc => {
                const tr = document.createElement('tr');
                const isPaused = proc.status === 'stopped' || proc.status === 'suspended';
                if (isPaused) tr.classList.add('row-paused');

                const watts = proc.estimated_wattage;
                let powerClass = 'power-low';
                if (watts > 10) powerClass = 'power-high';
                else if (watts > 2) powerClass = 'power-med';

                const cpuDisplay = isPaused ? 
                    `<span class="badge paused">PAUSED</span>` : 
                    `${proc.cpu_percent.toFixed(1)}%`;

                tr.innerHTML = `
                    <td><code>${proc.pid}</code></td>
                    <td><strong>${proc.name}</strong></td>
                    <td>${cpuDisplay}</td>
                    <td class="${powerClass}" style="font-weight: 600;">${watts.toFixed(2)} W</td>
                    <td>
                        <div class="action-btns">
                            <button onclick="controlProcess(${proc.pid}, 'suspend')" class="ctrl-btn pause" title="Pause">⏸</button>
                            <button onclick="controlProcess(${proc.pid}, 'resume')" class="ctrl-btn resume" title="Resume">▶</button>
                            <button onclick="controlProcess(${proc.pid}, 'kill')" class="ctrl-btn kill" title="Terminate">✕</button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (e) {
        console.error("Failed to poll system process view", e);
    }
}

async function controlProcess(pid, action) {
    try {
        const res = await fetch('/api/process-control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pid, action })
        });
        const data = await res.json();
        if (data.success) {
            console.log(data.message);
        } else {
            alert(data.error);
        }
    } catch (e) {
        console.error("Control API call failed", e);
    }
}

function renderTasksTable() {
    const tbody = document.getElementById('tasks-tbody');
    tbody.innerHTML = '';

    tasks.forEach((task, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${task.tid}</td>
            <td><input type="text" value="${task.name}" onchange="updateTask(${index}, 'name', this.value)"></td>
            <td><input type="number" min="0" value="${task.arrival_time}" onchange="updateTask(${index}, 'arrival_time', this.value)"></td>
            <td><input type="number" min="1" value="${task.burst_time}" onchange="updateTask(${index}, 'burst_time', this.value)"></td>
            <td><input type="number" min="1" value="${task.deadline}" onchange="updateTask(${index}, 'deadline', this.value)"></td>
            <td><button class="remove-btn" onclick="removeTask(${index})">×</button></td>
        `;
        tbody.appendChild(tr);
    });
}

window.updateTask = function(index, field, value) {
    if (field === 'name') {
        tasks[index][field] = value;
    } else {
        tasks[index][field] = parseInt(value, 10);
    }
};

window.removeTask = function(index) {
    tasks.splice(index, 1);
    renderTasksTable();
};

async function runSimulation() {
    const config = {
        num_queues: parseInt(document.getElementById('cfg-queues').value, 10),
        time_quanta: document.getElementById('cfg-quanta').value.split(',').map(n => parseInt(n.trim(), 10)),
        boost_interval: parseInt(document.getElementById('cfg-boost').value, 10)
    };

    const payload = {
        config: config,
        tasks: tasks
    };

    const btn = document.querySelector('button[type="submit"]');
    btn.textContent = 'Simulating...';
    btn.disabled = true;

    try {
        const res = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        renderResults(data);
    } catch (e) {
        console.error("Simulation failed:", e);
        alert("Failed to run simulation. Check console.");
    } finally {
        btn.textContent = 'Run Simulation';
        btn.disabled = false;
    }
}

function renderResults(data) {
    // Top stats
    document.getElementById('res-energy').textContent = data.total_energy.toFixed(2);
    if (document.getElementById('res-energy-saved')) {
        document.getElementById('res-energy-saved').textContent = data.energy_saved.toFixed(2);
    }
    
    const met = data.completed_tasks.filter(t => t.deadline_met).length;
    const total = data.completed_tasks.length;
    const hitRate = total > 0 ? ((met / total) * 100).toFixed(1) : 0;
    document.getElementById('res-hitrate').textContent = hitRate;

    // Task Results Table
    const resultsTbody = document.getElementById('results-tbody');
    resultsTbody.innerHTML = '';
    data.completed_tasks.forEach(task => {
        const tr = document.createElement('tr');
        const statusClass = task.deadline_met ? 'status-met' : 'status-miss';
        const statusText = task.deadline_met ? '✓ Met' : '✗ Missed';
        tr.innerHTML = `
            <td>${task.tid}</td>
            <td><strong>${task.name}</strong></td>
            <td>${task.wait_time}</td>
            <td style="color: #3b82f6;">${task.energy_consumed.toFixed(2)} J</td>
            <td class="${statusClass}">${statusText}</td>
        `;
        resultsTbody.appendChild(tr);
    });

    // Timeline Rendering
    const timelineContainer = document.getElementById('timeline');
    const timeline = document.createElement('div');
    timeline.className = 'timeline';

    data.trace.forEach(tick => {
        const block = document.createElement('div');
        block.className = 'tick-block';
        
        let qClass = 'idle';
        let taskName = 'Idle';
        let qName = '-';
        if (tick.queue_level !== null) {
            qClass = `q${tick.queue_level}`;
            qName = `Q${tick.queue_level}`;
            const taskObj = data.completed_tasks.find(kt => kt.tid === tick.running_task);
            taskName = taskObj ? taskObj.name : `Task ${tick.running_task}`;
        }
        
        block.classList.add(qClass);

        const info = `<div class="tick-info">
                        <strong>${taskName}</strong><br/>
                        Tick: ${tick.tick}<br/>
                        Queue: ${qName}<br/>
                        Event: ${tick.event || 'Run'}
                      </div>`;
        
        block.innerHTML = info;
        timeline.appendChild(block);
    });

    timelineContainer.innerHTML = '';
    timelineContainer.appendChild(timeline);
}

function updateDvfsLegend(numQueues) {
    const list = document.getElementById('dvfs-list');
    const levels = [
        { name: "HIGH_PERF", power: "24.000W" },
        { name: "BALANCED",  power: "13.500W" },
        { name: "ECO_SAVE",  power: "6.400W" },
        { name: "ULTRA_ECO", power: "3.920W" },
        { name: "MIN_POWER", power: "1.800W" }
    ];

    list.innerHTML = '';
    for (let i = 0; i < numQueues; i++) {
        const li = document.createElement('li');
        li.innerHTML = `
            <span class="ql">Q${i}</span>
            <span class="qv">${levels[i].name}</span>
            <span class="qp">${levels[i].power}</span>
        `;
        list.appendChild(li);
    }

    // Update Timeline Legend
    const legend = document.getElementById('timeline-legend');
    if (legend) {
        const legendLabels = ["High", "Balanced", "Eco", "Ultra Eco", "Min Power"];
        legend.innerHTML = '';
        
        for (let i = 0; i < numQueues; i++) {
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.innerHTML = `<span class="dot q${i}"></span> Q${i} (${legendLabels[i]})`;
            legend.appendChild(item);
        }
        // Always add Idle
        const idleItem = document.createElement('div');
        idleItem.className = 'legend-item';
        idleItem.innerHTML = `<span class="dot idle"></span> Idle`;
        legend.appendChild(idleItem);
    }
}