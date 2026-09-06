# The vendor argus image with one file changed inside its war.
#
# argus advertises its endpoints from the capabilities template shipped in
# the war (https://replace.me.com/argus/...). At request time cadc-vosi's
# CapGetAction rewrites only the *host name* — new URL(template protocol,
# request host, path) — so the scheme stays the template's and the port is
# always the scheme's default: CADC deploys behind a TLS terminator on 443.
# With TLS off (the fairness rules) the only address argus can advertise
# correctly is http://<host>/argus on port 80, and the template's scheme
# must say http. Nothing else in the image is touched; the digest below is
# the vendor image's.
FROM images.opencadc.org/caom2/argus:1.0.27@sha256:34a74b237ed48a291533bdaf36484856285b39e0ae02804c96501e96085e7f4b AS vendor

FROM python:3.12-slim AS patch
COPY --from=vendor /usr/share/tomcat/webapps/argus.war /vendor.war
RUN python3 - <<'PY'
import zipfile
with zipfile.ZipFile("/vendor.war") as src, zipfile.ZipFile("/argus.war", "w") as dst:
    for item in src.infolist():
        data = src.read(item)
        if item.filename == "capabilities.xml":
            assert b"https://replace.me.com" in data
            data = data.replace(b"https://replace.me.com", b"http://localhost")
        dst.writestr(item, data)
PY

FROM vendor
COPY --from=patch /argus.war /usr/share/tomcat/webapps/argus.war
