def calculate_metrics(processes):
    n = len(processes)

    if n == 0:
        return 0, 0

    total_tat = 0
    total_wt = 0

    for p in processes:
        completion = p.get("completion", p["arrival"])  # safe fallback
        tat = completion - p["arrival"]
        wt = tat - p.get("original", p["burst"])

        total_tat += tat
        total_wt += wt

    return total_tat / n, total_wt / n