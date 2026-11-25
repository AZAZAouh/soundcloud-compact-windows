# Validation and performance

Local observations from 24 November 2026. Windows 11 25H2, 8 logical processors, SoundCloud 2.12.4.0 x64.

## Functional checks

| Check | Result |
| --- | --- |
| Separate UWP registration | Registered as SoundClaude.Compact80 |
| Original installation | 77 copied files matched the installed source |
| Login | User completed activation in the separate app |
| Compact UI | User confirmed the smaller layout |
| Player volume | Visible without hover |
| Sidebar volume | Vertical bar visible on the home screen |
| Drag interaction | Tested on both controls |
| Shared state | Sidebar change appeared on the player slider |
| Playback | Track started and progress advanced |
| Patched binary | Fully disassembled after modification; checksum and file length verified |
| Lower priority launcher | BelowNormal observed; launcher exits |

The final attempt to restore the minimized window was stopped by the user's Escape key. No further UI input was issued after that interruption. Continued track progress after that particular minimize/restore cycle was not visually rechecked.

## Short process samples

| Scenario | Interval | Process CPU time | Average total CPU, 8 logical processors | Working set | Private commit |
| --- | ---: | ---: | ---: | ---: | ---: |
| Scale-only home idle, after 15 s warmup | 15.022 s | 0 s | 0% | 202.2 MiB | 345.4 MiB |
| Full patch home idle, after 15 s warmup | 15.010 s | 1.625 s | ~1.35% | 203.5 MiB | 347.5 MiB |
| Full patch, minimized during playback | 15.013 s | 0.390625 s | ~0.33% | 199.2 MiB | 251.7 MiB |

`average total CPU % = delta process CPU seconds / wall seconds / logical processor count × 100`

Working set and private commit are different measurements; neither is a guaranteed cap. These short samples include variability from application lifecycle, networking, image loading, focus and Windows scheduling.

**No material RAM reduction or general speedup is established.** The visible-window sample has higher CPU with the persistent volume UI. The minimized playback result is the most relevant observation for the original gaming use case, but there is no matched baseline playback sample proving a reduction.

Disabling the equalizer removes a specific 120 ms React-state interval. Disabling Sentry removes its initialization. Shorter inactive query retention can release query data earlier. These are concrete implementation changes, not claims about a measured percentage gain.

Valorant FPS, GPU utilization, audio latency, very long sessions and behaviour under memory pressure were not benchmarked.

## Automated checks

Four tests use synthetic inputs to verify rejection of:
- truncated input;
- an unsupported bytecode version;
- an invalid footer;
- an unknown input even with a valid footer.

An additional integration test runs only if the local supported bundle exists. It verifies both scale-only and full output hashes, the declared file length, the SHA-1 footer, and that the input remains unchanged.

The public CI cannot validate the real application UI or the binary transformation without the proprietary input. The integration test is explicitly skipped there; it is not reported as an application test.
