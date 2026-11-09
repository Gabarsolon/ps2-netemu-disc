# P16: service-context findings

The logger is now working on the console. These findings narrow the remaining
authentication investigation; they do not establish an authentication fix or
identify the emulator's live secure-service image.

## What the console established

See [P16_CONSOLE_RESULT.md](P16_CONSOLE_RESULT.md) for hashes and artifacts.

- With the existing two branch patches verified before launch, the emulator
  received a properly identified `0x5005` reply with status `0x16`, zero key
  flags and an unchanged sector buffer.
- A temporary forced-error marker in the PS2 helper was verified as data
  before launch, but its expected `0x5a` did not appear in the emulator reply.
  The word was stock after return to XMB.
- A separate GameOS helper marker did execute: the controlled syscall returned
  exactly `0xffffffff8001055a`. The marker was then restored and verified stock.

The GameOS result confirms effective code modification in that service image.
It does not prove that the emulator uses the same image, physical mapping or
instruction state at its different entry point.

## GameOS syscall interface is not the raw VUART command interface

The exact firmware 4.93 LV2 syscall table resolves syscall 864 to its secure
access wrapper. Its jump table covers selectors `0x5004..0x5012`, but selectors
`0x5005` and `0x5006` enter the default error path. Calling userland
`syscall864(0x5005, ...)` is therefore not a direct positive control for the
emulator's VUART opcode `0x5005`.

The `0x5004` selector does accept a scalar mode and reaches the separately
audited GameOS helper. Offline execution of the real wrapper confirmed the
error translation used in the successful live control: secure status `0x5a`
becomes kernel result `0x8001055a`. The test's native helpers and transport
boundaries were mocked; the actual wrapper and status translation executed.

Private primary evidence:

- `local_only/p16_service_context/syscall864_cases.json`;
- `local_only/p16_service_context/lv2/` targeted instruction/decompiler output;
- `local_only/p16_service_context/kernel_status_abi.json`;
- `local_only/p16_service_context/host_sentinel_abi.json`.

## Port numbers are scoped to the caller

The local 4.93 LV1 code for the VUART write hypercall first obtains the current
caller context, follows its owning context, and looks up the indexed endpoint
in that owner's endpoint table. It then follows the endpoint's peer and checks
peer state before transferring data. The VUART read path uses the same kind of
caller-owned endpoint lookup.

Conceptually, the lookup is:

```
endpoint = current_caller.owner.vuart[port_number]
destination = endpoint.peer
```

Thus the number 10 does not identify a single system-wide service instance.
Different callers can have different endpoints at index 10. This is a primary
code fact, not yet a measurement of which peers GameOS and netemu actually use.

Source: `local_only/p16_service_context/lv1/fn_002f2af4.{c,asm}` and adjacent
read-side extraction from the exact local LV1 ELF. The earlier assumption that
the XMB mapping must also be the emulator's target is not established.

The system-manager image also has distinct PS2 NE launch metadata and shutdown
paths. Those names and branches support investigating partition context, but
do not by themselves identify a reload point for ss_server1.

## A guessed invalid mode is not a read-only query

The audited GameOS helper performs readiness, sense, and firmware/REPORT KEY
work before its final supported-mode dispatch. An unsupported mode would not
necessarily return before those operations. Special modes also have explicit
state-changing paths. No invalid-mode experiment was performed.

Similarly, the direct CFW LV1-call facility is not a ready substitute for a
typed GameOS wrapper. VUART buffers need correct LPAR translations, and a raw
GameOS consumer could interfere with the existing VUART consumer. No raw
GameOS VUART experiment was performed.

## Remaining unknowns

The unresolved question is which endpoint peer and service image handle the
emulator's actual request. The available observations do not distinguish all
of service-instance differences, image reload timing, physical mapping changes
and instruction visibility. A future comparison needs a verified request ABI,
known native effects and an independent observation of that context.

Keep the validated logger and the measured request/reply identity as the
baseline. Do not treat another absent marker, a stock word after reboot, or an
accepted profile branch as proof of the missing runtime relationship.
