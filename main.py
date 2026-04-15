from flask import Flask, render_template, request, jsonify
import copy

from scheduler.fcfs import fcfs
from scheduler.sjf import sjf
from scheduler.rr import rr
from scheduler.energy import energy_scheduler
from scheduler.metrics import calculate_metrics

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/schedule", methods=["POST"])
def schedule():
    data = request.get_json()

    # ✅ Validate input
    if not data or "processes" not in data:
        return jsonify({"error": "Invalid input"}), 400

    processes = data["processes"]

    if len(processes) == 0:
        return jsonify({"error": "No processes provided"}), 400

    results = {}

    algorithms = {
        "fcfs": fcfs,
        "sjf": sjf,
        "rr": rr,
        "energy": energy_scheduler
    }

    for name, func in algorithms.items():

        # ✅ Deep copy (important fix)
        procs = copy.deepcopy(processes)

        # store original burst safely
        for p in procs:
            p["original"] = p["burst"]

        gantt, energy = func(procs)
        tat, wt = calculate_metrics(procs)

        results[name] = {
            "gantt": gantt,
            "energy": energy,
            "tat": tat,
            "wt": wt
        }

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)