# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: NODE 09 CATALYST MARKETING AND SCRIPT ENGINE (node_09_catalyst/__init__.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; BRAND-LEVEL ISOLATION
# ==============================================================================

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

ROOT_DIR = os.environ.get("GOINGS_OS_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Default entity campaign archetypes
ENTITY_CAMPAIGN_DEFAULTS: Dict[str, Dict[str, str]] = {
    "Luxury Affairs Event Center": {
        "focus_vector": "Norfolk Takeover Cruise Waterfront Logistics",
        "visual_style_constraints": "Texz-Architect Gold Metallic Accents, Cinematic Dark Noir, 4K High-Res Shutter, Anamorphic Flare",
        "storyboard_sequence": (
            "Scene 1: Ultra-high-resolution slow-motion tracking shot of an elite, sharp-dressed crowd "
            "boarding a luxury cruise liner at the Norfolk waterfront. Gold metallic lighting accents "
            "reflect flawlessly off the polished hull surfaces. Scene 2: Cut to a high-end hospitality "
            "coordination cockpit displaying real-time regional venue mapping overlays on sleek glass interfaces. "
            "Scene 3: Monolithic graphic typography transitions onto the center screen with crisp contrast reading: "
            "KEEP IT GOINGS. The frequency of regional entertainment dominance."
        ),
        "target_audience": "High-net-worth commercial hospitality, event planners, executive venue patrons"
    },
    "Norfolk Takeover Cruise LLC": {
        "focus_vector": "Maritime Luxury Experience and Ticket Allocation",
        "visual_style_constraints": "Deep Ocean Indigo, Sunset Amber Reflections, Crisp Maritime Typography, Stabilized Drone Flyover",
        "storyboard_sequence": (
            "Scene 1: Sweeping aerial drone shot of the luxury cruise vessel departing the harbor into the golden twilight. "
            "Scene 2: VIP lounge coordination showing synchronized soundstage production and exclusive guest hospitality. "
            "Scene 3: Bold golden lettering announcing statutory booking windows: Secure Your Cabin. Norfolk Takeover Cruise."
        ),
        "target_audience": "Maritime travelers, luxury entertainment seekers, group reservation coordinators"
    },
    "Keep It Goings LLC": {
        "focus_vector": "Faceless AI Architecture and Sovereign Enterprise Systems",
        "visual_style_constraints": "Titanium Slate, Neon Cyan Data Matrix, Ultra-Minimal Glassmorphism, 60fps Macro Optics",
        "storyboard_sequence": (
            "Scene 1: Clean architectural server racks humming silently in a climate-controlled data node. "
            "Scene 2: Micro-animations tracing multi-tenant database transactions in real time across the Goings OS network. "
            "Scene 3: Text overlay: Engineering Sovereign Infrastructure for Modern Conglomerates. Keep It Goings."
        ),
        "target_audience": "Enterprise founders, cloud architecture teams, institutional stakeholders"
    },
    "Tanita Brinkley Enterprises LLC": {
        "focus_vector": "Strategic Tax Shield and Business Credit Optimization",
        "visual_style_constraints": "Emerald Green Trim, Executive Mahogany, Polished Brass Typography, Sharp Studio Portraiture",
        "storyboard_sequence": (
            "Scene 1: Executive desk featuring clean legal documents, financial ledgers, and secure biometric tablets. "
            "Scene 2: Dynamic financial risk score chart rising steadily while reducing debt-to-income overhead. "
            "Scene 3: Final title card: Tanita Talks Business. Build Business Credit. Shield Your Wealth."
        ),
        "target_audience": "Business owners seeking credit tier escalation and tax optimization"
    },
    "Choice Inc": {
        "focus_vector": "501(c)(3) Workforce Development and Community Grants",
        "visual_style_constraints": "Warm Solar Flare, Human-Centric Natural Lighting, Documentary Realism, Crisp White Text",
        "storyboard_sequence": (
            "Scene 1: Community workshops where young leaders receive hands-on technology and trade mentorship. "
            "Scene 2: Transparent grant allocation dashboards demonstrating direct dollar impact across neighborhoods. "
            "Scene 3: Closing graphic: Choice Inc. Empowering Communities Through Dedicated Action."
        ),
        "target_audience": "Philanthropic donors, community partners, grant underwriters"
    },
    "Luxury Decor & Rentals LLC": {
        "focus_vector": "Bespoke Event Staging and Premium Rental Inventories",
        "visual_style_constraints": "Champagne Silk, Crystal Prismatic Bokeh, Velvet Textures, Studio Macro Precision",
        "storyboard_sequence": (
            "Scene 1: Elegant floral installations and crystal chandeliers catching the light inside an expansive ballroom. "
            "Scene 2: Seamless setup team arranging custom furniture arrangements with millimeter precision. "
            "Scene 3: Screen title: Elevate Every Celebration. Luxury Decor and Rentals."
        ),
        "target_audience": "Wedding planners, corporate gala organizers, private venue clients"
    }
}


class CatalystScriptEngine:
    """Node 09 Automated Catalyst and CMO Script Compilation Engine."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or ROOT_DIR
        self.node09_dir = os.path.join(self.base_dir, "core_nodes", "node_09_catalyst_cmo")
        os.makedirs(self.node09_dir, exist_ok=True)

    def pull_script_parameters(
        self,
        campaign_id: Optional[str] = None,
        entity_name: str = "Luxury Affairs Event Center"
    ) -> Dict[str, Any]:
        """Extracts or compiles storyboard parameters and visual constraints for a target entity campaign."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cid = campaign_id or f"CATALYST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Match entity or default
        matched_entity = entity_name
        archetype = None
        for key, val in ENTITY_CAMPAIGN_DEFAULTS.items():
            if key.lower() in entity_name.lower() or entity_name.lower() in key.lower():
                matched_entity = key
                archetype = val
                break

        if not archetype:
            matched_entity = entity_name
            archetype = {
                "focus_vector": f"Automated Campaign Alignment for {entity_name}",
                "visual_style_constraints": "High-Definition Contrast, Brand Color Highlights, Dynamic Camera Motion",
                "storyboard_sequence": f"Scene 1: Brand introduction for {entity_name}. Scene 2: Core value proposition. Scene 3: Call to action.",
                "target_audience": "Target consumer and commercial client base"
            }

        script_payload: Dict[str, Any] = {
            "campaign_id": cid,
            "target_entity": matched_entity,
            "focus_vector": archetype["focus_vector"],
            "visual_style_constraints": archetype["visual_style_constraints"],
            "storyboard_sequence": archetype["storyboard_sequence"],
            "target_audience": archetype["target_audience"],
            "generated_at": timestamp,
            "node_origin": "node_09_catalyst_cmo"
        }

        # Persist copy to node_09_catalyst_cmo staging directory
        staging_file = os.path.join(self.node09_dir, f"{cid}_prompt.json")
        try:
            with open(staging_file, "w", encoding="utf-8") as f:
                json.dump(script_payload, f, indent=2)
        except Exception:
            pass

        return script_payload


def pull_script_parameters(campaign_id: Optional[str] = None, entity_name: str = "Luxury Affairs Event Center") -> Dict[str, Any]:
    """Convenience helper pulling script parameters from Catalyst engine."""
    engine = CatalystScriptEngine()
    return engine.pull_script_parameters(campaign_id=campaign_id, entity_name=entity_name)
