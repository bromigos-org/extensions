# bromigOS extensions

The catalog of bromigOS extensions: themes, live-layer decks and shader layers, desktop
widgets, VECTOR's tools, memory stores and skills, homelab adapters, commands and
theme-set hooks. `bromigos ext search` reads `index.toml`; the theme switcher shows its
themes with their previews; `bromigos ext install <name>` installs one by name.

```sh
bromigos ext search                 # everything here
bromigos ext search --kind theme    # just the themes
bromigos ext info hello-deck        # what it would install, and its permissions
bromigos ext install hello-deck     # asks first when it runs code or reaches VECTOR
```

How extensions work — the manifest, permissions, the ledger, updates, VECTOR's guard —
is in bromigOS's `docs/extensions.md`.

## What's here

| | |
|---|---|
| `index.toml` | the catalog: one `[[extension]]` per entry (name, description, kinds, url, path, ref, preview, tags; `bundled` for what ships with bromigOS) |
| `examples/` | one working extension per kind, each made by `bromigos ext new <kind> <name>` and tested: `teal-glass` (theme), `hello-deck` (live deck), `load-panel` (widget), `uptime-tool` (VECTOR tool), `this-host` (homelab adapter) |
| `previews/` | the pictures the switcher and search show |
| `schema/` | JSON Schemas for `bromigos-ext.toml` and `index.toml` (point your editor's TOML schema setting at them) |
| `tools/check.py` | what CI runs on every push and pull request |

## Adding an extension

1. Make it: `bromigos ext new <kind> <name>` (or `bromigos theme new <name> --from wick`),
   edit it, `bromigos ext validate .`, install it with `bromigos ext install --copy .`
   and use it.
2. Publish it: a git repository with `bromigos-ext.toml` at its root (or a folder in one:
   give `path`), a licence, and a tag (`git tag v1.0.0 && git push --tags`).
3. Add an `[[extension]]` to `index.toml` (and a preview to `previews/`, a PNG, JPEG or
   WebP under 1 MB), run `python3 tools/check.py`, and open a pull request.

The catalog checks listings, not code: an extension that runs code shows its declared
permissions before it installs, and the person installing decides. Mire and Tidewell ship
with bromigOS and are listed here so they can be found.

## Licence

MIT OR Apache-2.0, at your option (`LICENSE-MIT`, `LICENSE-APACHE`). Each example is
under the same terms; an extension listed from elsewhere keeps its own licence.
