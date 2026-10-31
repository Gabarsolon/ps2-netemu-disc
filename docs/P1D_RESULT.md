# P1d result (console, 2026-10-31)

Variant A (`local_only/p1d/ps2_netemu_p1d_A.self`): one `lv1_open_device(bus_id=9, dev_id=0, flags=0)` issued from the menu hook through our own `sc 0` wrapper (code slot 0x4820). Variant B (close(4,2) without open) was not run.

- **PROVEN (owner):** the console crashed (powered off) with variant A.
- **INFERRED:** an open with an INVALID bus id, which touches no device, is enough to kill the partition. So the cause is not "the optical device was opened". It is the open_device hypercall itself in this context, or our way of issuing it.
- **Differences between the stock HDD open (works) and ours (fatal), all UNKNOWN as to which matters:**
  1. Stock issues 170 inside its init path (early); ours is issued later from the menu hook.
  2. Stock `sc 0` sits in stock text; ours sits in our wrapper in the code slot (0x4828). The repository reads (91) that work go through the STOCK helper `0x111eb8`, not through an own wrapper.
  3. 4.93 / Evilnat LV1 or the guest bridge may treat 170/171 after init differently (e.g. a lock-down after init).
- Next: P1e tests difference 2 with a harmless call: our own wrapper issuing LV1 91 (a repository read that works through the stock helper).
