from collections import deque
from energy import compute_energy

def rr(processes, q=2):
    time = 0
    energy = 0
    gantt = []

    processes.sort(key=lambda x: x["arrival"])
    queue = deque()
    i = 0

    while i < len(processes) or queue:

        while i < len(processes) and processes[i]["arrival"] <= time:
            queue.append(processes[i])
            i += 1

        if queue:
            p = queue.popleft()

            exec_time = min(q, p["burst"])

            start = time
            time += exec_time

            p["burst"] -= exec_time
            energy += compute_energy("HIGH", exec_time)

            gantt.append((p["pid"], start, time))

            while i < len(processes) and processes[i]["arrival"] <= time:
                queue.append(processes[i])
                i += 1

            if p["burst"] > 0:
                queue.append(p)
            else:
                p["completion"] = time
        else:
            time += 1

    return gantt, energy