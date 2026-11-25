# Technical notes

## Input contract

The patch is tied to a single binary, not merely to the HBC version.

| Artifact | SHA-256 |
| --- | --- |
| Source, 2,955,088 bytes | `68cc48434e2768750836d439c7adbcb9375f26a5d5a39ccb3c855cea7bd405d6` |
| Scale-only output | `7b94413ec5103057995afe97530e7b9673b0adba3e2a1d6e087b86dea1636219` |
| Full output, 2,956,279 bytes | `39956da883bf02111929d0fb68176537ecb2a4cc30c1a900a56037e062cbb97a` |

The original bundle contains 18,299 functions. Its first eight bytes are `C6 1F BC 03 C1 03 19 1F`, followed by bytecode version 96.

## Patch map

These IDs and offsets are valid only for the source hash above.

| Function / location | Change |
| --- | --- |
| Shared object-value buffer, absolute offset 803533 | Serialized tag for two int32 values; payload at 803534 changes 940/540 to 1175/675 |
| 17171, relative 0x245 | Visual expansion predicate becomes true; keyboard adjustment mode stays separate |
| 17200, relative 0x16b and 0x176 | Static opacity and translation for the volume bar |
| 17175 | Slider animation effect returns without scheduling animation |
| 5966 | Sentry setup returns without initialization |
| 17286, relative 0x37 | Decorative equalizer animation predicate becomes false |
| 11293, relative 0x42 | Default inactive query retention becomes 60,000 ms |
| 17488 | Sidebar rendering function receives a volume component and is relocated before the footer |

The sidebar imports the existing Metro module 1890 (VolumeSlider), reuses the shared volume store, and rotates a wrapper by -90 degrees. It is mounted outside the native focus-memory container, which clipped the first attempted placement.

The new sidebar bytecode is inserted after existing branches so their relative destinations remain stable. Its function ID is preserved, and its header offset, bytecode size and highest read-cache index are updated. The bundle's file length and SHA-1 footer are recomputed. Final output SHA-256 must match the known validated result.

## Local package layout

1. Read the installed package into `original/`.
2. Validate and patch the bundle in memory.
3. Create `compact-80/` using the local snapshot.
4. Replace only the local manifest identity with `SoundClaude.Compact80`.
5. Remove the now-invalid Store signature and block map from the local layout.
6. Register that unsigned development layout through Windows package deployment.

This is a UWP development layout, not a signed distributable MSIX. Direct executable launch did not produce a usable standalone app in the investigation. Developer Mode was required for registration on the test machine.

Source identity and Publisher are preserved where needed for the native entrypoint and WinRT classes; the local package Name and display name are separate. App storage is consequently separate, and a fresh login was required.

## Design decisions

- **Exact binary guards:** matching HBC96 alone does not make hardcoded function IDs safe.
- **Reproducible outputs:** source and output hashes make unintended changes detectable.
- **No global zoom patch:** the shared application sizing utility directly controls relevant layout values.
- **Visual state separated from input mode:** keeping volume visible must not permanently capture navigation keys.
- **No resident launcher:** priority adjustment is a bounded startup operation.
- **No working-set trimming:** forcibly dropping resident pages can cause paging and does not eliminate allocations.

## Limits

Not all dimensions necessarily use SizeUtil. Design scaling depends on window dimensions at initialization, and resizing behaviour has not been exhaustively tested. The application version is old and may become unavailable through the Store.

The precise native memory floor is unknown. Subscription features, every possible screen, account migration and future updates have not been exhaustively tested. The patch changes UI and optional diagnostics; it does not modify authentication or entitlement logic.

## Tooling

[hermes-dec](https://github.com/P1sec/hermes-dec) provides the parser and opcode definitions. Setup-Tools.ps1 fetches an immutable revision. No proprietary input or complete disassembly is checked into this repository.
