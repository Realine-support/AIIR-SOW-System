"""Workflows package - Multi-step business processes"""

# OLD workflows commented out (use simplified versions)
# from .workflow_1_pricing import process_transcript_to_pricing
# from .workflow_3_send_archive import send_sow_and_archive

# ACTIVE workflows
from .workflow_1_pricing_simplified import process_transcript_to_pricing_simplified
from .workflow_2_sow_generation import generate_sow_from_approval

__all__ = [
    "process_transcript_to_pricing_simplified",
    "generate_sow_from_approval",
]
