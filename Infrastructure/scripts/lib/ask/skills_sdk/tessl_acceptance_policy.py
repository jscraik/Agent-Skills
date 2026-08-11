"""Canonical score thresholds for private Tessl evidence lanes.

The acceptance floor admits a candidate to the next SDK gate.  The target is
an improvement objective, not a second hidden admission requirement.
"""

TESSL_ACCEPTANCE_SCORE = 85
TESSL_TARGET_SCORE = 90
TESSL_ACCEPTANCE_SCORE_RATE = TESSL_ACCEPTANCE_SCORE / 100
TESSL_TARGET_SCORE_RATE = TESSL_TARGET_SCORE / 100
