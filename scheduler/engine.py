"""
The core MLFQ simulation engine.
Executes the simulation tick-by-tick and generates a trace.
"""

from collections import deque
from typing import Optional

from .models import Task, SchedulerConfig, TickRecord
from .energy import get_power_for_queue, IDLE_POWER_WATTS


class MLFQEngine:
    """Multi-Level Feedback Queue scheduler simulator."""

    def __init__(self, config: Optional[SchedulerConfig] = None):
        self.cfg = config or SchedulerConfig()
        self.queues: list[deque[Task]] = [deque() for _ in range(self.cfg.num_queues)]
        self.tasks: list[Task] = []
        self.completed: list[Task] = []
        self.tick: int = 0
        self.total_energy: float = 0.0
        self.trace: list[TickRecord] = []
        self._ticks_since_boost: int = 0
        self.max_ticks = 1000  # safety threshold

    def load_tasks(self, tasks: list[Task]) -> None:
        """Load tasks into the system, sorted by arrival time."""
        self.tasks = sorted(tasks, key=lambda t: t.arrival_time)
        # Reset state
        self.queues = [deque() for _ in range(self.cfg.num_queues)]
        self.completed = []
        self.tick = 0
        self.total_energy = 0.0
        self.trace = []
        self._ticks_since_boost = 0

    def step(self, pending: list[Task], active_set: set[int]) -> bool:
        """Executes a single tick of the simulation.
        Returns True if the simulation should continue, False if done.
        """
        if not pending and not active_set:
            return False
            
        if self.tick > self.max_ticks:
            print("[!] Maximum tick limit reached. Aborting.")
            return False

        # ── 1. Admit newly arrived tasks ──────────────────
        while pending and pending[0].arrival_time <= self.tick:
            task = pending.pop(0)
            task.current_queue = 0
            task.quantum_used = 0
            self.queues[0].append(task)
            active_set.add(task.tid)

        # ── 2. Priority boost (anti-starvation) ──────────
        event_notes: list[str] = []
        self._ticks_since_boost += 1
        if self._ticks_since_boost >= self.cfg.boost_interval:
            self._priority_boost()
            self._ticks_since_boost = 0
            event_notes.append("BOOST")

        # ── 3. Pick the highest-priority task ─────────────
        task = self._pick_next_task()

        if task is None:
            # CPU is idle
            power = IDLE_POWER_WATTS
            energy = power  # × 1 tick
            self.total_energy += energy
            self.trace.append(TickRecord(
                tick=self.tick, running_task=None, queue_level=None,
                power_watts=power, energy_joule=energy,
                event="IDLE"))
            self.tick += 1
            return True

        # ── 4. Execute one tick ───────────────────────────
        q_level = task.current_queue
        power = get_power_for_queue(q_level)
        energy = power  # × 1 tick

        if task.first_run_time is None:
            task.first_run_time = self.tick

        task.remaining_burst -= 1
        task.quantum_used += 1
        task.energy_consumed += energy
        self.total_energy += energy

        # ── 5. Check completion ───────────────────────────
        if task.remaining_burst == 0:
            task.completion_time = self.tick + 1
            task.deadline_met = (task.completion_time <= task.deadline)
            self.completed.append(task)
            active_set.discard(task.tid)
            event_notes.append(
                f"COMPLETED({'✓ on-time' if task.deadline_met else '✗ MISSED'})")

        # ── 6. Check quantum exhaustion → demotion ────────
        elif task.quantum_used >= self.cfg.time_quanta[q_level]:
            task.quantum_used = 0
            old_q = task.current_queue
            if task.current_queue < self.cfg.num_queues - 1:
                task.current_queue += 1
                event_notes.append(f"DEMOTED Q{old_q}→Q{task.current_queue}")
            self.queues[task.current_queue].append(task)

        else:
            # Task still has quantum left
            self.queues[q_level].appendleft(task)

        # ── 7. Accumulate wait time for other active tasks 
        for q in self.queues:
            for t in q:
                if t.tid != task.tid:
                    t.wait_time += 1

        # ── 8. Record trace ───────────────────────────────
        self.trace.append(TickRecord(
            tick=self.tick,
            running_task=task.tid,
            queue_level=q_level,
            power_watts=power,
            energy_joule=energy,
            event=" | ".join(event_notes) if event_notes else "RUN"
        ))

        self.tick += 1
        return True

    def run_full(self) -> dict:
        """Run the simulation to completion and return result summary."""
        pending = list(self.tasks)
        active_set: set[int] = set()

        self.max_ticks = sum(t.burst_time for t in self.tasks) + max(
            (t.arrival_time for t in self.tasks), default=0) + 100

        while self.step(pending, active_set):
            pass

        return self.get_summary()

    def get_summary(self) -> dict:
        """Generate final simulation statistics."""
        normal_power = get_power_for_queue(0)
        idle_power = IDLE_POWER_WATTS
        
        normal_energy = sum(
            normal_power if tr.running_task is not None else idle_power 
            for tr in self.trace
        )

        return {
            "total_ticks": self.tick,
            "total_energy": round(self.total_energy, 3),
            "normal_energy": round(normal_energy, 3),
            "energy_saved": round(normal_energy - self.total_energy, 3),
            "trace": [tr.to_dict() for tr in self.trace],
            "completed_tasks": [t.to_dict() for t in self.completed],
        }

    # ── Internal ──────────────────────────────────────────────
    def _pick_next_task(self) -> Optional[Task]:
        """Return the next task from the highest non-empty queue (FIFO)."""
        for q in self.queues:
            if q:
                return q.popleft()
        return None

    def _priority_boost(self) -> None:
        """Move ALL tasks to Queue 0 to prevent starvation."""
        for level in range(1, self.cfg.num_queues):
            while self.queues[level]:
                task = self.queues[level].popleft()
                task.current_queue = 0
                task.quantum_used = 0
                self.queues[0].append(task)
