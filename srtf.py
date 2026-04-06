import heapq
from energy import compute_energy

def srtf(processes):
    time = 0
    energy = 0
    ready = []
    gantt = []
    i = 0

    processes.sort(key=lambda x: x["arrival"])

    while i < len(processes) or ready:
        while i < len(processes) and processes[i]["arrival"] <= time:
            heapq.heappush(ready, (processes[i]["burst"], processes[i]["pid"], processes[i]))
            i += 1

        if ready:
            _, _, p = heapq.heappop(ready)

            start = time
            time += 1

            p["burst"] -= 1
            energy += compute_energy("HIGH", 1)

            gantt.append((p["pid"], start, time))

            if p["burst"] > 0:
                heapq.heappush(ready, (p["burst"], p["pid"], p))
            else:
                p["completion"] = time
        else:
            time += 1

    return gantt, energy