# Codes

A [Hubra](https://hubra.club) plugin for door codes, lock combinations and
passcodes. Each code is stored encrypted with the club's own key, shown
masked until someone with the right clicks the eye, and can be copied with
one click.

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
`CHANGELOG.md`, merge, then publish a GitHub release tagged `v<version>`.
The workflow tests, signs (after approval in the `plugin-signing`
environment) and attaches `codes-<version>.zip`.
