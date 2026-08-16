"""Local, offline visualization (P20 replay viewer + P21 GUI).

Two presentation layers over one model layer: a headless text renderer and a Tkinter
window (`tk_live`, `tk_replay`), both fed by the same pure view-models (`live_model`,
`replay_model`) so every rendering decision stays unit-testable without a display.

The live GUI shows only the local player's truth and can never reveal the opponent's
position; the replay viewer works on post-audit records where both trajectories are
legally revealed, and its VERIFIED OK / TAMPERED badge is the output of the real
per-record SHA-256 check in `replay_verify`."""
