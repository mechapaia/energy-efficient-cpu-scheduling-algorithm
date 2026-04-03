import heapq

def compute_energy(level, time):
    levels = {
        "LOW": (0.8, 1.0),
        "MEDIUM": (1.0, 1.5),
        "HIGH": (1.2, 2.0)
    }
    V, f = levels[level]
    return (V**2) * f * time


def energy_scheduler(processes):
    time = 0
    total_energy = 0
    ready = []
    gantt = []
    i = 0

    # sort by arrival time
    processes.sort(key=lambda x: x["arrival"])

    while i < len(processes) or ready:

        # add arrived processes
        while i < len(processes) and processes[i]["arrival"] <= time:
            heapq.heappush(ready, (processes[i]["burst"], processes[i]["pid"], processes[i]))
            i += 1

        if ready:
            _, _, p = heapq.heappop(ready)

            # load-based DVFS
            load = len(ready)

            if load <= 1:
                level = "LOW"
                speed = 0.8
            elif load <= 3:
                level = "MEDIUM"
                speed = 1
            else:
                level = "HIGH"
                speed = 1.2

            exec_time = 1
            actual_time = exec_time / speed

            start = time
            time += actual_time

            p["burst"] -= exec_time
            energy = compute_energy(level, actual_time)
            total_energy += round(energy, 4)

            gantt.append((p["pid"], start, time, level))

            if p["burst"] > 0:
                heapq.heappush(ready, (p["burst"], p["pid"], p))
            else:
                p["completion"] = time
        else:
            time += 1
            
    return gantt, total_energy
