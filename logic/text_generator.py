def generate_concept_text(ANE, res, mode="lang"):

    q_req = round(res["q_required"], 1)
    q_ab = round(res["q_abluft"], 1)
    delta = round(res["delta"], 1)

    n_ald = res["n_ald"]
    n_uld = res["n_uld"]

    supply_rooms = res["df"][res["df"]["Typ"] == "Zuluft"]["Raum"].tolist()
    exhaust_rooms = res["df"][res["df"]["Typ"] == "Abluft"]["Raum"].tolist()

    # -----------------------------
    # Luftführungstext
    # -----------------------------
    flow_text = ""
    for (a, b), d in res["uld_edges"].items():
        flow_text += (
            f"Die Luft strömt von {a} nach {b} "
            f"mit einem Volumenstrom von ca. {d['Volumenstrom']} m³/h "
            f"über {d['Anzahl']} Überströmöffnungen. "
        )

    # =============================
    # KURZTEXT
    # =============================
    if mode == "kurz":

        text = f"""
Lüftungskonzept gemäß DIN 1946-6 für eine Nutzungseinheit mit {ANE} m².

Feuchteschutz: {q_req} m³/h, vorhandene Abluft: {q_ab} m³/h.
"""

        if delta > 0:
            text += f"Zusätzliche Maßnahmen erforderlich. Es werden {n_ald} ALD vorgesehen.\n"
        else:
            text += "Feuchteschutz ist sichergestellt.\n"

        text += f"""
Luftführung von {", ".join(supply_rooms)} zu {", ".join(exhaust_rooms)}.
Es sind {n_uld} Überströmöffnungen erforderlich.

Innenliegende Räume werden gemäß DIN 18017-3 entlüftet.
"""

        return text.strip()

    # =============================
    # BEHÖRDENTEXT
    # =============================
    if mode == "behoerde":

        text = f"""
Für die Nutzungseinheit mit einer Fläche von {ANE} m² wurde ein Lüftungskonzept gemäß DIN 1946-6 erstellt.

Der zum Feuchteschutz erforderliche Luftvolumenstrom gemäß DIN 1946-6 beträgt {q_req} m³/h.
Die vorhandenen Abluftvolumenströme betragen {q_ab} m³/h.
"""

        if delta > 0:
            text += f"""
Der notwendige Luftvolumenstrom wird nicht vollständig erreicht. 
Gemäß DIN 1946-6 sind daher lüftungstechnische Maßnahmen erforderlich.

Zur Sicherstellung des Feuchteschutzes werden {n_ald} Außenluftdurchlässe vorgesehen.
"""
        else:
            text += """
Der Feuchteschutz gemäß DIN 1946-6 ist ohne zusätzliche Maßnahmen gewährleistet.
"""

        text += f"""
Die Luftführung erfolgt normgerecht von Zulufträumen ({", ".join(supply_rooms)}) 
in Richtung der Ablufträume ({", ".join(exhaust_rooms)}).

{flow_text}

Die Überströmung erfolgt über insgesamt {n_uld} Überströmöffnungen.

Innenliegende Räume werden gemäß DIN 18017-3 mechanisch entlüftet.
"""

        return text.strip()

    # =============================
    # LANGTEXT (STANDARD)
    # =============================
    text = f"""
Für die Nutzungseinheit mit einer Fläche von {ANE} m² wurde ein Lüftungskonzept gemäß DIN 1946-6 erstellt.

Der erforderliche Luftvolumenstrom zum Feuchteschutz beträgt {q_req} m³/h.
Die vorhandenen Abluftvolumenströme betragen insgesamt {q_ab} m³/h.
"""

    if delta > 0:
        text += f"""
Da der erforderliche Feuchteschutz gemäß DIN 1946-6 nicht vollständig sichergestellt werden kann,
sind zusätzliche lüftungstechnische Maßnahmen erforderlich.

Zur Sicherstellung des Mindestluftwechsels werden {n_ald} Außenluftdurchlässe (ALD) vorgesehen.
"""
    else:
        text += """
Der Feuchteschutz gemäß DIN 1946-6 ist gewährleistet, zusätzliche Maßnahmen sind nicht erforderlich.
"""

    text += f"""
Die Luftführung erfolgt von den Zulufträumen ({", ".join(supply_rooms)}) 
über Überströmbereiche in die Ablufträume ({", ".join(exhaust_rooms)}).

{flow_text}

Zur Sicherstellung der Luftüberströmung werden insgesamt {n_uld} Überströmöffnungen vorgesehen.

Innenliegende Räume werden gemäß DIN 18017-3 mechanisch entlüftet.
"""

    return text.strip()
