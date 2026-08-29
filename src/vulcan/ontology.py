from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from vulcan.models.environment import EnvironmentSpec

# Design analogy: Palantir Ontology models real-world objects, relationships and actions.
# https://www.palantir.com/docs/foundry/ontology/overview/


class EntityKind(str, Enum):
    CLINIC = "clinic"
    PERSON = "person"
    ROLE = "role"
    ROOM = "room"
    DEVICE = "device"
    SYSTEM = "system"
    DATA = "data"
    WORKFLOW = "workflow"
    ENDPOINT = "endpoint"


class ClinicEntity(BaseModel):
    id: str
    kind: EntityKind
    name: str
    properties: dict[str, object] = Field(default_factory=dict)


class ClinicRelation(BaseModel):
    source: str
    relation: str
    target: str


class ClinicOntology(BaseModel):
    entities: list[ClinicEntity] = Field(default_factory=list)
    relations: list[ClinicRelation] = Field(default_factory=list)


class ClinicOntologyBuilder:
    """Create a minimal machine-readable clinic graph from collected facts only."""

    def build(self, environment: EnvironmentSpec) -> ClinicOntology:
        entities = [ClinicEntity(id="clinic", kind=EntityKind.CLINIC, name=environment.clinic_name)]
        relations: list[ClinicRelation] = []
        seen: set[str] = {"clinic"}

        for fact in environment.facts:
            root = fact.key.split(".", 1)[0]
            if root not in seen:
                kind = EntityKind.SYSTEM if root in {"ehr", "pacs", "network"} else EntityKind.DEVICE
                entities.append(ClinicEntity(id=root, kind=kind, name=root.upper()))
                relations.append(ClinicRelation(source="clinic", relation="contains", target=root))
                seen.add(root)

            entities.append(
                ClinicEntity(
                    id=f"fact:{fact.key}",
                    kind=EntityKind.DATA,
                    name=fact.key,
                    properties={"value": fact.value, "status": fact.status.value, "source": fact.source},
                )
            )
            relations.append(
                ClinicRelation(source=root, relation="has_fact", target=f"fact:{fact.key}")
            )

        return ClinicOntology(entities=entities, relations=relations)
