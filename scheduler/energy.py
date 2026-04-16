"""
DVFS energy constants and helper functions.
Power formula:  P = C * V^2 * f
"""

from .models import DVFSLevel

# ── DVFS levels, one per priority queue ──────────────────────
DVFS_LEVELS: list[DVFSLevel] = [
    DVFSLevel(name="HIGH_PERF",  voltage=1.2, frequency=2.0, capacitance=10.0),
    DVFSLevel(name="BALANCED",   voltage=1.0, frequency=1.5, capacitance=10.0),
    DVFSLevel(name="ECO_SAVE",   voltage=0.8, frequency=1.0, capacitance=10.0),
    DVFSLevel(name="ULTRA_ECO",  voltage=0.7, frequency=0.8, capacitance=10.0),
    DVFSLevel(name="MIN_POWER",  voltage=0.6, frequency=0.5, capacitance=10.0),
]

# Static/leakage power when no task is running
IDLE_POWER_WATTS: float = 0.5


def get_power_for_queue(queue_level: int) -> float:
    """Return dynamic power (W) for a given queue level."""
    if 0 <= queue_level < len(DVFS_LEVELS):
        return DVFS_LEVELS[queue_level].power
    return IDLE_POWER_WATTS


def get_dvfs_info() -> list[dict]:
    """Return serialisable DVFS metadata for the API."""
    result = []
    for i, d in enumerate(DVFS_LEVELS):
        info = d.to_dict()
        info["queue"] = i
        info["formula"] = (
            f"P = {d.capacitance:.1f} * ({d.voltage:.2f})^2 "
            f"* {d.frequency:.1f} = {d.power:.3f} W"
        )
        result.append(info)
    return result
