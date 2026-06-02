"""
Social dynamics system for The Cognisphere.

Handles alliances, factions, institutions, betrayals, and social relationships
that drive emergent civilization behavior.
"""

import random
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class AllianceType(Enum):
    """Types of alliances between agents."""

    TRADE = "trade"
    DEFENSE = "defense"
    KNOWLEDGE = "knowledge"
    POLITICAL = "political"
    CULTURAL = "cultural"


class FactionType(Enum):
    """Types of factions in the simulation."""

    ECONOMIC = "economic"
    CULTURAL = "cultural"
    POLITICAL = "political"
    TECHNOLOGICAL = "technological"
    RELIGIOUS = "religious"


class InstitutionType(Enum):
    """Types of institutions in the simulation."""

    COUNCIL = "council"
    TEMPLE = "temple"
    GUILD = "guild"
    ACADEMY = "academy"
    COURT = "court"


@dataclass
class Alliance:
    """Represents an alliance between agents."""

    alliance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    members: Set[str] = field(default_factory=set)
    alliance_type: AllianceType = AllianceType.TRADE
    strength: float = 1.0  # 0.0 to 1.0
    created_at: datetime = field(default_factory=datetime.now)
    last_interaction: datetime = field(default_factory=datetime.now)
    shared_resources: Dict[str, Dict[str, float]] = field(default_factory=dict)
    mutual_benefits: Dict[str, float] = field(default_factory=dict)
    trust_levels: Dict[Tuple[str, str], float] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def add_member(self, agent_id: str) -> None:
        """Add a member to the alliance."""
        self.members.add(agent_id)
        if agent_id not in self.shared_resources:
            self.shared_resources[agent_id] = {}
        if agent_id not in self.mutual_benefits:
            self.mutual_benefits[agent_id] = 0.0

        # Initialize trust levels with new member
        for existing_member in self.members:
            if existing_member != agent_id:
                self.trust_levels[(agent_id, existing_member)] = 0.5
                self.trust_levels[(existing_member, agent_id)] = 0.5

    def remove_member(self, agent_id: str) -> None:
        """Remove a member from the alliance."""
        self.members.discard(agent_id)
        self.shared_resources.pop(agent_id, None)
        self.mutual_benefits.pop(agent_id, None)

        # Remove trust relationships
        keys_to_remove = [key for key in self.trust_levels.keys() if agent_id in key]
        for key in keys_to_remove:
            del self.trust_levels[key]

    def update_strength(self, interaction_success: bool, interaction_type: str = "general") -> None:
        """Update alliance strength based on interactions."""
        if interaction_success:
            self.strength = min(1.0, self.strength + 0.02)
        else:
            self.strength = max(0.0, self.strength - 0.05)

        self.last_interaction = datetime.now()

        # Record interaction in history
        self.history.append(
            {
                "timestamp": datetime.now(),
                "type": interaction_type,
                "success": interaction_success,
                "strength_after": self.strength,
            }
        )

    def update_trust(self, agent_a: str, agent_b: str, trust_change: float) -> None:
        """Update trust level between two alliance members."""
        key = (agent_a, agent_b)
        if key in self.trust_levels:
            self.trust_levels[key] = max(0.0, min(1.0, self.trust_levels[key] + trust_change))

    def get_member_benefit(self, agent_id: str) -> float:
        """Get the benefit an agent receives from this alliance."""
        return self.mutual_benefits.get(agent_id, 0.0)

    def calculate_cohesion(self) -> float:
        """Calculate alliance cohesion based on trust levels."""
        if len(self.members) < 2:
            return 0.0

        total_trust = 0.0
        trust_pairs = 0

        for (member_a, member_b), trust in self.trust_levels.items():
            if member_a in self.members and member_b in self.members:
                total_trust += trust
                trust_pairs += 1

        return total_trust / trust_pairs if trust_pairs > 0 else 0.0


@dataclass
class Betrayal:
    """Represents a betrayal event between agents."""

    betrayal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    betrayer_id: str = ""
    betrayed_id: str = ""
    alliance_id: Optional[str] = None
    reason: str = ""
    severity: float = 0.5  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    consequences: Dict[str, Any] = field(default_factory=dict)

    def calculate_reputation_impact(self) -> Dict[str, float]:
        """Calculate reputation impact of this betrayal."""
        impact = {
            self.betrayer_id: -self.severity * 0.5,  # Betrayer loses reputation
            self.betrayed_id: self.severity * 0.2,  # Betrayed gains sympathy
        }
        return impact


