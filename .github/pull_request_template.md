<!-- Adding or changing a listing? Tick each box. Anything else: say what and why, and delete the list. -->

**What this adds or changes**

<!-- The extension, its repository and its release tag, and one line on what it does. -->

**Checklist**

- [ ] `bromigos ext validate` passes on the extension.
- [ ] It has a licence and a README, and a tagged release that `ref` names.
- [ ] Its permissions declare everything it reaches (code, network hosts, paths).
- [ ] The entry's `name` matches the manifest, and `kinds` matches its parts.
- [ ] There's a preview in `previews/` (PNG, JPEG or WebP, under 1 MB).
- [ ] For a widget: its category is in `tags`, and it shows real data only.
- [ ] `tools/check.py` passes (it prints `… entries, 0 errors`).

See [CONTRIBUTING.md](../CONTRIBUTING.md) for each step and what reviewers look for.
