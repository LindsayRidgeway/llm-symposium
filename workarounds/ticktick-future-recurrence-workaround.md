# TickTick Connector: Workaround for Projecting Future Recurring Tasks

## Problem

The TickTick connector may not explicitly return every future occurrence of a recurring task, even though TickTick's native calendar displays those occurrences.

Therefore, future schedule queries cannot reliably be answered by listing only explicitly returned future task instances.

## Workaround

For calendar-style questions, retrieve the recurring task itself and inspect its recurrence rule.

Use that recurrence rule to project future occurrences for the requested date range.

Conceptually:

1. Retrieve relevant tasks, including recurring tasks.
2. Identify each task's recurrence rule.
3. Expand the recurrence rule across the requested future date range.
4. Combine those projected occurrences with explicitly dated non-recurring tasks.
5. Deduplicate any occurrences that TickTick has already returned explicitly.
6. Present the resulting combined schedule to the user.

## Example

Suppose a task is defined to recur every four weeks.

The connector may return:

- June 13
- July 11
- August 9

while failing to return the next occurrence.

If the recurrence rule itself remains active, project the next occurrence from the rule rather than concluding that the schedule ends with August 9.

Likewise, if a class is defined to recur Monday through Friday, project the weekday occurrences within the requested period even if only one or two upcoming instances were explicitly returned.

## Important Qualification

A calculated occurrence should be described internally as **projected from the recurrence rule**, not as an independently returned task instance.

The recurrence rule is the basis for the projection.

If the recurrence rule is unavailable, ambiguous, has exceptions, or may have been modified, do not invent future occurrences. Report the limitation instead.

## Recommended Interpretation

For future calendar questions:

**recurrence definition + explicit one-time tasks → projected calendar**

rather than:

**explicitly returned future instances → calendar**

The former more closely reproduces the behavior observed in TickTick's native projected calendar.

## Maintenance

Because connector behavior can change, periodically test whether future recurring instances have begun appearing reliably. If they have, this workaround may no longer be necessary.
