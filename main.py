import heapq
import copy


def compute_energy(level, time):
    levels = {
        "LOW": (0.8, 1.0),
        "MEDIUM": (1.0, 1.5),
        "HIGH": (1.2, 2.0)
    }
    V, f = levels[level]
    return round((V**2) * f * time, 4)


def energy_scheduler(processes):
    processes = copy.deepcopy(processes)

    time = 0
    total_energy = 0
    ready = []
    gantt = []
    i = 0

    processes.sort(key=lambda x: x["arrival"])

    while True:

        # Add processes that have arrived
        while i < len(processes) and processes[i]["arrival"] <= time:
            heapq.heappush(ready, (processes[i]["burst"], processes[i]["pid"], processes[i]))
            i += 1

        # If nothing is left
        if not ready and i >= len(processes):
            break

        if ready:
            _, _, p = heapq.heappop(ready)

            load = len(ready)

            if load <= 1:
                level = "LOW"
                speed = 0.8
            elif load <= 3:
                level = "MEDIUM"
                speed = 1.0
            else:
                level = "HIGH"
                speed = 1.2

            exec_time = 1
            actual_time = exec_time / speed

            start = time
            time += actual_time

            p["burst"] -= exec_time
            energy = compute_energy(level, actual_time)
            total_energy += energy

            gantt.append((p["pid"], round(start, 3), round(time, 3), level))

            if p["burst"] > 0:
                heapq.heappush(ready, (p["burst"], p["pid"], p))
            else:
                p["completion"] = round(time, 3)

        else:
            # Jump to next process arrival
            if i < len(processes):
                time = processes[i]["arrival"]

    return gantt, round(total_energy, 4)
    processes = [
    {"pid": "P1", "arrival": 0, "burst": 5},
    {"pid": "P2", "arrival": 1, "burst": 3},
    {"pid": "P3", "arrival": 2, "burst": 2}
]

gantt, energy = energy_scheduler(processes)

print("Gantt:", gantt)
print("Energy:", energy)
