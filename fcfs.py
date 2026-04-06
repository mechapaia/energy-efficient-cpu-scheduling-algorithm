from energy import compute_energy

def fcfs(processes):
    time = 0
    energy = 0
    gantt = []

    processes.sort(key=lambda x: x["arrival"])

    for p in processes:
        if time < p["arrival"]:
            time = p["arrival"]

        start = time
        time += p["burst"]

        gantt.append((p["pid"], start, time))
        energy += compute_energy("HIGH", p["burst"])

        p["completion"] = time

    return gantt, energy