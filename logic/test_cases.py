# logic/test_cases.py

def get_test_cases():

    return [

        {
            "name": "Beispiel 5.1",
            "ANE": 80,
            "system": "ventilatorgestützt",
            "rooms": [
                {"Raum": "Küche", "Typ": "Abluft", "Kategorie (DIN 1946-6)": "Küche"},
                {"Raum": "Bad", "Typ": "Abluft", "Kategorie (DIN 1946-6)": "Bad"},
            ],
            "expected": {
                "min_q": 130,
                "type": "mechanisch"
            }
        },

        {
            "name": "Beispiel 6.8",
            "ANE": 70,
            "system": "kombiniert",
            "rooms": [
                {"Raum": "Bad", "Typ": "Abluft", "Kategorie (DIN 1946-6)": "Bad"}
            ],
            "expected": {
                "ald_required": True
            },
            "Aenv": 40
        },

        {
            "name": "Fehlerfall Innenliegend",
            "ANE": 80,
            "system": "freie Lüftung",
            "rooms": [
                {"Raum": "Bad", "Typ": "Zuluft", "Kategorie (DIN 1946-6)": "Bad", "Innenliegend": True}
            ],
            "expected": {
                "error": True,
                "error_contains": "muss Abluft sein"
            }
        },

        {
            "name": "Fehlerfall DIN18017 Kategorie fehlt",
            "ANE": 75,
            "system": "freie Lüftung",
            "rooms": [
                {"Raum": "Bad innen", "Typ": "Abluft", "Kategorie (DIN 1946-6)": "Bad", "Innenliegend": True}
            ],
            "expected": {
                "error": True,
                "error_contains": "benötigt eine DIN 18017 Kategorie"
            }
        },

        {
            "name": "Auto-Fix ändert Volumenströme",
            "ANE": 85,
            "system": "ventilatorgestützt",
            "rooms": [
                {
                    "Raum": "Bad innen",
                    "Typ": "Zuluft",
                    "Kategorie (DIN 1946-6)": "Bad",
                    "Innenliegend": True,
                    "DIN 18017 Kategorie": ""
                },
                {
                    "Raum": "Wohnzimmer",
                    "Typ": "Zuluft",
                    "Kategorie (DIN 1946-6)": "Wohnzimmer",
                    "Innenliegend": False
                }
            ],
            "expected": {
                "auto_fix_changes_flows": True
            }
        }

    ]
