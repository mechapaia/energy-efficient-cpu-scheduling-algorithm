import platform
from flask import Flask, render_template, request, jsonify
import psutil
from scheduler.models import Task, SchedulerConfig
from scheduler.engine import MLFQEngine
from scheduler.energy import get_dvfs_info
from scheduler.ai import get_ai_response

app = Flask(__name__)

# Default workload configuration for the simulator
DEFAULT_TASKS = [
    {"tid": 1, "name": "SensorRead",   "arrival_time": 0,  "burst_time": 3,  "deadline": 18},
    {"tid": 2, "name": "MotorControl", "arrival_time": 0,  "burst_time": 6,  "deadline": 22},
    {"tid": 3, "name": "DataLog",      "arrival_time": 2,  "burst_time": 10, "deadline": 43},
    {"tid": 4, "name": "CommTx",       "arrival_time": 3,  "burst_time": 4,  "deadline": 26},
    {"tid": 5, "name": "ImageProc",    "arrival_time": 5,  "burst_time": 12, "deadline": 49},
    {"tid": 6, "name": "Heartbeat",    "arrival_time": 7,  "burst_time": 2,  "deadline": 13},
    {"tid": 7, "name": "FaultCheck",   "arrival_time": 10, "burst_time": 5,  "deadline": 41},
    {"tid": 8, "name": "Encryption",   "arrival_time": 12, "burst_time": 8,  "deadline": 51},
]

@app.route('/')
def index():
    """Renders the main dashboard page."""
    return render_template('index.html', dvfs_info=get_dvfs_info())

@app.route('/api/simulate', methods=['POST'])
def simulate():
    """Runs the MLFQ scheduling simulation based on user input."""
    data = request.json
    
    # Parse configuration
    cfg_data = data.get('config', {})
    config = SchedulerConfig(
        num_queues=int(cfg_data.get('num_queues', 3)),
        time_quanta=tuple(cfg_data.get('time_quanta', [2, 4, 8])),
        boost_interval=int(cfg_data.get('boost_interval', 20))
    )
    
    # Parse tasks
    task_data = data.get('tasks', DEFAULT_TASKS)
    tasks = [
        Task(
            tid=int(t['tid']),
            name=t['name'],
            arrival_time=int(t['arrival_time']),
            burst_time=int(t['burst_time']),
            deadline=int(t['deadline'])
        ) for t in task_data
    ]
        
    engine = MLFQEngine(config)
    engine.load_tasks(tasks)
    result = engine.run_full()
    
    return jsonify(result)

def get_clean_processes():
    """
    Returns a list of the top active processes with their PID, Name, CPU usage percentage,
    and estimated wattage usage based on a 45W TDP.
    """
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'status']):
        try:
            pinfo = proc.info
            name = pinfo.get('name', '')
            cpu_percent = pinfo.get('cpu_percent', 0.0)
            status = pinfo.get('status', '')
            
            # Filter: Exclude common idle/system background tasks for clarity
            if name and name != 'System Idle Process':
                # Energy Math: estimated_watts = TDP * (cpu_percent / 100)
                pinfo['estimated_wattage'] = 45 * (cpu_percent / 100.0)
                processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Sort: Suspended/Stopped tasks first, then by CPU Usage
    processes.sort(
        key=lambda x: (x.get('status') in ['stopped', 'suspended'], x.get('cpu_percent', 0)), 
        reverse=True
    )
    return processes[:40]

def detect_scheduling_algorithm():
    """Detects the scheduling algorithm used by the host operating system."""
    os_type = platform.system()

    if os_type == "Linux":
        try:
            with open("/sys/kernel/debug/sched/features", "r") as f:
                features = f.read()
                if "eevdf" in features:
                    return "Linux CFS (EEVDF)"
                return "Linux CFS"
        except (FileNotFoundError, PermissionError):
            return "Linux CFS (Standard)"

    if os_type == "Windows":
        return "Windows Priority-Based MLFQ"

    return f"{os_type} Standard Scheduler"

# Flask routes
@app.route('/api/top-processes', methods=['GET'])
def api_top_processes():
    return jsonify(get_clean_processes())

@app.route('/api/os-algorithm', methods=['GET'])
def api_os_algorithm():
    return jsonify({"algorithm": detect_scheduling_algorithm(), "os": platform.system()})

@app.route('/api/process-control', methods=['POST'])
def api_process_control():
    data = request.json
    pid = data.get('pid')
    action = data.get('action')
    
    try:
        proc = psutil.Process(pid)
        if action == 'kill':
            proc.terminate()
            msg = f"Process {pid} terminated."
        elif action == 'suspend':
            proc.suspend()
            msg = f"Process {pid} paused."
        elif action == 'resume':
            proc.resume()
            msg = f"Process {pid} resumed."
        else:
            return jsonify({"success": False, "error": "Invalid action"}), 400
            
        return jsonify({"success": True, "message": msg})
    except psutil.AccessDenied:
        return jsonify({"success": False, "error": "Access Denied. Run as admin?"}), 403
    except psutil.NoSuchProcess:
        return jsonify({"success": False, "error": "Process no longer exists."}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """AI Chatbot endpoint."""
    data = request.json
    message = data.get('message')
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    response = get_ai_response(message)
    return jsonify({"response": response})

if __name__ == '__main__':
    # Initial call to psutil to avoid 0% on first fetch
    psutil.cpu_percent(interval=0.1)
    app.run(debug=True, port=5000)
