#!/usr/bin/env python3
"""Checks the catalog (CI runs it; so can you: python3 tools/check.py).

  * index.toml and every example's bromigos-ext.toml against the JSON Schemas (schema/);
  * every entry: a unique name; a preview that exists (a PNG, JPEG or WebP under 1 MB);
  * every entry in this repository (url = this repo, path = its folder): the folder has a
    manifest whose name and kinds match the entry; each part's path exists, inside the
    folder, not a symlink; commands and hooks are committed executable; Python compiles;
    the permissions match the parts (code = true when a part runs code, a VECTOR level
    for VECTOR tools and memory, never the terminal); no symlink leaves the folder.

bromigos ext validate (in bromigOS) is the full check at install time; this one keeps the
catalog honest without bromigOS's binary.
"""
import json
import os
import py_compile
import subprocess
import sys
import tempfile
import tomllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE_URLS = ("https://github.com/bromigos-org/extensions", "https://github.com/bromigos-org/extensions.git",
             "git@github.com:bromigos-org/extensions.git")
CODE = {"live-deck", "widget", "vector-tool", "vector-memory", "homelab-adapter", "command", "hook"}
EXEC = {"command", "hook"}
errors = []


def fail(where, msg):
    errors.append(f"{where}: {msg}")


def schema_check(doc, schema_file, where):
    try:
        import jsonschema
    except ImportError:
        fail(where, "jsonschema isn't installed (pip install jsonschema)")
        return
    with open(os.path.join(ROOT, "schema", schema_file)) as f:
        schema = json.load(f)
    v = jsonschema.Draft202012Validator(schema)
    for e in sorted(v.iter_errors(doc), key=lambda e: list(e.path)):
        fail(where, f"{'/'.join(str(p) for p in e.path) or '(top)'}: {e.message}")


def git_modes():
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "-s"], capture_output=True, text=True).stdout
    return {line.split("\t", 1)[1]: line.split()[0] for line in out.splitlines() if "\t" in line}


def inside(base, path):
    b = os.path.realpath(base)
    return os.path.realpath(path) == b or os.path.realpath(path).startswith(b + os.sep)


def check_example(entry, modes):
    name = entry["name"]
    folder = os.path.join(ROOT, entry["path"])
    where = f"{name} ({entry['path']})"
    if not inside(ROOT, folder) or not os.path.isdir(folder):
        fail(where, "no such folder in this repository")
        return
    mpath = os.path.join(folder, "bromigos-ext.toml")
    if not os.path.isfile(mpath) or os.path.islink(mpath):
        fail(where, "no bromigos-ext.toml (or it's a symlink)")
        return
    with open(mpath, "rb") as f:
        m = tomllib.load(f)
    schema_check(m, "bromigos-ext.schema.json", f"{where} bromigos-ext.toml")
    meta = m.get("extension", {})
    if meta.get("name") != name:
        fail(where, f"the manifest calls it {meta.get('name')!r}")
    parts = m.get("provides", [])
    kinds = sorted({p.get("kind") for p in parts})
    if kinds != sorted(set(entry.get("kinds", []))):
        fail(where, f"kinds {entry.get('kinds')} but the manifest provides {kinds}")
    perms = m.get("permissions", {})
    if any(k in CODE for k in kinds) and not perms.get("code"):
        fail(where, "a part runs code: [permissions] code = true")
    if any(k in ("vector-tool", "vector-memory") for k in kinds) and perms.get("vector") not in ("read", "desktop"):
        fail(where, "VECTOR tools or memory: [permissions] vector = \"read\" or \"desktop\"")
    for p in parts:
        path = os.path.join(folder, p.get("path", ""))
        if not inside(folder, path) or not os.path.exists(path):
            fail(where, f"{p.get('kind')} {p.get('path')!r}: missing or outside the folder")
            continue
        if os.path.islink(path):
            fail(where, f"{p.get('path')!r} is a symlink")
        if p.get("kind") in EXEC:
            rel = os.path.relpath(path, ROOT)
            if modes.get(rel) != "100755":
                fail(where, f"{rel} isn't committed executable (git update-index --chmod=+x)")
    for dp, dns, fs in os.walk(folder):
        dns[:] = [d for d in dns if d != "__pycache__"]
        for f in fs + dns:
            p = os.path.join(dp, f)
            if os.path.islink(p) and not inside(folder, p):
                fail(where, f"{os.path.relpath(p, folder)}: a symlink out of the extension")
            if f.endswith(".py") and os.path.isfile(p):
                with tempfile.TemporaryDirectory() as t:
                    try:
                        py_compile.compile(p, cfile=os.path.join(t, "x.pyc"), doraise=True)
                    except py_compile.PyCompileError as e:
                        fail(where, f"{f}: {e.msg.strip().splitlines()[-1]}")


def main():
    with open(os.path.join(ROOT, "index.toml"), "rb") as f:
        index = tomllib.load(f)
    schema_check(index, "index.schema.json", "index.toml")
    modes = git_modes()
    seen = set()
    entries = index.get("extension", [])
    for e in entries:
        name = e.get("name", "?")
        if name in seen:
            fail(name, "listed twice")
        seen.add(name)
        pv = e.get("preview")
        if pv and not pv.startswith("https://"):
            p = os.path.join(ROOT, pv)
            if not inside(ROOT, p) or not os.path.isfile(p):
                fail(name, f"preview {pv} doesn't exist")
            else:
                with open(p, "rb") as f:
                    head = f.read(12)
                if not (head.startswith(b"\x89PNG") or head.startswith(b"\xff\xd8") or head[8:12] == b"WEBP"):
                    fail(name, f"preview {pv}: not a PNG, JPEG or WebP")
                if os.path.getsize(p) > 1 << 20:
                    fail(name, f"preview {pv}: over 1 MB")
        if e.get("url", "").rstrip("/") in HERE_URLS and not e.get("bundled"):
            if not e.get("path"):
                fail(name, "an entry in this repository needs its path")
            else:
                check_example(e, modes)
    for err in errors:
        print("ERROR", err)
    print(f"{len(entries)} entries, {len(errors)} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
