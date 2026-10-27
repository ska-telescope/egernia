"""skycell's IVOA user-defined functions, through /sync.

skycell only: pg_sphere has none of them, and the capabilities declare none
under it. The epoch propagation is checked against ERFA's ``pmsafe``, an
independent implementation, on the fastest-moving star on the sky; the two
differ by ERFA's light-time correction, which ESA SP-1200's rigorous
propagation leaves out: 0.012 mas in position over these ten years. The
IVOA catalogue of ADQL user-defined functions (Endorsed Note 1.2) gives
examples with answers; its NULL cases come from an uploaded table, ADQL
having no NULL literal, as a catalogue's missing radial velocities would.
"""

import json
import math

import httpx
import psycopg
import pytest
from egernia_core.config import GEOMETRY_BACKENDS, _choose

pytestmark = [
    pytest.mark.component,
    # the backend as the services read it
    pytest.mark.skipif(
        _choose("TAP_GEOMETRY_BACKEND", "pgsphere", GEOMETRY_BACKENDS) != "skycell",
        reason="the user-defined functions are skycell's",
    ),
]

erfa = pytest.importorskip("erfa")

# Barnard's star, Gaia DR3 at J2016.0: deg, mas, mas/yr (pmra * cos dec), km/s
BARNARD = {
    "ra": 269.44850252543836,
    "dec": 4.739420051112412,
    "plx": 546.975939,
    "pmra": -801.551,
    "pmdec": 10362.394,
    "rv": -110.353,
}
_MAS = math.radians(1 / 3_600_000)


