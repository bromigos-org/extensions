# Contributing to the catalog

This repository is the catalog of bromigOS extensions: the list that `bromigos ext
search`, the theme switcher and the widget gallery's **Get more widgets** read. This page
says how to add your extension to it, what the check tests, and what reviewers look for.

To make an extension first, start from a starter (`bromigos ext new KIND NAME`). The
bromigOS manual's [Make your own widget](https://github.com/bromigos-org/bromigOS/blob/main/manual/src/make-a-widget.md)
page walks through one, and bromigOS's
[docs/extensions.md](https://github.com/bromigos-org/bromigOS/blob/main/docs/extensions.md)
is the full reference.

## Before you open a pull request

Your extension lives in its own git repository. Check that:

- `bromigos-ext.toml` is at its root, or in a folder you'll name in the entry's `path`;
- `bromigos ext validate` passes on it;
- it has a licence and a README that says what it does;
- it has a tagged release, so the listing can pin it (`git tag v1.0.0 && git push --tags`);
- its permissions say everything it reaches: `code = true` when any part runs code, every
  host it talks to under `network`, and every path outside its folder under `filesystem`.

## Add the entry

1. Fork this repository.
2. Add an `[[extension]]` entry to `index.toml`, in the section that fits. The fields are
   [below](#entry-fields).
3. Add a picture to `previews/`: a PNG, JPEG or WebP under 1 MB. For a theme, use the
   switcher's own picture:

   ```sh
   bromigos theme previews --dir path/to/theme --out previews/NAME.jpg
   ```

   For a widget, draw it offscreen at its default size:

   ```sh
   bromigos-widgets render path/to/widget.py previews/NAME.png
   ```

4. Run the check, the same one CI runs. It needs Python 3.11 or newer and the
   `jsonschema` package.

   ```sh
   python3 -m venv /tmp/venv && /tmp/venv/bin/pip install jsonschema
   /tmp/venv/bin/python tools/check.py
   ```

   It prints each problem, then a count such as `15 entries, 0 errors`.
5. Open a pull request. The template asks you to confirm each step.

An entry looks like this:

```toml
[[extension]]
name = "moon-phase"
display_name = "Moon Phase"
description = "A desktop widget with the Moon's phase tonight, worked out from the date."
kinds = ["widget"]
url = "https://github.com/you/moon-phase"
ref = "v1.0.0"
preview = "previews/moon-phase.png"
tags = ["widget", "fun"]
authors = ["Your Name"]
licence = "MIT"
```

### Entry fields

| Field | Required | What it holds |
|---|---|---|
| `name` | Yes | The extension's name, exactly as its manifest gives it |
| `description` | Yes | One line on what it is |
| `kinds` | Yes | The kinds of the parts it provides, such as `["widget"]` |
| `url` | Yes | The git repository, starting with `https://`, `ssh://` or `git@` |
| `display_name` | No | The name people see, such as `Moon Phase` |
| `path` | No | The extension's folder, when it isn't at the repository's root |
| `ref` | No | A tag or branch to install instead of the default branch |
| `preview` | No | A picture in `previews/`, or an `https://` URL |
| `tags` | No | Words that help search find it. For a widget, include its category: `system`, `network`, `homelab`, `media`, `notes` or `fun` |
| `authors` | No | Who made it, shown on its card |
| `licence` | No | Its licence, shown on its card |
| `bundled` | No | `true` for an extension that ships with bromigOS |

## What the check tests

`tools/check.py` reads the listing, never runs the code:

- `index.toml`, and each example's manifest, against the schemas in `schema/`;
- each name listed once;
- each preview exists, is a PNG, JPEG or WebP, and is under 1 MB;
- for an entry in this repository, its folder: the manifest's name and kinds match the
  entry, each part exists inside the folder and isn't a symlink, commands and hooks are
  committed executable, Python compiles, the permissions match the parts, and no symlink
  leaves the folder.

## What reviewers look for

A person reads every listing before it's merged. They look at:

- **What it does matches what it says.** The description, the README, the permissions
  and the code tell the same story.
- **Nothing hidden.** No code that downloads and runs other code, no obfuscated code, no
  network access the permissions don't declare, and nothing that sends data anywhere the
  README doesn't say.
- **Real data.** A widget shows real readings, and says so when it has none. No made-up
  numbers dressed as readings.
- **It fits the desktop.** It draws with the panels' own helpers, in the theme's colours,
  and every part a pointer can rest on has a hover hint.
- **Accounts the right way.** A widget that signs in to a service uses a `secret-signin`
  setting and `bromigos_account`, so tokens stay in the keyring. It never asks for a
  password, and never stores a token in a file.
- **A pinned release.** `ref` names a tag, so what was reviewed is what installs.
- **A licence** that lets people use it.

A listing can be removed if the extension changes into something it didn't say it was.
To report a harmful extension or a hijacked listing, follow [SECURITY.md](SECURITY.md).
Don't open a public issue for it.

## Other changes

To fix a typo, a broken link or an example here, open a pull request. To ask for a
listing without making the change yourself, use the "List an extension" issue form.
Everyone here follows the [Code of Conduct](CODE_OF_CONDUCT.md).
