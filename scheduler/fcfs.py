from scheduler.energy import compute_energy

def fcfs(processes):
    time = 0
    energy = 0
    gantt = []

    # Sort by arrival time
    processes = sorted(processes, key=lambda x: x["arrival"])

    for p in processes:
        if time < p["arrival"]:
            time = p["arrival"]

        start = time
        time += p["burst"]

        gantt.append({
            "pid": p["pid"],
            "start": start,
            "end": time
        })

        energy += compute_energy("HIGH", p["burst"])
        p["completion"] = time

    return gantt, energy