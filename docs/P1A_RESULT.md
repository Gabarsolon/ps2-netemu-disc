# P1a result (console test, 2026-10-31)

Build: `local_only/p1a/ps2_netemu_p1a.self` (sha256 `17d5ed32390e1d5d1dc3a3c74c18d9a81d2cc62edf0732a4c23442380d7700d6`), repository lookups only (LV1 91), label-only.

Label text as reported by the owner (typed from the `Debug Information` row, not yet cross-checked against photos):

`p1a DONE devs=12 rom=1 hdd=1 rom b=04 d=02 p=0 t=5 hdd b=0 d=0 p=? ph=both err rc=-6 sb=b4 n=65+`

## Reading

- **PROVEN (console, via label):** the repository seen from the ps2_netemu partition contains an optical (ROM, device type 5) storage node: bus index 4, device index 2, port 0. 12 devices in total were enumerated; the probe made 65 or more LV1 91 calls without any fault.
- **PROVEN:** it is on storage bus index 4 (`sb=b4`, bus type 5), the same bus index the netemu's own HDD enumerator searches (`0x114ea4(4, 0, info, type 0, port 2)`), so the HDD and the optical drive are siblings on one bus. `ph=both` means both phat-emulator selector guesses (bus type 5, bus index 4) matched.
- **INFERRED:** `err rc=-6` is `LV1_NO_ENTRY` (repository node missing), the expected result for the nonexistent bus/device indexes the scan walks past. Not an anomaly.
- **Caveat on the HDD control:** the page-C control reported the FIRST type-0 device the scan met (bus 0, dev 0, port unreadable), not the netemu's HDD (stock expects bus 4, port 2). So the control did not confirm the HDD as designed. It does not invalidate the ROM finding: the repository reads work and return plausible structure; but the "hdd" line should not be read as the netemu HDD.
- **UNKNOWN:** whether `lv1_open_device` on that node is allowed for this partition (visible is not the same as permitted); whether reads work after an open; the 64-bit bus/dev ids (stored in the mailbox, not shown).

## Next

P1b: attempt `open_device` (LV1 170) on the found ROM node with the ids read from the repository, log the return code, then close (171). No reads, no drive commands. Needs the owner's approval; worst case a hang or reboot of the partition.
