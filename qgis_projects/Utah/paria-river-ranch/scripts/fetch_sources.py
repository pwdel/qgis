"""Download public context with complete feature retrieval and request provenance."""
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'sources'
BBOX = '-112.95,36.95,-111.65,37.97'
SGID = 'https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/'
SERVICES = {
    'trailheads': SGID + 'UtahTrailheads/FeatureServer/0',
    'roads': SGID + 'UtahRoads/FeatureServer/0',
    'state-trails': SGID + 'TrailsAndPathways/FeatureServer/0',
    'usfs-trails': 'https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_TrailNFSPublishWithDataStatus_01/MapServer/0',
    'lidar-coverage': SGID + 'LiDAR_Extents/FeatureServer/0',
}

def get(url, params=None):
    if params:
        url += '?' + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'UtahEquestrianAtlas/1.0 (public GIS research)'})
            with urllib.request.urlopen(req, timeout=90) as r:
                body = r.read()
            return body, url
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))

def js(url, params=None):
    b, u = get(url, params)
    d = json.loads(b)
    if 'error' in d:
        raise RuntimeError((u, d['error']))
    return d, u

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def fetch_features(item):
    name, base = item
    if (OUT / (name + '-request.json')).exists():
        return name, 'using completed snapshot'
    meta, _ = js(base, {'f': 'json'})
    save(OUT / (name + '-service.json'), meta)
    p = {'f': 'json', 'where': '1=1', 'geometry': BBOX,
         'geometryType': 'esriGeometryEnvelope', 'inSR': 4326,
         'spatialRel': 'esriSpatialRelIntersects', 'returnIdsOnly': 'true'}
    ids, query_url = js(base + '/query', p)
    save(OUT / (name + '-ids.json'), ids)
    oid = ids['objectIdFieldName']
    wanted = sorted(ids.get('objectIds') or [])
    features, urls = [], [query_url]
    for start in range(0, len(wanted), 80):
        q = {'f': 'geojson', 'objectIds': ','.join(map(str, wanted[start:start+80])),
             'outFields': '*', 'outSR': 4326, 'returnGeometry': 'true'}
        d, u = js(base + '/query', q)
        if d.get('exceededTransferLimit'):
            raise RuntimeError('truncated ' + name)
        features.extend(d['features'])
        urls.append(u)
    actual = [f['properties'].get(oid, f.get('id')) for f in features]
    assert sorted(actual) == wanted, (name, 'missing/duplicate feature IDs')
    save(OUT / (name + '.geojson'), {'type': 'FeatureCollection', 'features': features})
    save(OUT / (name + '-request.json'), {'urls': urls, 'bbox_wgs84': BBOX,
         'retrieved_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'requested_count': len(wanted), 'received_count': len(features), 'object_id_field': oid})
    return name, len(features)

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(5) as pool:
        for result in pool.map(fetch_features, SERVICES.items()):
            print(result, flush=True)
