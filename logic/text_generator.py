def generate_concept_text(ANE, res):

    q_req = round(res["q_required"], 1)
    q_ab = round(res["q_abluft"], 1)
    delta = round(res["delta"], 1)

    n_ald = res["n_ald"]
    n_uld = res["n_uld"]

    # Räume gruppieren
    supply_rooms = res["df"][res["df"]["Typ"] == "Zuluft"]["Raum"].tolist()
    exhaust_rooms = res["df"][res["df"]["Typ"] == "Abluft"]["Raum"].tolist()

    # Luftführung beschreiben
    flow_text = ""
    for (a, b), d in res["uld_edges"].items():
        flow_text += f"Die Luft strömt von {a} nach {b} mit einem Volumenstrom von ca. {d['Volumenstrom']} m³/h über {d['Anzahl']} Überströmöffnungen. "

    # Haupttext
    text = f"""
Für die Nutzungseinheit mit einer Fläche von {ANE} m² wurde ein Lüftungskonzept gemäß DIN 1946-6 erstellt.

Der erforderliche Luftvolumenstrom zum Feuchteschutz beträgt {q_req} m³/h. 
Die vorhandenen Abluftvolumenströme betragen insgesamt {q_ab} m³/h.

"""

    if delta > 0:
        text += f"""
Da der erforderliche Feuchteschutz durch die vorhandenen Abluftvolumenströme nicht vollständig sichergestellt werden kann, 
sind zusätzliche lüftungstechnische Maßnahmen erforderlich.

Zur Sicherstellung des Luftwechsels werden {n_ald} Außenluftdurchlässe (ALD) in den Zulufträumen vorgesehen.
"""
    else:
        text += """
Der Feuchteschutz ist durch die vorhandenen Luftvolumenströme gewährleistet. Zusätzliche Maßnahmen sind nicht erforderlich.
"""

    text += f"""
Die Luftführung erfolgt von den Zulufträumen ({", ".join(supply_rooms)}) 
über Überströmbereiche in die Ablufträume ({", ".join(exhaust_rooms)}).

{flow_text}

Insgesamt werden {n_uld} Überströmöffnungen (ÜLD) zur Sicherstellung der Luftüberströmung vorgesehen.

Innenliegende Ablufträume werden gemäß DIN 18017-3 mechanisch entlüftet.
"""

    return text
