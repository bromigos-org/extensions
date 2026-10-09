# Load Panel

A bromigOS desktop widget: a panel of this machine's load average.

```sh
bromigos ext install ./load-panel        # or its git URL; it appears within seconds
bromigos-widgets render load_panel OUT.png
```

`widget.py` defines a `panels.Panel` subclass: `tick()` samples, `draw()` paints
(cairo, and the widgets' `draw` helpers: `D.frame`, `D.label`, `D.seg7`, `D.spark`,
`D.ring`, …), `region()` gives each part its hover hint. `LAYOUT` sizes it; the user's
`layout.json` can place it. docs/plugins.md has the rest.
