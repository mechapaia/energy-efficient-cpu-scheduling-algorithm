from energy import energy_scheduler
from fcfs import fcfs
from srtf import srtf
from rr import rr
import copy


def calculate_metrics(processes):
    n = len(processes)
    tat = sum(p["completion"] - p["arrival"] for p in processes) / n
    wt = sum((p["completion"] - p["arrival"] - p["original"]) for p in processes) / n
    return tat, wt


def print_results(name, gantt, energy, tat, wt):
    print(f"\n{name} Results:")
    print("-" * 30)
    print(f"Energy: {energy:.2f}")
    print(f"Avg TAT: {tat:.2f}")
    print(f"Avg WT: {wt:.2f}")


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

    # FCFS
    p1 = copy.deepcopy(processes)
    g1, e1 = fcfs(p1)
    tat1, wt1 = calculate_metrics(p1)

    # SRTF
    p2 = copy.deepcopy(processes)
    g2, e2 = srtf(p2)
    tat2, wt2 = calculate_metrics(p2)

    # RR
    p3 = copy.deepcopy(processes)
    g3, e3 = rr(p3)
    tat3, wt3 = calculate_metrics(p3)

    # Energy-Aware
    p4 = copy.deepcopy(processes)
    g4, e4 = energy_scheduler(p4)
    tat4, wt4 = calculate_metrics(p4)

    # PRINT
    print_results("FCFS", g1, e1, tat1, wt1)
    print_results("SRTF", g2, e2, tat2, wt2)
    print_results("Round Robin", g3, e3, tat3, wt3)
    print_results("Energy-Aware", g4, e4, tat4, wt4)


if __name__ == "__main__":
    main()