def evaluate_formblatt_d(formblatt_a, formblatt_b, formblatt_c):

    erforderlich = formblatt_a["erforderlich"]
    fenster = formblatt_b["fensterlueftung"]

    fl = formblatt_c["FL"]
    nl = formblatt_c["NL"]

    massnahme = "keine"
    begruendung = []

    if not erforderlich:
        return {
            "massnahme": "keine",
            "begruendung": "Kein Lüftungskonzept erforderlich"
        }

    # Keine Fensterlüftung möglich
    if not fenster:
        return {
            "massnahme": "ventilatorgestützt",
            "begruendung": "Fensterlüftung nicht möglich"
        }

    # Feuchteschutz nicht erfüllt
    if fl["status"] == "nicht erfüllt":
        massnahme = "ALD"
        begruendung.append("Feuchteschutzlüftung nicht erfüllt")

    # Nennlüftung nicht erfüllt
    if nl["status"] == "nicht erfüllt":
        massnahme = "ventilatorgestützt"
        begruendung.append("Nennlüftung nicht erfüllt")

    if not begruendung:
        begruendung.append("Lüftung über Fenster möglich")

    return {
        "massnahme": massnahme,
        "begruendung": ", ".join(begruendung)
    }
