"""
Data models for the MLFQ CPU Scheduler.
Defines Task, DVFSLevel, TickRecord, and SchedulerConfig.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DVFSLevel:
    """Dynamic Voltage and Frequency Scaling state."""
    name: str
    voltage: float       # Volts
    frequency: float     # GHz
    capacitance: float   # nF (effective switched capacitance)

    @property
    def power(self) -> float:
        """Instantaneous dynamic power: P = C * V^2 * f  (Watts).

        With capacitance in nF and frequency in GHz the SI prefixes cancel:
            nF * V^2 * GHz  =  10^-9 * V^2 * 10^9  =  V^2  (Watts)
        """
        return self.capacitance * (self.voltage ** 2) * self.frequency

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "voltage": self.voltage,
            "frequency": self.frequency,
            "capacitance": self.capacitance,
            "power": round(self.power, 3),
        }


@dataclass
class Task:
    """A schedulable unit of work with burst time and deadline."""
    tid: int
    name: str
    arrival_time: int
    burst_time: int
    deadline: int

    # ── Runtime state (mutated by the scheduler) ──
    remaining_burst: int = 0
    current_queue: int = 0
    quantum_used: int = 0
    completion_time: Optional[int] = None
    first_run_time: Optional[int] = None
    wait_time: int = 0
    energy_consumed: float = 0.0
    deadline_met: bool = False

    def __post_init__(self):
        if self.remaining_burst == 0:
            self.remaining_burst = self.burst_time

    @property
    def turnaround_time(self) -> Optional[int]:
        if self.completion_time is not None:
            return self.completion_time - self.arrival_time
        return None

    @property
    def response_time(self) -> Optional[int]:
        if self.first_run_time is not None:
            return self.first_run_time - self.arrival_time
        return None

    def to_dict(self) -> dict:
        return {
            "tid": self.tid,
            "name": self.name,
            "arrival_time": self.arrival_time,
            "burst_time": self.burst_time,
            "deadline": self.deadline,
            "remaining_burst": self.remaining_burst,
            "current_queue": self.current_queue,
            "quantum_used": self.quantum_used,
            "completion_time": self.completion_time,
            "first_run_time": self.first_run_time,
            "wait_time": self.wait_time,
            "energy_consumed": round(self.energy_consumed, 3),
            "deadline_met": self.deadline_met,
            "turnaround_time": self.turnaround_time,
            "response_time": self.response_time,
        }


@dataclass
class TickRecord:
    """Snapshot of a single simulation tick."""
    tick: int
    running_task: Optional[int]      # tid or None (idle)
    queue_level: Optional[int]       # queue the task ran from
    power_watts: float
    energy_joule: float
    event: str = ""

    def to_dict(self) -> dict:
        return {
            "tick": self.tick,
            "running_task": self.running_task,
            "queue_level": self.queue_level,
            "power_watts": round(self.power_watts, 3),
            "energy_joule": round(self.energy_joule, 3),
            "event": self.event,
        }


@dataclass
class SchedulerConfig:
    """Tuneable MLFQ parameters."""
    num_queues: int = 3
    time_quanta: tuple[int, ...] = (2, 4, 8)
    boost_interval: int = 20

    def __post_init__(self):
        # Ensure time_quanta is a list for mutation
        self.time_quanta = list(self.time_quanta)

        # Ensure time_quanta matches num_queues
        current_len = len(self.time_quanta)
        if current_len < self.num_queues:
            # Pad with increments of 2 from the last available value
            last_val = self.time_quanta[-1] if self.time_quanta else 0
            for _ in range(self.num_queues - current_len):
                last_val += 2
                self.time_quanta.append(last_val)
        elif current_len > self.num_queues:
            # Truncate
            self.time_quanta = self.time_quanta[:self.num_queues]
        
        self.time_quanta = tuple(self.time_quanta)

    def to_dict(self) -> dict:
        return {
            "num_queues": self.num_queues,
            "time_quanta": list(self.time_quanta),
            "boost_interval": self.boost_interval,
        }
