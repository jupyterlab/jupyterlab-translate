# Release

## Update gettext.js

```bash
rm package-lock.json
rm -rf node_modules/
npm install gettext-extract
npm install @vercel/ncc -g
ncc build node_modules/gettext-extract/bin/gettext-extract -o jupyterlab_translate --minify
rm -rf jupyterlab_translate/typescript
```

## Make release

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
