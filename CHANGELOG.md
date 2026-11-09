# Codes

## 2.1.2

2.1.1 was tagged but couldn't be signed, so it was never released. 2.1.2 is the same plugin, signed. What it brings:

- Codes move into the Keys plugin: there a code is a key of the kind
  "code", stored encrypted, assignable to several members and groups (or
  public), shown in the inventory with the club's keys and on the account
  page of whoever it is assigned to. Keys 1.4 takes the codes over through
  the new query `codes.codes.export` (clear text, needs `codes.codes.read`
  or the system) within a few minutes; after that, switch Codes off and
  uninstall it.
- plugin.yaml lists the areas it uses (`uses:`).

## 2.1.1

2.1.0 was tagged but couldn't be signed, so it was never released. 2.1.1 is the same plugin, signed. What 2.1.0 brings:

- Codes move into the Keys plugin: there a code is a key of the kind
  "code", stored encrypted, assignable to several members and groups (or
  public), shown in the inventory with the club's keys and on the account
  page of whoever it is assigned to. Keys 1.4 takes the codes over through
  the new query `codes.codes.export` (clear text, needs `codes.codes.read`
  or the system) within a few minutes; after that, switch Codes off and
  uninstall it.
- plugin.yaml lists the areas it uses (`uses:`).

## 2.1.0

- Codes move into the Keys plugin: there a code is a key of the kind
  "code", stored encrypted, assignable to several members and groups (or
  public), shown in the inventory with the club's keys and on the account
  page of whoever it is assigned to. Keys 1.4 takes the codes over through
  the new query `codes.codes.export` (clear text, needs `codes.codes.read`
  or the system) within a few minutes; after that, switch Codes off and
  uninstall it.
- plugin.yaml lists the areas it uses (`uses:`).

## 2.0.1

The first release of the plugin. The v2.0.0 tag was set on the repository's
starting commit (the template's example), so it never built; 2.0.1 is the
Codes plugin described under 2.0.0, unchanged.

## 2.0.0

Codes is now a plugin instead of a part of Hubra. Clubs keep their codes,
their module switch and their roles: the table, the API and the permissions
are the same as before.
