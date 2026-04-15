from collections import deque
from scheduler.energy import compute_energy

def rr(processes, q=2):
    time = 0
    energy = 0
    gantt = []

    processes = sorted(processes, key=lambda x: x["arrival"])
    queue = deque()

    i = 0  # index for incoming processes

    while i < len(processes) or queue:

        # Add newly arrived processes
        while i < len(processes) and processes[i]["arrival"] <= time:
            queue.append(processes[i])
            i += 1

        if queue:
            p = queue.popleft()

            exec_time = min(q, p["burst"])

            start = time
            time += exec_time

            gantt.append({
                "pid": p["pid"],
                "start": start,
                "end": time
            })

            energy += compute_energy("HIGH", exec_time)

            p["burst"] -= exec_time

            # Add any new arrivals during execution
            while i < len(processes) and processes[i]["arrival"] <= time:
                queue.append(processes[i])
                i += 1

            if p["burst"] > 0:
                queue.append(p)
            else:
                p["completion"] = time

        else:
            # CPU idle
            time += 1

    return gantt, energy