def generate_formblatt_e(res):

    levels = res["levels"]
    d = res["formblatt_d"]

    text = f"""
Es wurde ein Lüftungskonzept gemäß DIN 1946-6 erstellt.

Die Prüfung gemäß Formblatt A hat ergeben, dass ein Lüftungskonzept erforderlich ist.

Die Berechnung der Lüftungsstufen nach Formblatt C ergibt:
- Feuchteschutzlüftung: {levels['FL']} m³/h
- Nennlüftung: {levels['NL']} m³/h

Auf Grundlage der Bewertung gemäß Formblatt D wird folgende Maßnahme festgelegt:

{d['massnahme'].upper()}

Begründung:
{d['begruendung']}

Damit ist die lüftungstechnische Maßnahme für die Nutzungseinheit festgelegt.
"""

    return text