@dataclass
class Faction:
    """Represents a faction of agents with shared interests."""

    faction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    faction_type: FactionType = FactionType.ECONOMIC
    members: Set[str] = field(default_factory=set)
    leader_id: Optional[str] = None
    ideology: Dict[str, float] = field(default_factory=dict)  # Ideology vector
    resources: Dict[str, float] = field(default_factory=dict)
    influence: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    internal_conflicts: List[Dict[str, Any]] = field(default_factory=list)
    achievements: List[Dict[str, Any]] = field(default_factory=list)

    def add_member(self, agent_id: str) -> None:
        """Add a member to the faction."""
        self.members.add(agent_id)
        self.last_activity = datetime.now()

        # If no leader, make the first member the leader
        if self.leader_id is None:
            self.leader_id = agent_id

    def remove_member(self, agent_id: str) -> None:
        """Remove a member from the faction."""
        self.members.discard(agent_id)
        if self.leader_id == agent_id:
            self.elect_new_leader()
        self.last_activity = datetime.now()

    def elect_new_leader(self) -> Optional[str]:
        """Elect a new leader from remaining members."""
        if not self.members:
            self.leader_id = None
            return None

        # Simple election based on influence and random factors
        candidates = list(self.members)
        self.leader_id = random.choice(candidates)
        return self.leader_id

    def add_achievement(self, achievement_type: str, description: str, impact: float) -> None:
        """Add an achievement to the faction."""
        self.achievements.append(
            {
                "id": str(uuid.uuid4()),
                "type": achievement_type,
                "description": description,
                "impact": impact,
                "timestamp": datetime.now(),
            }
        )

        # Increase faction influence based on achievement
        self.influence += impact * 0.1

    def add_internal_conflict(self, conflict_type: str, description: str, severity: float) -> None:
        """Add an internal conflict to the faction."""
        self.internal_conflicts.append(
            {
                "id": str(uuid.uuid4()),
                "type": conflict_type,
                "description": description,
                "severity": severity,
                "timestamp": datetime.now(),
            }
        )

        # Decrease faction influence based on conflict
        self.influence = max(0.0, self.influence - severity * 0.05)

    def calculate_stability(self) -> float:
        """Calculate faction stability based on conflicts and achievements."""
        if not self.achievements and not self.internal_conflicts:
            return 0.5  # Neutral stability

        total_achievements = sum(ach["impact"] for ach in self.achievements)
        total_conflicts = sum(conf["severity"] for conf in self.internal_conflicts)

        if total_achievements + total_conflicts == 0:
            return 0.5

        stability = total_achievements / (total_achievements + total_conflicts)
        return max(0.0, min(1.0, stability))


