# Codes

## Unreleased

- English search placeholder was German ("Suchen …").
- Security: a code or name of only spaces is refused, and the API caps a code at 255 and a description at 5000 characters (before, any length went into the table).

## 2.2.0

- Gives the standard roles access when a club first switches it on (`role_defaults`, docs/roles.md in hubra-app/hubra): Vorstand Ansehen. Roles without access don't see it; their own data from it stays on their profile. Needs Hubra 0.2.5 or later.

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
