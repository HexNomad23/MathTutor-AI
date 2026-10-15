"""English display names for stable storage identifiers and legacy statuses."""

SUBJECT_NAMES = {
    "algebra": "Algebra",
    "geometria": "Geometry",
    "fisica": "Physics",
    "calculo": "Calculus",
}

LEGACY_STATUS_NAMES = {
    "Verificado": "Verified",
    "Comprobación numérica": "Numerical check",
    "No se pudo verificar": "Could not verify",
    "Fuera del alcance": "Out of scope",
}


def subject_name(value: str) -> str:
    return SUBJECT_NAMES.get(value, value.replace("_", " ").title())


def verification_name(value: str) -> str:
    return LEGACY_STATUS_NAMES.get(value, value)
