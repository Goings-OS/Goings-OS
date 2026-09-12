# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: NODE 18 TEST RUNNER (core_nodes/node_18_lexis_secretary/test_lexis_secretary.py)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; ENTERPRISE UNITTEST
# ==============================================================================

import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from tests.test_lexis_secretary import (
    TestComplianceScanner,
    TestRegulatoryDocumentGenerator,
    TestHitLEscalationGate,
    TestLexisSecretaryEngine
)

if __name__ == "__main__":
    unittest.main()