def _rows(base_url, query):
    response = httpx.post(
        f"{base_url}/sync",
        data={"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "json", "QUERY": query},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]


def _array(value):
    # an array column arrives as its JSON text for now
    return value if isinstance(value, list) else json.loads(value)


def _erfa(star, epoch0, epoch1):
    """ERFA's propagation, in the units of ivo_epoch_prop."""

    def jd(year):
        return 2451545.0 + (year - 2000.0) * 365.25, 0.0

    dec = math.radians(star["dec"])
    ra1, dec1, pmr1, pmd1, px1, rv1 = erfa.pmsafe(
        math.radians(star["ra"]),
        dec,
        star["pmra"] * _MAS / math.cos(dec),
        star["pmdec"] * _MAS,
        star["plx"] / 1000,
        star["rv"],
        *jd(epoch0),
        *jd(epoch1),
    )
    return (
        math.degrees(ra1),
        math.degrees(dec1),
        px1 * 1000,
        pmr1 / _MAS * math.cos(dec1),
        pmd1 / _MAS,
        rv1,
    )


def _arguments(star):
    return "{ra}, {dec}, {plx}, {pmra}, {pmdec}, {rv}".format(**star)


def _offset_mas(ra, dec, ra_ref, dec_ref):
    return math.hypot((ra - ra_ref) * math.cos(math.radians(dec_ref)), dec - dec_ref) * 3_600_000


def test_epoch_propagation_agrees_with_erfa(tap_service):
    args = _arguments(BARNARD)
    ((position, solution),) = _rows(
        tap_service,
        f"SELECT TOP 1 ivo_epoch_prop_pos({args}, 2016, 2026) AS p,"
        f" ivo_epoch_prop({args}, 2016, 2026) AS sol FROM ska.continuum_sources",
    )
    ra, dec, plx, pmra, pmdec, rv = _erfa(BARNARD, 2016, 2026)
    position, solution = _array(position), _array(solution)
    # the star moved 104 arcsec; the position, as [ra, dec] like a POINT
    assert _offset_mas(*position, ra, dec) < 0.1
    assert _offset_mas(*solution[:2], ra, dec) < 0.1
    assert solution[2] == pytest.approx(plx, abs=0.01)
    assert solution[3] == pytest.approx(pmra, abs=0.05)
    assert solution[4] == pytest.approx(pmdec, abs=0.05)
    assert solution[5] == pytest.approx(rv, abs=0.01)


def test_a_cone_search_on_propagated_positions(tap_service):
    cone = "CIRCLE('ICRS', 62.6, -65.5, 0.6)"
    here = _rows(
        tap_service,
        "SELECT source_id FROM ska.continuum_sources"
        f" WHERE 1 = CONTAINS(POINT('ICRS', ra, dec), {cone}) ORDER BY source_id",
    )
    assert here  # the cone holds sources, so the comparisons below mean something
    # no motion: the propagated positions are where they were
    assert (
        _rows(
            tap_service,
            "SELECT source_id FROM ska.continuum_sources WHERE 1 = CONTAINS("
            f"ivo_epoch_prop_pos(ra, dec, 0, 0, 2016, 2026), {cone}) ORDER BY source_id",
        )
        == here
    )
    # 400 arcsec/yr northwards for ten years carries them out of the cone
    assert (
        _rows(
            tap_service,
            "SELECT source_id FROM ska.continuum_sources WHERE 1 = CONTAINS("
            f"ivo_epoch_prop_pos(ra, dec, 0, 400000, 2016, 2026), {cone})",
        )
        == []
    )


def test_healpix_index_and_centre_are_inverse(tap_service):
    # NESTED, and a POINT-valued function is a POINT argument
    ((index, centre_index),) = _rows(
        tap_service,
        "SELECT TOP 1 ivo_healpix_index(1, 45, 80),"
        " ivo_healpix_index(10, ivo_healpix_center(10, 12345)) FROM ska.continuum_sources",
    )
    assert (index, centre_index) == (3, 12345)


# The catalogue's ivo_epoch_prop_pos examples (EN 1.2, section "Astrometry"):
# ra, dec, parallax, pmra, pmdec, radial_velocity, ref_epoch, out_epoch, and
# the answer. None is a NULL cell; the last answer the catalogue itself calls
# approximate ("the concrete small parallax has not been fixed normatively").
_CATALOGUE = [
    (
        (7.606083572, 11.79044105, 125, 300, -428.8, 52.51, 2016.0, 1992.25),
        (7.604061404627978, 11.7932703828279),
    ),
    (
        (7.606083572, 11.79044105, 125, 300, -428.8, 52.51, 2016.0, 1875.0),
        (7.594068213694308, 11.807251375203935),
    ),
    (
        (7.606083572, 11.79044105, 125, 300, -428.8, None, 2016.0, 1875.0),
        (7.594079587029898, 11.807235464326332),
    ),
    (
        (7.606083572, 11.79044105, 125, 300, None, None, 2016.0, 1875.0),
        (7.594080321498365, 11.790440798509207),
    ),
    (
        (7.606083572, 11.79044105, None, 300, -428.8, 52.51, 2016.0, 1875.0),
        (7.594079587020846, 11.807235464339055),
    ),
]
_COLUMNS = ("ra", "dec", "plx", "pmra", "pmdec", "rv", "ep0", "ep1", "ra_want", "dec_want")


def _upload(rows):
    fields = '<FIELD name="n" datatype="int"/>' + "".join(
        f'<FIELD name="{name}" datatype="double"/>' for name in _COLUMNS
    )
    body = "".join(
        "<TR>"
        + "".join("<TD/>" if v is None else f"<TD>{v!r}</TD>" for v in (n, *args, *want))
        + "</TR>"
        for n, (args, want) in enumerate(rows, 1)
    )
    return (
        '<?xml version="1.0"?><VOTABLE version="1.4"'
        ' xmlns="http://www.ivoa.net/xml/VOTable/v1.3"><RESOURCE><TABLE>'
        f"{fields}<DATA><TABLEDATA>{body}</TABLEDATA></DATA></TABLE></RESOURCE></VOTABLE>"
    ).encode()


@pytest.fixture(scope="module")
def skycell_version(database_url):
    with psycopg.connect(database_url) as conn:
        row = conn.execute("SELECT extversion FROM pg_extension WHERE extname = 'skycell'")
        version = row.fetchone()
    return tuple(int(part) for part in version[0].split(".")) if version else None


def test_epoch_propagation_gives_the_ivoa_catalogue_answers(tap_service, skycell_version):
    if skycell_version is None or skycell_version < (0, 32):
        pytest.skip(
            f"NULL arguments as the catalogue has them need skycell 0.32 (have {skycell_version})"
        )
    response = httpx.post(
        f"{tap_service}/sync",
        data={
            "LANG": "ADQL",
            "REQUEST": "doQuery",
            "FORMAT": "json",
            "UPLOAD": "ex,param:ex",
            "QUERY": "SELECT n, 3600000000 * DISTANCE(ivo_epoch_prop_pos(u.ra, u.dec, u.plx,"
            " u.pmra, u.pmdec, u.rv, u.ep0, u.ep1), POINT('ICRS', u.ra_want, u.dec_want))"
            " AS off_uas FROM TAP_UPLOAD.ex AS u ORDER BY n",
        },
        files={"ex": ("ex.vot", _upload(_CATALOGUE), "application/x-votable+xml")},
    )
    assert response.status_code == 200, response.text
    rows = response.json()["data"]
    # every example answered (no NULL), within a micro-arcsecond
    assert [n for n, _ in rows] == [1, 2, 3, 4, 5]
    assert all(off is not None and off < 1 for _, off in rows), rows
