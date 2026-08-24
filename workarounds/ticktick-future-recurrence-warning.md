# TickTick Connector: Future Recurring Tasks May Be Missing

## Status

Observed behavior. Treat as a connector limitation unless/until independently verified or corrected.

## Warning

Do not assume that the absence of a future recurring task from results returned by the TickTick connector means that the task is not scheduled in TickTick.

We observed a case involving a recurring task ("Begin one week of terbinafine") in which:

- TickTick's native app showed the next occurrence on September 6, 2026.
- The connector returned previous occurrences of the recurring task.
- The connector did not return the September 6 occurrence.
- Therefore, an LLM relying only on the returned future-task list incorrectly concluded that no future occurrence existed.

A similar problem was subsequently observed with recurring Chumash classes: the connector returned some near-term occurrences but did not provide all of the future occurrences visible/projected by TickTick.

## Likely Explanation

TickTick appears to distinguish between recurring-task definitions and individual occurrences generated from their recurrence rules.

The native TickTick calendar can project future occurrences from those rules even when those occurrences are not individually returned through the connector.

The precise layer responsible has not been established. Possibilities include TickTick's API, the MCP/connector implementation, or the way its query results expose recurring tasks.

## Operational Rule

When answering questions about future schedules:

**Do not treat the connector's explicitly returned future tasks as a complete calendar.**

In particular, do not tell the user that a recurring event does not exist merely because a future occurrence was not returned.

## Provenance

Discovered empirically during use of the TickTick integration in August 2026.

This entry should be revised or retired if subsequent testing shows that the connector's behavior has changed.
