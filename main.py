from energy import energy_scheduler

def calculate_metrics(processes):
    n = len(processes)

    tat = sum(p["completion"] - p["arrival"] for p in processes) / n
    wt = sum((p["completion"] - p["arrival"] - p["original"]) for p in processes) / n

    return tat, wt


def print_gantt(gantt):
    print("\nGantt Chart:")
    for task in gantt:
        pid, start, end, level = task
        print(f"P{pid} [{start:.2f} - {end:.2f}] ({level})")


def main():
    processes = []

    n = int(input("Enter number of processes: "))

    for i in range(n):
        arrival = int(input(f"Arrival time of P{i+1}: "))
        burst = int(input(f"Burst time of P{i+1}: "))

        processes.append({
            "pid": i + 1,
            "arrival": arrival,
            "burst": burst,
            "original": burst
        })

    gantt, energy = energy_scheduler(processes)
    tat, wt = calculate_metrics(processes)

    print_gantt(gantt)

    print("\n--- Results ---")
    print(f"Total Energy: {energy:.2f}")
    print(f"Average Turnaround Time: {tat:.2f}")
    print(f"Average Waiting Time: {wt:.2f}")


if __name__ == "__main__":
    main()