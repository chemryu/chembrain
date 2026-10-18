"""Portable v1 contract shared with ``src/libraryData.ts``.

All entity tables and IDs are required. Papers contain only ID, DOI and authors.
Known chemistry, solutions, stage conditions and evidence locators use explicit
allowlists at every nested object. Unknown numbers/units use explicit null.
Optional bounded technical annotations may be absent or null. Private document
text, arbitrary objects and old paper metadata are not portable library data.

Only JSON values, finite numbers, strings of <=3000 UTF-16 code units and a
serialized UTF-8 package <=5 MB are transferable. Document payload keys are
forbidden recursively. Normalize additionally canonicalizes known chemistry and
merges duplicate DOIs/known structures, preserving evidence and foreign keys.
"""
import copy
import hashlib
import json
import math
import re

KINDS = ('papers', 'chemicals', 'solutions', 'reactions')
_MISSING = object()
# ECMAScript trim/regex whitespace, shared with browser normalizeDoi.
_JS_WHITESPACE = '\t\n\v\f\r \u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff'


def key(namespace, value):
    return namespace + '-' + hashlib.sha256(value.encode()).hexdigest()[:20]


def doi(value):
    if not isinstance(value, str):
        raise ValueError('Invalid DOI')
    value = re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:[' + re.escape(_JS_WHITESPACE) + r']*)', '', value.strip(_JS_WHITESPACE), flags=re.I).lower()
    if not re.fullmatch(r'10\.[0-9]{4,9}/[^' + re.escape(_JS_WHITESPACE) + r'<>?#]+', value):
        raise ValueError('Invalid DOI')
    return value


def _string(value):
    return isinstance(value, str) and len(value.encode('utf-16-le', errors='surrogatepass')) // 2 <= 3000


def _optional_string(value):
    return value is None or _string(value)


def _strings(value):
    return isinstance(value, list) and all(_string(item) for item in value)


def _finite(value):
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _number(value, low=0, high=None):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and _finite(value) and value >= low and (high is None or value <= high))


def _nullable_number(value, low=0, high=None):
    return value is None or _number(value, low, high)


def _compact(value):
    if isinstance(value, dict):
        if any(not isinstance(k, str) for k in value):
            raise ValueError('JSON object keys must be strings')
        if set(value) & {'pdf', 'pages', 'full_text', 'text', 'quote', 'candidate_text', 'svg', 'image', 'base64'}:
            raise ValueError('Document text/images belong in the processor, not the library package')
        for item in value.values():
            _compact(item)
    elif isinstance(value, list):
        for item in value:
            _compact(item)
    elif isinstance(value, str):
        if not _string(value):
            raise ValueError('Text field exceeds compact package limit')
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        if not _finite(value):
            raise ValueError('Numbers must be finite')
    elif value is not None and not isinstance(value, bool):
        raise ValueError('Only JSON values may be transferred')


_ALLOWED = {
    'papers': {'id', 'doi', 'authors'},
    'chemicals': {'id', 'name', 'kind', 'aliases', 'smiles', 'inchikey', 'formula', 'molecular_weight', 'notes'},
    'solutions': {'id', 'solvents', 'solutes', 'concentration', 'concentration_unit'},
    'reactions': {'id', 'name', 'reactants', 'products', 'targets', 'yield_percent', 'yield_basis', 'status', 'steps', 'evidence', 'notes'},
}
_LEGACY_PAPER = {'title', 'journal', 'year', 'notes'}


def _keys(value, allowed):
    if not isinstance(value, dict) or set(value) - allowed:
        raise ValueError('Only explicitly allowed normalized fact fields may be transferred')


def project_legacy_library(data):
    """Explicit non-mutating projection of known old-v1 paper metadata only.

    Callers must preserve the original private local bytes before replacing them.
    This helper does not turn arbitrary/unknown document fields into valid facts.
    """
    if not isinstance(data, dict) or not isinstance(data.get('papers'), list):
        raise ValueError('Expected known legacy-v1 package')
    projected = copy.deepcopy(data)
    for paper in projected['papers']:
        _keys(paper, _ALLOWED['papers'] | _LEGACY_PAPER)
        if ('title' in paper and (not _string(paper['title']) or not paper['title'])
                or 'journal' in paper and not _string(paper['journal'])
                or 'notes' in paper and not _optional_string(paper['notes'])
                or 'year' in paper and paper['year'] is not None and
                (not _number(paper['year'], 1500, 3000) or int(paper['year']) != paper['year'])):
            raise ValueError('Invalid known legacy paper metadata')
        for field in _LEGACY_PAPER:
            paper.pop(field, None)
    return validate(projected)


