"""Civil-day certificate margin diagnostics; never extend or certify validity."""
from datetime import timedelta
from packages.engine.evaluate import day


def certificate_margin(start, check, maximum_days, *, buffer_days=0):
    """Research window only: buffers affect planning margin, never the deadline.

    Missing/invalid dates and dates before issue remain distinct. No default
    safety buffer, hourly conversion, sea extension or appointment guarantee.
    """
    if type(buffer_days) is not int or not 0 <= buffer_days <= 365:
        raise ValueError('planning buffer must be an integer from 0 to 365 days')
    result = dict(anchor_date=start, check_date=check, deadline=None,
                  remaining_days=None, planning_buffer_days=buffer_days,
                  planning_margin_days=None, outcome='missing_date',
                  date_policy='civil_day_research_estimate', enforceable=False)
    if start is None or check is None:
        return result
    try:
        issued, checked = day(start), day(check)
        deadline = issued + timedelta(days=maximum_days)
    except (ValueError, TypeError, OverflowError):
        result['outcome'] = 'invalid_date'
        return result
    remaining = (deadline - checked).days
    result.update(deadline=deadline.isoformat(), remaining_days=remaining,
                  planning_margin_days=remaining - buffer_days)
    result['outcome'] = ('check_before_issue' if checked < issued else
                         'expired' if remaining < 0 else
                         'buffer_shortfall' if remaining < buffer_days else
                         'within_research_window')
    return result
