import heapq
from scheduler.energy import compute_energy

def sjf(processes):
    time = 0
    energy = 0
    gantt = []
    ready = []
    i = 0

    # Sort by arrival time
    processes.sort(key=lambda x: x["arrival"])

    while i < len(processes) or ready:

        # Add arrived processes
        while i < len(processes) and processes[i]["arrival"] <= time:
            heapq.heappush(
                ready,
                (processes[i]["burst"], processes[i]["arrival"], processes[i]["pid"], processes[i])
            )
            i += 1

        if ready:
            _, _, _, p = heapq.heappop(ready)

            start = time
            time += p["burst"]

            gantt.append({
                "pid": p["pid"],
                "start": start,
                "end": time
            })

            energy += compute_energy("HIGH", p["burst"])
            p["completion"] = time

        else:
            # CPU idle
            time += 1

    return gantt, energy