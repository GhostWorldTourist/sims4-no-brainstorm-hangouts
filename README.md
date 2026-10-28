# No Brainstorm Hangouts

Apartment and penthouse neighbours (City Living) stop coming over to brainstorm.
"Invite to Brainstorm" and "Reject Brainstorm" never come up, because the visit
that puts them in the pie menu never gets scheduled. Every other neighbour
hangout works as before.

## How

Each of the six brainstorm hangout situations gets one `weight_multipliers`
entry of `0`. The apartment zone director multiplies a situation's own
multiplier into its pick chance, so these score zero and are never chosen. The
neighbour picks a different visit. `build.py` has the detail.

- Tuning only, no script. Nothing runs during play.
- Six small situation overrides. The zone directors are left alone.
- Requires City Living. Without it the overrides point at nothing and do nothing.

## Build

```
py build.py
```

Reads EA's tuning from the installed game, edits it, and writes
`GhostWorldTourist_NoBrainstormHangouts.package`. If a patch changes these
situations, the build stops and says so instead of overwriting EA's change.

Author: GhostWorldTourist
