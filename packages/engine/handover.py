"""Anonymous final pickup and overnight-care diagnostics, no custody confirmation."""
from packages.engine.outbound import instant

FIELDS = {'arrival_time', 'arrival_timezone', 'pickup_deadline', 'pickup_timezone',
          'overnight_required', 'overnight_care_available', 'overnight_custodian_role'}
ROLES = ('owner', 'authorized_person', 'carrier', 'receiving_carer')


def assess(record):
    if not isinstance(record, dict) or set(record) - FIELDS:
        raise ValueError('unknown final handover control')
    for field in ('overnight_required', 'overnight_care_available'):
        if record.get(field) is not None and type(record[field]) is not bool:
            raise ValueError('care selections must be boolean or null')
    role = record.get('overnight_custodian_role')
    if role is not None and role not in ROLES: raise ValueError('unsupported anonymous care role')
    times = ('arrival_time', 'arrival_timezone', 'pickup_deadline', 'pickup_timezone')
    if any(record.get(k) is None for k in times): pickup = 'missing'
    else:
        try:
            arrival = instant(record['arrival_time'], record['arrival_timezone'])
            deadline = instant(record['pickup_deadline'], record['pickup_timezone'])
            pickup = 'window_missed' if arrival > deadline else 'within_reported_window'
        except ValueError: pickup = 'invalid_time'
    required, care = record.get('overnight_required'), record.get('overnight_care_available')
    if required is False: overnight = 'not_reported_required'
    elif required is None: overnight = 'requirement_unknown'
    elif care is False: overnight = 'care_unavailable'
    elif care is None: overnight = 'care_unknown'
    elif role is None: overnight = 'custodian_unassigned'
    else: overnight = 'self_reported_pending_confirmation'
    blocked = pickup == 'window_missed' or overnight == 'care_unavailable'
    return dict(status='blocked' if blocked else 'needs_confirmation', pickup_outcome=pickup,
                overnight_outcome=overnight, overnight_custodian_role=role or 'pending_arrangement',
                custody_confirmed=False, external_confirmation='unknown',
                reason_codes=sorted(set(['final_pickup.' + pickup, 'overnight.' + overnight,
                                         'recovery_custody_and_care_arrangement_required' if blocked else
                                         'dated_handover_capacity_and_custody_unconfirmed'])))
