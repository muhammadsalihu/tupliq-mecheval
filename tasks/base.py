"""
Base Task definition and schema for MechEval benchmark tasks.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from graders.simulation_grader import StructuredGrader, ParameterSpec, GradingReport


class BaseTask(ABC):
    task_id: str
    title: str
    category: str
    description: str
    units_convention: str
    
    @abstractmethod
    def get_prompt(self) -> str:
        """Returns the complete, unambiguous prompt given to the evaluated AI model."""
        pass

    @abstractmethod
    def get_input_parameters(self) -> Dict[str, Any]:
        """Returns the dictionary of input engineering parameters."""
        pass

    @abstractmethod
    def get_reference_solution(self) -> Dict[str, Any]:
        """Computes the exact, verified reference solution dictionary."""
        pass

    @abstractmethod
    def get_grader_specs(self) -> List[ParameterSpec]:
        """Returns the list of parameter specifications and tolerances for grading."""
        pass

    def get_grader(self) -> StructuredGrader:
        """Instantiates the deterministic grader for this task."""
        return StructuredGrader(task_id=self.task_id, specs=self.get_grader_specs())

    def grade(self, candidate_solution: Dict[str, Any]) -> GradingReport:
        """Grades a candidate solution against the reference solution."""
        ref = self.get_reference_solution()
        grader = self.get_grader()
        return grader.grade(candidate_solution, ref)
