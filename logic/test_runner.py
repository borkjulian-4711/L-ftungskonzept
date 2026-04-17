# logic/test_runner.py

import pandas as pd

import logic.din1946_core as core
from logic.validation import validate_din
from logic.ald import calculate_ald_din


def run_tests(test_cases):

    results = []

    for test in test_cases:

        df = pd.DataFrame(test["rooms"])

        # Defaults ergänzen
        if "Innenliegend" not in df:
            df["Innenliegend"] = False

        df["Überströmt nach"] = ""

        # Berechnung
        levels = core.calculate_levels(test["ANE"])
        qv = levels["FL"]

        df = core.distribute_airflows(df, qv)
        df = core.apply_exhaust_values(df)

        q_mech = df["Abluft (m³/h)"].sum()
        q_supply = q_mech  # einfache Annahme für Test

        # Validierung
        errors, warnings = validate_din(
            df,
            qv,
            q_supply,
            test["system"]
        )

        # ALD
        ald = calculate_ald_din(qv, q_supply, "windschwach")

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

        results.append({
            "Test": test["name"],
            "Status": "PASS" if passed else "FAIL",
            "Details": reason
        })

    return results
