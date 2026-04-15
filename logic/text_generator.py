def generate_concept_text(ANE, res, mode="lang", meta=None):

    q_req = round(res["q_required"], 1)
    q_ab = round(res["q_abluft"], 1)
    delta = round(res["delta"], 1)

    n_ald = res["n_ald"]
    n_uld = res["n_uld"]

def clean_list(values):
    return [str(v) for v in values if v and str(v) != "nan"]


supply = clean_list(
    res["df"][res["df"]["Typ"] == "Zuluft"]["Raum"].tolist()
)

exhaust = clean_list(
    res["df"][res["df"]["Typ"] == "Abluft"]["Raum"].tolist()
)

    flow_text = ""
    for (a, b), d in res["uld_edges"].items():
        flow_text += f"{a} → {b}: {d['Volumenstrom']} m³/h über {d['Anzahl']} ÜLD. "

    base = f"Nutzungseinheit mit {ANE} m². "

    if mode == "kurz":
        return f"""{base}
Feuchteschutz: {q_req} m³/h, Abluft: {q_ab} m³/h.
ALD: {n_ald}, ÜLD: {n_uld}.
Innenliegende Räume gemäß DIN 18017-3.
"""

    if mode == "behoerde":
        return f"""
Gemäß DIN 1946-6 wurde für die Nutzungseinheit ({ANE} m²) ein Lüftungskonzept erstellt.

Erforderlicher Volumenstrom (Feuchteschutz): {q_req} m³/h.
Vorhandene Abluft: {q_ab} m³/h.

{'Maßnahmen erforderlich.' if delta>0 else 'Feuchteschutz erfüllt.'}

Zuluft: {", ".join(supply)} → Abluft: {", ".join(exhaust)}.

{flow_text}

Überströmöffnungen: {n_uld}.
"""

    return f"""
Für die Nutzungseinheit mit {ANE} m² wurde ein Lüftungskonzept gemäß DIN 1946-6 erstellt.

Feuchteschutz: {q_req} m³/h
Abluft: {q_ab} m³/h

{'Zusätzliche Maßnahmen erforderlich.' if delta>0 else 'Feuchteschutz sichergestellt.'}

Zuluft erfolgt über: {", ".join(supply)}.
Abluft erfolgt über: {", ".join(exhaust)}.

{flow_text}
flow_text = ""
for (a, b), d in res["uld_edges"].items():

    a = str(a)
    b = str(b)

    flow_text += (
        f"{a} → {b}: "
        f"{d['Volumenstrom']} m³/h über {d['Anzahl']} ÜLD. "
    )
Es werden {n_ald} ALD und {n_uld} ÜLD vorgesehen.

Innenliegende Räume gemäß DIN 18017-3.
"""
