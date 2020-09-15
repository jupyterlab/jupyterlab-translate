# Release

* Check code before releasing the package.

```bash
pre-commit run -a
check-manifest -v
```

* Bump versions

```bash
bump2version release --tag
bump2version patch
```

* Push commits and tags and CI will build and publish the package.

```bash
git push upstream master
git push upstream --tags
```
