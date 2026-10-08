"""Repository loading and compatibility adapter for Week 2 flat fixtures."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def load_repository(root=ROOT):
    # Reuse the offline schema and cross-reference gate before evaluation.
    sys.path.insert(0, str(ROOT / 'scripts'))
    from validate_data import read_json, validate_repository
    errors, _ = validate_repository(root)
    if errors:
        raise ValueError('\n'.join(errors))
    return [read_json(p) for p in sorted((root / 'data/rules').rglob('*.json'))]


def boundary_profile(flat):
    """Map documented flat fields; no unknown value is defaulted to permission."""
    profile = {'pet': {}, 'journey': {}, 'documents': {}, 'events': {}}
    for key, value in flat.items():
        group = ('pet' if key in ('species', 'birth_date', 'microchip_present') else
                 'documents' if key in ('certificate_model', 'certificate_issued_at') else 'journey')
        profile[group][key] = value
    return profile
