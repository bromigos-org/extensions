# Teal Glass

A bromigOS theme. Install it:

```sh
bromigos ext install https://github.com/you/teal-glass     # or: bromigos ext install ./teal-glass
bromigos theme set teal-glass
```

Edit `colors.toml` (the roles every app reads) and `theme.toml` (its name and mode);
add `backgrounds/`, `emblem/` or a painted world as `docs/theming.md` describes. Check
it with `bromigos ext validate .`, commit, push, and tag a release (`git tag v0.1.0`) so
people can pin it (`bromigos ext install <url>@v0.1.0`).
