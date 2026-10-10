# Security

This page says how to report a security problem in the bromigOS extension catalog, and
what happens after you do. Please report it privately, so it can be fixed before anyone
else hears about it.

`bromigos ext search` and `bromigos ext install NAME` read this catalog, so what it lists
reaches every bromigOS desktop. An extension that runs code shows its declared
permissions before it installs, and you decide. A way to get code onto a desktop without
that step is a security problem.

## Report a problem

Don't open a public issue for a security problem. Use one of these instead:

- **GitHub's private report.** Open the repository's **Security** tab and choose **Report
  a vulnerability**. Only the maintainers see it.
- **Email.** Write to contact@bromigos.org with "Security" at the start of the subject.

Security problems here include:

- a listed extension that does something harmful, or something its permissions don't
  declare;
- a listing whose `url` or `ref` has been taken over, or now points somewhere else;
- a way past the catalog check (`tools/check.py`) or the schemas in `schema/`;
- a problem in one of the examples in `examples/`.

Tell us:

- the extension's name and the catalog entry, or the file in this repository;
- the version of bromigOS, from `pacman -Q bromigos`;
- how to reproduce the problem, step by step;
- what an attacker could do with it.

Leave out anything private, such as your hostnames, addresses or tokens. We don't need
them.

## What happens next

We reply to say we have your report. We tell you whether we can reproduce the problem,
and we keep you posted until it's fixed. A harmful listing comes out of `index.toml`
first, and we look at the rest after. When the fix ships, we credit you, unless you'd
rather we didn't.

Please give us a fair chance to ship a fix before you tell anyone else.

## What this covers

- This repository: the catalog, its schemas and check, the examples and the previews.
- An extension listed from another repository belongs to its author. We can take its
  listing out of the catalog; to get its code fixed, report it to its author too.
- The `bromigos ext` command and the rest of the desktop live in
  [bromigos-org/bromigOS](https://github.com/bromigos-org/bromigOS). Report a problem
  there the same way.
