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
            }
        },

        {
            "name": "Fehlerfall Innenliegend",
            "ANE": 80,
            "system": "freie Lüftung",
            "rooms": [
                {"Raum": "Bad", "Typ": "Zuluft", "Kategorie (DIN 1946-6)": "Bad", "Innenliegend": True}
            ],
            "expected": {
                "error": True
            }
        }

    ]
