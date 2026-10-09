# Uptime Tool

A tool for VECTOR, bromigOS's desktop AI: `uptime_tool_uptime` tells him how long this
machine has been up and how loaded it is.

```sh
bromigos ext install ./uptime-tool        # or its git URL; it asks (it runs code)
bromigos restart vector                # he loads plugins at his start
```

Add tools in `register(vector)`: `vector.tool(name, description, json_schema, fn,
level="read"|"desktop")`. Declare the level in `bromigos-ext.toml`'s `[permissions]
vector`, and the hosts and paths it reaches: people see them before they install.
