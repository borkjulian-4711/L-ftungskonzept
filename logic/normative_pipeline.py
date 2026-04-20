from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd

import logic.din1946_core as core
from logic.ald import calculate_ald_din
from logic.din18017 import get_din18017_flow
from logic.infiltration import (
    calculate_infiltration_din,
    calculate_shaft_flow,
    get_ez_din,
)
from logic.system_logic import evaluate_system
from logic.validation import validate_din


REQUIRED_COLUMNS = [
    "Raum",
    "Fläche",
    "Typ",
    "Kategorie (DIN 1946-6)",
    "Innenliegend",
    "DIN 18017 Kategorie",
    "Überströmt nach",
]


@dataclass
class NormativeInput:
    ane: float
    level: str
    system: str
    wind: str
    aenv: float
    luftdicht: bool
    shaft_enabled: bool
    gebaeudetyp: str = "EFH"


@dataclass
class NormativeResult:
    rooms: pd.DataFrame
    levels: dict
    qv_required: float
    q_mech: float
    q_supply: float
    q_inf: float
    q_shaft: float
    system_result: dict
    ald: dict
    errors: List[str]
    warnings: List[str]
    audit_trail: List[str]


def _prepare_rooms(df_rooms: pd.DataFrame) -> pd.DataFrame:
    df = df_rooms.copy()

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            if column in ["Innenliegend"]:
                df[column] = False
            else:
                df[column] = ""

    df = df[REQUIRED_COLUMNS].fillna("")
    df["Innenliegend"] = df["Innenliegend"].astype(bool)

    return df


def _apply_normative_exhaust(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    work = df.copy()
    audit_trail = []

    din1946_min = {
        "Küche": 60,
        "Bad": 40,
        "WC": 30,
        "Hauswirtschaftsraum": 30,
        "Abstellraum": 30,
    }

    work["Abluft (m³/h)"] = 0

    for idx, row in work.iterrows():
        if row["Typ"] != "Abluft":
            continue

        room_name = str(row.get("Raum", f"Raum {idx + 1}"))
        din1946_flow = din1946_min.get(row["Kategorie (DIN 1946-6)"], 30)
        din18017_flow = 0

        if row.get("Innenliegend", False):
            din18017_category = str(row.get("DIN 18017 Kategorie", "")).split(" ")[0]
            din18017_flow = get_din18017_flow(din18017_category)

        final_flow = max(din1946_flow, din18017_flow)
        work.loc[idx, "Abluft (m³/h)"] = final_flow

        audit_trail.append(
            (
                f"{room_name}: Abluft auf {final_flow} m³/h gesetzt "
                f"(DIN1946={din1946_flow}, DIN18017={din18017_flow})."
            )
        )

    return work, audit_trail


def run_normative_calculation(df_rooms: pd.DataFrame, params: NormativeInput) -> NormativeResult:
    audit_trail = ["Normativer Rechenlauf initialisiert."]

    rooms = _prepare_rooms(df_rooms)
    levels = core.calculate_levels(params.ane)
    qv_required = levels[params.level]
    audit_trail.append(f"Lüftungsstufe {params.level}: qv_required={qv_required} m³/h.")

    rooms = core.distribute_airflows(rooms, qv_required)
    rooms, exhaust_audit = _apply_normative_exhaust(rooms)
    audit_trail.extend(exhaust_audit)

    ez = get_ez_din(params.gebaeudetyp, params.wind, params.luftdicht)
    q_inf = calculate_infiltration_din(params.aenv, ez)
    q_shaft = calculate_shaft_flow() if params.shaft_enabled else 0
    q_mech = rooms["Abluft (m³/h)"].sum()

    if params.system == "freie Lüftung":
        q_supply = q_inf + q_shaft
        audit_trail.append(
            f"Freie Lüftung: q_supply=q_inf+q_shaft={q_supply} m³/h."
        )
    elif params.system == "ventilatorgestützt":
        rooms, q_supply, _ = core.dimension_ventilation_system(rooms, qv_required)
        q_mech = rooms["Abluft (m³/h)"].sum()
        audit_trail.append(
            f"Ventilatorgestützt: Zu/Abluft auf {q_supply} m³/h dimensioniert."
        )
    else:
        q_supply = q_mech + q_inf + q_shaft
        audit_trail.append(
            f"Kombiniert: q_supply=q_mech+q_inf+q_shaft={q_supply} m³/h."
        )

    errors, warnings = validate_din(rooms, qv_required, q_supply, params.system)
    system_result = evaluate_system(q_mech, qv_required, q_supply)
    ald = calculate_ald_din(qv_required, q_supply, params.wind)

    audit_trail.append(
        f"Validierung abgeschlossen: {len(errors)} Fehler, {len(warnings)} Warnungen."
    )

    return NormativeResult(
        rooms=rooms,
        levels=levels,
        qv_required=qv_required,
        q_mech=q_mech,
        q_supply=q_supply,
        q_inf=q_inf,
        q_shaft=q_shaft,
        system_result=system_result,
        ald=ald,
        errors=errors,
        warnings=warnings,
        audit_trail=audit_trail,
    )
