# Release

## Update gettext.js

You will need to install `yarn`.

```bash
yarn run clean:all
yarn install
yarn run build
```

## Make release

* Check code before releasing the package.

```bash
pre-commit run -a
check-manifest -v
```

* Bump versions

```bash
hatch version <new_version>
git commit -m "Bump verison"
git tag <new_tag>
```

* Push commits and tags and CI will build and publish the package.

```bash
git push upstream master
git push upstream --tags
```
