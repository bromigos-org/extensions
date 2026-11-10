#!/usr/bin/env python3
"""Checks the catalog (CI runs it; so can you: python3 tools/check.py).

  * index.toml and every example's bromigos-ext.toml against the JSON Schemas (schema/);
  * every entry: a unique name; a preview that exists (a PNG, JPEG or WebP under 1 MB);
  * every entry in this repository (url = this repo, path = its folder): the folder has a
    manifest whose name and kinds match the entry; each part's path exists, inside the
    folder, not a symlink; commands and hooks are committed executable; Python compiles;
    the permissions match the parts (code = true when a part runs code, a VECTOR level
    for VECTOR tools and memory, never the terminal); no symlink leaves the folder;
  * every folder under examples/ has an entry, so none goes unchecked.

bromigos ext validate (in bromigOS) is the full check at install time; this one keeps the
catalog honest without bromigOS's binary.
"""
import json
import os
import py_compile
import re
import subprocess
import sys
import tempfile
import tomllib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# This repository, however the URL spells it: GitHub ignores case, and https, ssh and
# git@ forms, a .git suffix and a trailing / all reach the same place.
HERE = re.compile(r"^(https://|ssh://)?([^@/]*@)?(www\.)?github\.com(:\d+)?[:/]+bromigos-org/extensions(\.git)?/*$",
                  re.IGNORECASE)
CODE = {"live-deck", "widget", "vector-tool", "vector-memory", "homelab-adapter", "command", "hook"}
EXEC = {"command", "hook"}
errors = []


def fail(where, msg):
    errors.append(f"{where}: {msg}")


def load_toml(path, where):
    """The parsed file, or None (with the error recorded) when it isn't valid TOML."""
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
        fail(where, f"not valid TOML: {e}")
        return None


def schema_check(doc, schema_file, where):
    """True when doc has the schema's shape; the checks after it rely on that shape."""
    try:
        import jsonschema
    except ImportError:
        fail(where, "jsonschema isn't installed (pip install jsonschema)")
        return False
    with open(os.path.join(ROOT, "schema", schema_file)) as f:
        schema = json.load(f)
    v = jsonschema.Draft202012Validator(schema)
    found = sorted(v.iter_errors(doc), key=lambda e: [str(p) for p in e.path])
    for e in found:
        fail(where, f"{'/'.join(str(p) for p in e.path) or '(top)'}: {e.message}")
    return not found


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
    m = load_toml(mpath, f"{where} bromigos-ext.toml")
    if m is None or not schema_check(m, "bromigos-ext.schema.json", f"{where} bromigos-ext.toml"):
        return
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
    index = load_toml(os.path.join(ROOT, "index.toml"), "index.toml")
    # The checks below read each entry's fields: only with the schema's shape.
    if index is None or not schema_check(index, "index.schema.json", "index.toml"):
        for err in errors:
            print("ERROR", err)
        print(f"index.toml can't be read, {len(errors)} errors")
        sys.exit(1)
    modes = git_modes()
    seen = set()
    checked = set()
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
        if HERE.match(e.get("url", "").strip()) and not e.get("bundled"):
            if not e.get("path"):
                fail(name, "an entry in this repository needs its path")
            else:
                checked.add(os.path.realpath(os.path.join(ROOT, e["path"])))
                check_example(e, modes)
    examples = os.path.join(ROOT, "examples")
    for d in sorted(os.listdir(examples)) if os.path.isdir(examples) else []:
        p = os.path.join(examples, d)
        if (os.path.isdir(p) or os.path.islink(p)) and os.path.realpath(p) not in checked:
            fail(f"examples/{d}", "no entry in index.toml lists it, so nothing checks it")
    for err in errors:
        print("ERROR", err)
    print(f"{len(entries)} entries, {len(errors)} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
