# Hello Deck

A bromigOS live-layer deck: a full-screen hologram of this machine's load average.

```sh
bromigos ext install ./hello-deck        # or its git URL
bromigos-live plugin hello-deck          # open it; Esc closes it
```

`deck.py` is the whole deck: `_sample()` fetches (on a poller thread), `build()` draws
with deckkit's painter (`b.arc`, `b.line`, `b.text`; `space=2` is the deck's 3D space),
`pick_pts`/`pick_ids` make things hoverable. docs/plugins.md and the live layer's
`live/deckkit.py` have the rest. Declare what it reaches in `bromigos-ext.toml`'s
`[permissions]` (hosts, paths): people see it before they install.
