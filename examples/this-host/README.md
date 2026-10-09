# This Host

A homelab adapter for bromigOS: it provides the `hosts` capability with this machine.

```sh
bromigos ext install ./this-host        # or its git URL; it asks (it runs code)
```

Then add a source to `~/.config/bromigos/homelab.toml` and restart what reads it:

```toml
[[source]]
type = "this_host"
```

`adapter.py` shows the shape: a `registry.Adapter` subclass, `@register`ed under its
`type`, with `provides` and one method per capability. docs/homelab.md has the rest.