def _validate(data, *, allow_duplicate_doi=False):
    if not isinstance(data, dict) or isinstance(data.get('schema_version'), bool) or data.get('schema_version') != 1:
        raise ValueError('Expected Chembrain package schema_version 1')
    _compact(data)
    try:
        size = len(json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8'))
    except (TypeError, ValueError, UnicodeError) as error:
        raise ValueError('Use a JSON package') from error
    if size > 5_000_000:
        raise ValueError('Package exceeds 5 MB; split the import')
    if set(data) - {'schema_version', 'generated_at', *KINDS}:
        raise ValueError('Only normalized library fields may be transferred')
    if not _optional_string(data.get('generated_at')):
        raise ValueError('Invalid generated_at metadata')
    ids = {}
    for kind in KINDS:
        if not isinstance(data.get(kind), list):
            raise ValueError('Missing entity table: ' + kind)
        ids[kind] = set()
        for row in data[kind]:
            _keys(row, _ALLOWED[kind])
            identifier = row.get('id') if isinstance(row, dict) else None
            if not _string(identifier) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,120}', identifier) or identifier in ids[kind]:
                raise ValueError('Invalid or duplicate entity ID in ' + kind)
            ids[kind].add(identifier)
    data = copy.deepcopy(data)
    seen = set()
    for p in data['papers']:
        if not _strings(p.get('authors')):
            raise ValueError('Paper DOI and authors are required')
        p['doi'] = doi(p.get('doi'))
        if p['doi'] in seen and not allow_duplicate_doi:
            raise ValueError('Paper DOI must be unique')
        seen.add(p['doi'])
    for c in data['chemicals']:
        if (not _string(c.get('name')) or not c['name'] or c.get('kind') not in ('compound', 'reagent', 'solvent', 'catalyst')
                or not _strings(c.get('aliases'))
                or any(not _optional_string(c.get(f)) for f in ('smiles', 'inchikey', 'formula', 'notes'))
                or not _nullable_number(c.get('molecular_weight'))):
            raise ValueError('Invalid chemical metadata')
    for s in data['solutions']:
        if (not _strings(s.get('solvents')) or any(item not in ids['chemicals'] for item in s['solvents'])
                or not isinstance(s.get('solutes'), list)
                or not _nullable_number(s.get('concentration', _MISSING))
                or not _optional_string(s.get('concentration_unit', _MISSING))):
            raise ValueError('Invalid solution metadata')
        for solute in s['solutes']:
            _keys(solute, {'chemical_id', 'role', 'amount', 'unit'})
            if (not isinstance(solute, dict) or not _string(solute.get('chemical_id'))
                    or solute['chemical_id'] not in ids['chemicals'] or not _string(solute.get('role'))
                    or not _nullable_number(solute.get('amount', _MISSING))
                    or not _optional_string(solute.get('unit', _MISSING))):
                raise ValueError('Invalid solution solute')
    for r in data['reactions']:
        if (not _string(r.get('name')) or not r['name'] or r.get('status') not in ('draft', 'reviewed')
                or any(not _optional_string(r.get(f)) for f in ('notes', 'yield_basis'))
                or any(not _strings(r.get(f)) for f in ('reactants', 'products', 'targets'))
                or not r['reactants'] or not r['products']
                or any(item not in ids['chemicals'] for f in ('reactants', 'products', 'targets') for item in r[f])):
            raise ValueError('Invalid reaction participants')
        if not _nullable_number(r.get('yield_percent', _MISSING), 0, 100):
            raise ValueError('Invalid yield')
        if not isinstance(r.get('steps'), list):
            raise ValueError('Reaction steps must be an array')
        for step in r['steps']:
            _keys(step, {'solution_id', 'temperature', 'time', 'notes'})
            if (not isinstance(step, dict) or not _string(step.get('solution_id'))
                    or step['solution_id'] not in ids['solutions']
                    or any(not _optional_string(step.get(f)) for f in ('temperature', 'time', 'notes'))):
                raise ValueError('Invalid reaction solution/conditions')
        if not isinstance(r.get('evidence'), list) or not r['evidence']:
            raise ValueError('Reaction requires source DOI and PDF page/locator')
        for evidence in r['evidence']:
            _keys(evidence, {'paper_id', 'page', 'locator'})
            page = evidence.get('page') if isinstance(evidence, dict) else None
            if (not isinstance(evidence, dict) or not _string(evidence.get('paper_id'))
                    or evidence['paper_id'] not in ids['papers']
                    or not _number(page, 1) or int(page) != page
                    or not _string(evidence.get('locator')) or not evidence['locator']):
                raise ValueError('Reaction requires source DOI and 1-based PDF page/locator')
    return data


def _checked(data, **options):
    try:
        return _validate(data, **options)
    except (TypeError, KeyError, OverflowError, RecursionError, UnicodeError) as error:
        raise ValueError('Malformed portable package') from error


def validate(data):
    """Validate without mutating the input; return a canonical-DOI clone."""
    return _checked(data)


def normalize(data):
    """Canonical known structures/DOIs, deduplicate and relink all foreign keys."""
    from server.chemistry import describe_molecule
    # Validate shapes before indexing/maps/RDKit; duplicate DOI rows are allowed
    # only here so they can be intentionally merged without losing locators.
    data = _checked(data, allow_duplicate_doi=True)
    paper_map = {}; chemical_map = {}; papers = []; chemicals = []
    for p in data['papers']:
        existing = next((x for x in papers if x['doi'] == p['doi']), None)
        paper_map[p['id']] = existing['id'] if existing else p['id']
        if not existing:
            papers.append(p)
    for c in data['chemicals']:
        if c.get('smiles'):
            c.update(describe_molecule(c['smiles']))
        existing = next((x for x in chemicals if c.get('inchikey') and x.get('inchikey') == c['inchikey']), None)
        chemical_map[c['id']] = existing['id'] if existing else c['id']
        if existing:
            existing['aliases'] = list(dict.fromkeys(existing['aliases'] + c['aliases'] + ([c['name']] if c['name'] != existing['name'] else [])))
        else:
            chemicals.append(c)
    for s in data['solutions']:
        s['solvents'] = [chemical_map[x] for x in s['solvents']]
        for solute in s['solutes']:
            _keys(solute, {'chemical_id', 'role', 'amount', 'unit'})
            solute['chemical_id'] = chemical_map[solute['chemical_id']]
    for r in data['reactions']:
        for field in ('reactants', 'products', 'targets'):
            r[field] = [chemical_map[x] for x in r[field]]
        for evidence in r['evidence']:
            evidence['paper_id'] = paper_map[evidence['paper_id']]
    data['papers'] = papers; data['chemicals'] = chemicals
    return validate(data)
