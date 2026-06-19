from dataclasses import dataclass, field
from typing import Dict, List, Optional
import datetime


@dataclass
class Technician:
    id: str
    name: str
    specialty: str
    queue: List[Dict] = field(default_factory=list)
    available: bool = True

    @property
    def queue_length(self) -> int:
        return len(self.queue)

    @property
    def estimated_wait(self) -> float:
        return sum(item.get("duration_minutes", 0) for item in self.queue)

    def assign_ticket(self, ticket: Dict) -> None:
        self.queue.append(ticket)


class GreedyRouter:
    def __init__(
        self,
        technicians: List[Technician],
        category_durations: Dict[str, float],
        mismatch_penalty: float = 120.0,
        overload_penalty_factor: float = 12.0,
    ):
        self.technicians: Dict[str, Technician] = {tech.id: tech for tech in technicians}
        self.category_durations = category_durations
        self.mismatch_penalty = mismatch_penalty
        self.overload_penalty_factor = overload_penalty_factor

    def build_ticket(self, text: str, category: str, urgency: int) -> Dict:
        duration = float(self.category_durations.get(category, 25.0))
        return {
            "text": text,
            "category": category,
            "urgency": urgency,
            "duration_minutes": duration,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

    def score_candidate(self, technician: Technician, ticket: Dict) -> Dict[str, float]:
        urgency = ticket["urgency"]
        estimated_wait = technician.estimated_wait
        specialty_penalty = 0.0 if technician.specialty == ticket["category"] else self.mismatch_penalty
        overload_penalty = max(0, technician.queue_length - 2) * self.overload_penalty_factor
        score = urgency * estimated_wait + specialty_penalty + overload_penalty
        if not technician.available:
            score += 100.0
        return {
            "score": score,
            "estimated_wait": estimated_wait,
            "specialty_penalty": specialty_penalty,
            "overload_penalty": overload_penalty,
            "queue_length": technician.queue_length,
            "technician_name": technician.name,
        }

    def select(self, ticket: Dict) -> tuple[Optional[Technician], Dict[str, float]]:
        best_technician = None
        best_metrics: Dict[str, float] = {}
        for technician in self.technicians.values():
            candidate_metrics = self.score_candidate(technician, ticket)
            if best_technician is None or candidate_metrics["score"] < best_metrics["score"]:
                best_technician = technician
                best_metrics = candidate_metrics
        return best_technician, best_metrics

    def assign(self, ticket: Dict) -> tuple[Optional[Technician], Dict[str, float]]:
        technician, metrics = self.select(ticket)
        if technician:
            technician.assign_ticket(ticket)
        return technician, metrics

    def get_technicians(self) -> List[Technician]:
        return list(self.technicians.values())
