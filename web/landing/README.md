# FNP-QNN Public Landing Page

Public URL: https://fnpqnn.securedme.ca/
Public email: fnpqnn@securedme.ca
Public repository: https://github.com/SeCuReDmE-main-dev/FNP-QNN-MVP

## File Layout

```text
web/landing/
├── index.html
├── fnp-qnn-landing.css
├── favicon.svg
├── robots.txt
└── README.md
```

Generated local deployment package:

```text
dist/fnpqnn-public/
├── index.html
├── fnp-qnn-landing.css
├── favicon.svg
└── robots.txt
```

## Hosting Requirements

The page is fully static HTML, CSS, and SVG. It does not require JavaScript, Node, a CDN framework, external fonts, analytics, cookies, or a backend service.

Expected cPanel document root:

```text
/home/xacm7978/fnpqnn.securedme.ca
```

Verify this path before deployment. If it does not exist, stop and confirm the correct document root in cPanel.

## Deployment Steps

1. Build or refresh the local package:

```powershell
New-Item -ItemType Directory -Force .\dist\fnpqnn-public
Copy-Item .\web\landing\index.html .\dist\fnpqnn-public\index.html -Force
Copy-Item .\web\landing\fnp-qnn-landing.css .\dist\fnpqnn-public\fnp-qnn-landing.css -Force
Copy-Item .\web\landing\favicon.svg .\dist\fnpqnn-public\favicon.svg -Force
Copy-Item .\web\landing\robots.txt .\dist\fnpqnn-public\robots.txt -Force
Compress-Archive -Path .\dist\fnpqnn-public\* -DestinationPath .\dist\fnpqnn-public.zip -Force
Get-FileHash .\dist\fnpqnn-public.zip -Algorithm SHA256
```

2. In cPanel File Manager, open the verified document root.
3. Back up the current files before replacing anything.
4. Upload only these files:

```text
index.html
fnp-qnn-landing.css
favicon.svg
robots.txt
```

5. Do not overwrite `.htaccess`, mail configuration, DNS configuration, credentials, or unrelated files.

## Backup Steps

Before replacing files on a shell-enabled host:

```bash
TARGET="/home/xacm7978/fnpqnn.securedme.ca"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP="/home/xacm7978/fnpqnn.securedme.ca_backup_${STAMP}"
mkdir -p "$BACKUP"
cp -a "$TARGET"/. "$BACKUP"/
```

Then copy only the static public files and set permissions:

```bash
cp dist/fnpqnn-public/index.html "$TARGET/index.html"
cp dist/fnpqnn-public/fnp-qnn-landing.css "$TARGET/fnp-qnn-landing.css"
cp dist/fnpqnn-public/favicon.svg "$TARGET/favicon.svg"
cp dist/fnpqnn-public/robots.txt "$TARGET/robots.txt"
chmod 755 "$TARGET"
chmod 644 "$TARGET/index.html" "$TARGET/fnp-qnn-landing.css" "$TARGET/favicon.svg" "$TARGET/robots.txt"
```

## Smoke Tests

Local preview:

```powershell
python -m http.server 8765 --directory web/landing
curl.exe -I http://127.0.0.1:8765/
curl.exe -I http://127.0.0.1:8765/fnp-qnn-landing.css
curl.exe -s http://127.0.0.1:8765/ | Select-String "FNP-QNN|fnpqnn.securedme.ca|fnpqnn@securedme.ca|FNP-QNN-MVP|non-clinical"
```

Live smoke test after real deployment:

```bash
curl -I http://fnpqnn.securedme.ca/
curl -I https://fnpqnn.securedme.ca/
curl -I https://fnpqnn.securedme.ca/fnp-qnn-landing.css
curl -I https://fnpqnn.securedme.ca/favicon.svg
curl -I https://fnpqnn.securedme.ca/robots.txt
curl -s https://fnpqnn.securedme.ca/ | grep -E "FNP-QNN|fnpqnn@securedme.ca|FNP-QNN-MVP|non-clinical|i_fractal"
```

## Public Boundary

FNP-QNN is an alpha-local educational research simulator. It is not clinical, diagnostic, therapeutic, emergency, safety-critical, or production-public software. Results are local simulation evidence only.

Never include secrets, tokens, private corpora, private evidence, environment values, unpublished material, or local machine paths in this public landing page package.
