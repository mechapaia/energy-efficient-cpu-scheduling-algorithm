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
    time, energy = 0, 0
    ready = []
    gantt = []
    i = 0

    processes.sort(key=lambda x: x["arrival"])

    while i < len(processes) or ready:
        # Add arriving processes
        while i < len(processes) and processes[i]["arrival"] <= time:
            heapq.heappush(ready, (processes[i]["burst"], processes[i]["pid"], processes[i]))
            i += 1

        if ready:
            _, _, p = heapq.heappop(ready)

            load = len(ready)
            if load <= 1:
                level = "LOW"
                speed = 0.8   # slightly improved balance
            elif load <= 3:
                level = "MEDIUM"
                speed = 1
            else:
                level = "HIGH"
                speed = 1.2   # reduced from 1.5

            exec_time = 1
            actual = exec_time / speed

            start = time
            time += actual

            p["burst"] -= exec_time
            energy += compute_energy(level, actual)

            gantt.append({
                "pid": p["pid"],
                "start": start,
                "end": time,
                "level": level
            })

            # ❗ FIXED HERE (added pid as tie-breaker)
            if p["burst"] > 0:
                heapq.heappush(ready, (p["burst"], p["pid"], p))
            else:
                p["completion"] = time
        else:
            time += 1

    return gantt, energy