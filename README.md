# Codes

[![Test and release](https://github.com/hubra-app/hubra-plugin-codes/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/hubra-app/hubra-plugin-codes/actions/workflows/release.yml?query=branch%3Amain) [![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-bitsandbricks-ffdd00?logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/bitsandbricks)

> **Moving into Keys.** From Keys 1.4 a code is a key of the kind "code"
> (encrypted, assignable to members and groups, in the inventory). Keys takes
> this plugin's codes over by itself through the query `codes.codes.export`;
> once they show up in the inventory, switch Codes off and uninstall it.

A [Hubra](https://hubra.club) plugin for door codes, lock combinations and
passcodes. Each code is stored encrypted with the club's own key, never
sent in a list: someone with the right clicks the eye (or copy) to fetch one
code, and every such reveal is in the audit log with who saw which code.

**Plugin id** `codes` · **Package** `hubra_codes` · **Module** `codes` · **Works with** Hubra `>=0.2,<1` (the version without the built-in Codes module)

## Moving from the built-in module

Codes was part of Hubra itself until it moved out
([hubra-app/hubra#171](https://github.com/hubra-app/hubra/pull/171)). The
plugin keeps everything the same, so nothing has to be migrated by hand:

- the module code `codes`, so clubs that had it on keep it on;
- the table `codes` and its rows;
- the API path `/api/v1/codes`;
- the permissions `codes.codes.read/create/update/delete`, so roles keep them;
- the club-app page `/app/operations/codes` (under **Weitere**).

The migration creates the table only where it does not exist yet. Codes are
still re-encrypted when the club key or `FERNET_KEY` is rotated, because the
plugin declares its encrypted column, and Hubra keeps rotating the column
even while the plugin is not installed.

[hubra-plugin-keys](https://github.com/hubra-app/hubra-plugin-keys) links a
key to a code when both plugins are on.

## Layout

```
plugin.yaml              # id, version, Hubra range, package, modules
hubra_codes/             # Module, model, schemas, service, routes
migrations/              # creates the codes table where it is missing
frontend/src/            # the Codes page, its API calls and translations
tests/                   # runs with Hubra's pytest fixtures
```

## Develop

Clone into `plugins/codes` of a Hubra checkout:

```
cd hubra/app/backend
pytest ../../plugins/codes
cd ../frontend
npm run typecheck:plugins
npm run build:plugin -- ../../plugins/codes
```

## Release

Bump `version` in `plugin.yaml`, add a `## <version>` section to
`CHANGELOG.md` and merge. Then tag the merged commit on main and push the tag:

```sh
git switch main && git pull
git tag v<version> && git push origin v<version>
```

The workflow tests the plugin and builds its frontend, the `plugin-signing`
job signs it after your approval, and only then is the GitHub release
`v<version>` published, with `codes-<version>.zip` and its `.sha256` attached. Files
listed in `.releaseignore` stay out of the zip. Releases are immutable, so a
published version never changes: fix a bad one with a new version.