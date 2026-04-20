# logic/test_runner.py

import pandas as pd

from logic.normative_pipeline import NormativeInput, run_normative_calculation


def run_tests(test_cases):

    results = []

    for test in test_cases:

        df = pd.DataFrame(test["rooms"])

        # Defaults ergänzen
        if "Innenliegend" not in df:
            df["Innenliegend"] = False

        df["Überströmt nach"] = ""

        result = run_normative_calculation(
            df,
            NormativeInput(
                ane=test["ANE"],
                level=test.get("level", "FL"),
                system=test["system"],
                wind=test.get("wind", "windschwach"),
                aenv=test.get("Aenv", 200),
                luftdicht=test.get("luftdicht", False),
                shaft_enabled=test.get("shaft", False),
            ),
        )
        errors, warnings = result.errors, result.warnings
        ald = result.ald

        # Bewertung
        passed = True
        reason = ""

        exp = test["expected"]

        if "error" in exp:
            if exp["error"] and not errors:
                passed = False
                reason = "Fehler erwartet, aber keiner erkannt"

        if "ald_required" in exp:
            if exp["ald_required"] and ald.get("anzahl", 0) == 0:
                passed = False
                reason = "ALD erwartet, aber keiner berechnet"

        if "error_contains" in exp:
            expected_text = exp["error_contains"]
            if not any(expected_text in msg for msg in errors):
                passed = False
                reason = f"Erwarteter Fehlertext fehlt: {expected_text}"

        results.append({
            "Test": test["name"],
            "Status": "PASS" if passed else "FAIL",
            "Details": reason,
            "Warnings": len(warnings),
        })

    return results
