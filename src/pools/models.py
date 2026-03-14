"""Data models for DIVE-TOGAF resource pools."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any


class ToolType(str, Enum):
    RETRIEVAL = "retrieval"
    PROCESSING = "processing"


class ToolDomain(str, Enum):
    ADM = "adm"
    ARCHIMATE = "archimate"
    REPOSITORY = "repository"
    GOVERNANCE = "governance"
    GENERAL = "general"


class SeedCategory(str, Enum):
    TOGAF_PHASE = "togaf_phase"
    TOGAF_ARTIFACT = "togaf_artifact"
    TOGAF_TECHNIQUE = "togaf_technique"
    ARCHIMATE_ELEMENT = "archimate_element"
    ARCHIMATE_VIEWPOINT = "archimate_viewpoint"
    INDUSTRY_CASE = "industry_case"
    STANDARD = "standard"
    CAPABILITY = "capability"
    BUILDING_BLOCK = "building_block"
    STAKEHOLDER = "stakeholder"


class ExemplarFamily(str, Enum):
    RETRIEVE_COMPUTE = "retrieve_compute"
    MULTI_HOP_RETRIEVAL = "multi_hop_retrieval"
    COMPARE_DECIDE = "compare_decide"
    GAP_ANALYSIS = "gap_analysis"
    AGGREGATE = "aggregate"
    COMPLIANCE_CHECK = "compliance_check"
    RISK_ASSESSMENT = "risk_assessment"
    ROADMAP_PLANNING = "roadmap_planning"
    STAKEHOLDER_ANALYSIS = "stakeholder_analysis"
    COST_BENEFIT = "cost_benefit"


@dataclass
class ToolParameter:
    name: str
    type: str
    description: str
    required: bool = True
    enum: list[str] | None = None
    default: Any = None


@dataclass
class ToolDefinition:
    id: str
    name: str
    description: str
    tool_type: ToolType
    domain: ToolDomain
    parameters: list[ToolParameter]
    return_schema: dict[str, Any]
    examples: list[dict[str, Any]] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["tool_type"] = self.tool_type.value
        d["domain"] = self.domain.value
        return d


@dataclass
class SeedConcept:
    id: str
    name: str
    category: SeedCategory
    description: str
    domain: str
    related_tools: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["category"] = self.category.value
        return d


@dataclass
class Exemplar:
    id: str
    family: ExemplarFamily
    template: str
    implied_pattern: list[str]
    complexity: int  # 1-5
    required_tool_types: list[str]
    description: str
    sub_questions: int = 1
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["family"] = self.family.value
        return d


def save_pool(items: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [item.to_dict() if hasattr(item, "to_dict") else item for item in items]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_pool(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
