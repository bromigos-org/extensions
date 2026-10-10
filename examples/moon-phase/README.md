# Moon Phase

A bromigOS desktop widget: the Moon's phase tonight, how much of it is lit, and the days
to the next full and new moon. It fetches nothing. The phase comes from the date.

```sh
bromigos ext install moon-phase           # from the catalog; it appears within seconds
bromigos-widgets render moon_phase OUT.png
```

`widget.py` defines a `panels.Panel` subclass. Its `description`, `category` and `reads`
are what bromigOS's widget gallery shows, and `min_size` and `max_size` are the sizes
edit mode lets it take. bromigOS's docs/plugins.md has the rest.
