---
type: dashboard
title: Migration routes
updated: "2026-11-09"
---

Each direct ancestor's dated residences (from the `residences` property), oldest ancestors first. Regenerate with `_System/tools/migration.py` after adding residences.

## Country paths at a glance

| Ancestor | Born | Countries |
|---|---|---|
| [[John Smith (1870–1931)]] | 1870 | England → United States |
| [[Tomasz Nowak (1898–1960)]] | 1898 | Poland → United States |

## Routes

### [[John Smith (1870–1931)]]

**England → United States**

```mermaid
%%{init: {"flowchart": {"useMaxWidth": true}}}%%
flowchart LR
  s0["1870<br/>Hollin<br/>England"]
  s1["1895<br/>Millbrook<br/>United States"]
  s0 --> s1
```

### [[Tomasz Nowak (1898–1960)]]

**Poland → United States**

```mermaid
%%{init: {"flowchart": {"useMaxWidth": true}}}%%
flowchart LR
  s0["1898<br/>Lesna<br/>Poland"]
  s1["1921<br/>Millbrook<br/>United States"]
  s0 --> s1
```