@dataclass
class Institution:
    """Represents an institution in the simulation."""

    institution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    institution_type: InstitutionType = InstitutionType.COUNCIL
    members: Set[str] = field(default_factory=set)
    leader_id: Optional[str] = None
    purpose: str = ""
    authority: float = 0.5  # 0.0 to 1.0
    resources: Dict[str, float] = field(default_factory=dict)
    policies: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_meeting: datetime = field(default_factory=datetime.now)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    legitimacy: float = 0.5  # 0.0 to 1.0

    def add_member(self, agent_id: str) -> None:
        """Add a member to the institution."""
        self.members.add(agent_id)
        self.last_meeting = datetime.now()

        # If no leader, make the first member the leader
        if self.leader_id is None:
            self.leader_id = agent_id

    def remove_member(self, agent_id: str) -> None:
        """Remove a member from the institution."""
        self.members.discard(agent_id)
        if self.leader_id == agent_id:
            self.leader_id = None

    def make_decision(
        self, decision: str, proposer_id: str, agent_preferences: Dict[str, float]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Make a decision through institutional process."""
        if not self.members:
            return False, {"error": "No members in institution"}

        # Calculate votes based on member preferences and influence
        votes_for = 0.0
        votes_against = 0.0
        total_influence = 0.0

        for member_id in self.members:
            # Get member's preference for this decision
            preference = agent_preferences.get(member_id, 0.5)

            # Weight by authority and legitimacy
            influence_weight = self.authority * self.legitimacy

            if preference > 0.5:
                votes_for += preference * influence_weight
            else:
                votes_against += (1.0 - preference) * influence_weight

            total_influence += influence_weight

        decision_made = votes_for > votes_against
        decision_details = {
            "votes_for": votes_for,
            "votes_against": votes_against,
            "total_influence": total_influence,
            "proposer": proposer_id,
            "timestamp": datetime.now(),
        }

        if decision_made:
            self.last_meeting = datetime.now()
            self.decisions.append(
                {"decision": decision, "details": decision_details, "timestamp": datetime.now()}
            )

            # Increase legitimacy for successful decisions
            self.legitimacy = min(1.0, self.legitimacy + 0.05)
        else:
            # Decrease legitimacy for failed decisions
            self.legitimacy = max(0.0, self.legitimacy - 0.02)

        return decision_made, decision_details


class SocialEngine:
    """Main social engine that manages all social dynamics."""

    def __init__(self):
        self.alliances: Dict[str, Alliance] = {}
        self.betrayals: List[Betrayal] = []
        self.factions: Dict[str, Faction] = {}
        self.institutions: Dict[str, Institution] = {}
        self.agent_reputations: Dict[str, float] = {}
        self.social_network: Dict[str, Set[str]] = defaultdict(set)
        self.relationship_strengths: Dict[Tuple[str, str], float] = {}

    def create_alliance(
        self, member_ids: List[str], alliance_type: AllianceType = AllianceType.TRADE
    ) -> Alliance:
        """Create a new alliance between agents."""
        alliance = Alliance(alliance_type=alliance_type)
        for agent_id in member_ids:
            alliance.add_member(agent_id)
            self.social_network[agent_id].update(member_ids)
            self.social_network[agent_id].discard(agent_id)  # Remove self

        self.alliances[alliance.alliance_id] = alliance
        return alliance

    def create_faction(
        self, name: str, faction_type: FactionType, founder_id: str, ideology: Dict[str, float]
    ) -> Faction:
        """Create a new faction."""
        faction = Faction(
            name=name, faction_type=faction_type, leader_id=founder_id, ideology=ideology
        )
        faction.add_member(founder_id)
        self.factions[faction.faction_id] = faction
        return faction

    def create_institution(
        self, name: str, institution_type: InstitutionType, founder_id: str, purpose: str
    ) -> Institution:
        """Create a new institution."""
        institution = Institution(
            name=name, institution_type=institution_type, leader_id=founder_id, purpose=purpose
        )
        institution.add_member(founder_id)
        self.institutions[institution.institution_id] = institution
        return institution

    def execute_betrayal(
        self,
        betrayer_id: str,
        betrayed_id: str,
        alliance_id: Optional[str] = None,
        reason: str = "",
        severity: float = 0.5,
    ) -> Betrayal:
        """Execute a betrayal between agents."""
        betrayal = Betrayal(
            betrayer_id=betrayer_id,
            betrayed_id=betrayed_id,
            alliance_id=alliance_id,
            reason=reason,
            severity=severity,
        )

        self.betrayals.append(betrayal)

        # Update reputations
        reputation_impact = betrayal.calculate_reputation_impact()
        for agent_id, impact in reputation_impact.items():
            self.agent_reputations[agent_id] = max(
                0.0, self.agent_reputations.get(agent_id, 0.5) + impact
            )

        # Update alliance if applicable
        if alliance_id and alliance_id in self.alliances:
            alliance = self.alliances[alliance_id]
            alliance.remove_member(betrayer_id)
            alliance.update_strength(False)

        # Update relationship strength
        relationship_key = (betrayer_id, betrayed_id)
        self.relationship_strengths[relationship_key] = max(
            0.0, self.relationship_strengths.get(relationship_key, 0.5) - severity
        )

        return betrayal

    def form_alliance(
        self, agent_a: str, agent_b: str, alliance_type: AllianceType = AllianceType.TRADE
    ) -> Optional[Alliance]:
        """Form an alliance between two agents."""
        # Check if agents can form alliance (not already enemies, etc.)
        relationship_key = (agent_a, agent_b)
        relationship_strength = self.relationship_strengths.get(relationship_key, 0.5)

        if relationship_strength < 0.3:  # Too hostile to form alliance
            return None

        alliance = self.create_alliance([agent_a, agent_b], alliance_type)

        # Increase relationship strength
        self.relationship_strengths[relationship_key] = min(1.0, relationship_strength + 0.2)

        return alliance

    def join_faction(self, agent_id: str, faction_id: str) -> bool:
        """Have an agent join a faction."""
        if faction_id not in self.factions:
            return False

        faction = self.factions[faction_id]

        # Check if agent is compatible with faction ideology
        # This is simplified - in reality would check agent's ideology vector

        faction.add_member(agent_id)
        return True

    def join_institution(self, agent_id: str, institution_id: str) -> bool:
        """Have an agent join an institution."""
        if institution_id not in self.institutions:
            return False

        institution = self.institutions[institution_id]
        institution.add_member(agent_id)
        return True

    def process_social_interactions(self, agents: List[Any]) -> Dict[str, Any]:
        """Process social interactions for the current tick."""
        interactions = {
            "alliances_formed": 0,
            "betrayals_executed": 0,
            "factions_created": 0,
            "institutions_created": 0,
            "social_conflicts": 0,
        }

        # Random social interactions
        for _ in range(random.randint(1, 5)):
            interaction_type = random.choice(
                ["form_alliance", "betrayal", "join_faction", "join_institution", "social_conflict"]
            )

            if interaction_type == "form_alliance" and len(agents) >= 2:
                agent_a, agent_b = random.sample(agents, 2)
                if self.form_alliance(agent_a.agent_id, agent_b.agent_id):
                    interactions["alliances_formed"] += 1

            elif interaction_type == "betrayal" and len(agents) >= 2:
                agent_a, agent_b = random.sample(agents, 2)
                if random.random() < 0.1:  # 10% chance of betrayal
                    self.execute_betrayal(
                        agent_a.agent_id,
                        agent_b.agent_id,
                        reason="Opportunistic betrayal",
                        severity=random.uniform(0.3, 0.8),
                    )
                    interactions["betrayals_executed"] += 1

            elif interaction_type == "join_faction" and self.factions:
                agent = random.choice(agents)
                faction_id = random.choice(list(self.factions.keys()))
                if self.join_faction(agent.agent_id, faction_id):
                    interactions["social_conflicts"] += 1

        return interactions

    def update_social_state(self) -> None:
        """Update the social state for the current tick."""
        # Update alliance strengths based on time
        for alliance in self.alliances.values():
            if datetime.now() - alliance.last_interaction > timedelta(hours=24):
                alliance.update_strength(False)  # Decay if no recent activity

        # Clean up weak alliances
        weak_alliances = [
            alliance_id
            for alliance_id, alliance in self.alliances.items()
            if alliance.strength < 0.1 or len(alliance.members) < 2
        ]
        for alliance_id in weak_alliances:
            del self.alliances[alliance_id]

        # Update faction stability
        for faction in self.factions.values():
            stability = faction.calculate_stability()
            if stability < 0.2 and len(faction.members) > 1:
                # Faction might split or dissolve
                if random.random() < 0.1:  # 10% chance
                    # Remove some members
                    members_to_remove = random.sample(
                        list(faction.members), random.randint(1, len(faction.members) // 2)
                    )
                    for member_id in members_to_remove:
                        faction.remove_member(member_id)

    def get_agent_social_status(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive social status for an agent."""
        status: Dict[str, Any] = {
            "reputation": self.agent_reputations.get(agent_id, 0.5),
            "alliances": [],
            "factions": [],
            "institutions": [],
            "betrayals": [],
            "relationships": {},
        }

        # Check alliance membership
        for alliance in self.alliances.values():
            if agent_id in alliance.members:
                status["alliances"].append(
                    {
                        "alliance_id": alliance.alliance_id,
                        "type": alliance.alliance_type.value,
                        "strength": alliance.strength,
                        "cohesion": alliance.calculate_cohesion(),
                        "benefit": alliance.get_member_benefit(agent_id),
                    }
                )

        # Check faction membership
        for faction in self.factions.values():
            if agent_id in faction.members:
                status["factions"].append(
                    {
                        "faction_id": faction.faction_id,
                        "name": faction.name,
                        "type": faction.faction_type.value,
                        "is_leader": faction.leader_id == agent_id,
                        "stability": faction.calculate_stability(),
                        "influence": faction.influence,
                    }
                )

        # Check institution membership
        for institution in self.institutions.values():
            if agent_id in institution.members:
                status["institutions"].append(
                    {
                        "institution_id": institution.institution_id,
                        "name": institution.name,
                        "type": institution.institution_type.value,
                        "is_leader": institution.leader_id == agent_id,
                        "authority": institution.authority,
                        "legitimacy": institution.legitimacy,
                    }
                )

        # Check betrayals
        for betrayal in self.betrayals:
            if agent_id in [betrayal.betrayer_id, betrayal.betrayed_id]:
                status["betrayals"].append(
                    {
                        "betrayal_id": betrayal.betrayal_id,
                        "role": "betrayer" if agent_id == betrayal.betrayer_id else "betrayed",
                        "severity": betrayal.severity,
                        "reason": betrayal.reason,
                        "timestamp": betrayal.timestamp,
                    }
                )

        # Get relationship strengths
        for (agent_a, agent_b), strength in self.relationship_strengths.items():
            if agent_a == agent_id:
                status["relationships"][agent_b] = strength
            elif agent_b == agent_id:
                status["relationships"][agent_a] = strength

        return status

    def get_social_summary(self) -> Dict[str, Any]:
        """Get summary of social state."""
        return {
            "total_alliances": len(self.alliances),
            "total_factions": len(self.factions),
            "total_institutions": len(self.institutions),
            "total_betrayals": len(self.betrayals),
            "average_reputation": sum(self.agent_reputations.values()) / len(self.agent_reputations)
            if self.agent_reputations
            else 0.0,
            "active_alliances": len([a for a in self.alliances.values() if a.strength > 0.5]),
            "stable_factions": len(
                [f for f in self.factions.values() if f.calculate_stability() > 0.6]
            ),
            "legitimate_institutions": len(
                [i for i in self.institutions.values() if i.legitimacy > 0.5]
            ),
        }
