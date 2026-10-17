"""Record public-provider connectivity separately from deterministic validation.

This is an observation, not a replacement for tests. Unreachable upstreams stay
UNAVAILABLE and must be reported honestly. No credentials are requested; at most
one independently license-verified public PDF is checked in temporary storage.
"""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from server.jacs_collection import CrossrefClient, ISSNS, canonical_doi, _licensed_pdf, _save_pdf
from server.store import Store


def main():
    result = {'status':'UNAVAILABLE','provider':'Crossref','journal':'JACS','requested_pdfs':False}
    try:
        start = (datetime.now(timezone.utc) - timedelta(days=14)).date().isoformat()
        response = CrossrefClient().page(start, '*')
        items = response.get('items')
        if not isinstance(items,list):
            raise ValueError('Provider returned invalid items')
        for paper in items:
            assert ISSNS.intersection(paper.get('ISSN',[]))
            assert canonical_doi(paper['DOI']).startswith('10.1021/')
        result.update(status='PASS', articles_observed=len(items), first_doi=items[0]['DOI'] if items else None)
        candidates = [(paper, _licensed_pdf(paper,datetime.now(timezone.utc))) for paper in items]
        candidates = [(paper,candidate) for paper,candidate in candidates if candidate]
        result['verified_oa_pdf_links'] = len(candidates)
        result['live_pdf'] = 'NO_VERIFIED_LINK_IN_OBSERVED_PAGE'
        if candidates:
            paper,candidate = candidates[0]
            try:
                pdf = CrossrefClient().pdf(candidate)
                with tempfile.TemporaryDirectory(prefix='Chembrain public PDF probe ') as temporary:
                    _save_pdf(Store(Path(temporary)),canonical_doi(paper['DOI']),pdf,candidate,'probe',datetime.now(timezone.utc).isoformat())
                result.update(live_pdf='PASS', live_pdf_bytes=len(pdf), requested_pdfs=True)
            except Exception as error:
                result.update(live_pdf='UNAVAILABLE', live_pdf_reason=type(error).__name__, requested_pdfs=True)
        if len(sys.argv) == 2:
            with tempfile.TemporaryDirectory(prefix='Chembrain JACS metadata probe ') as temporary:
                data_dir = Path(temporary) / 'data'
                execution = subprocess.run([str(Path(sys.argv[1]).resolve()),'--sync-jacs','--metadata-only',
                                            '--days','14','--max-pages','1','--data-dir',str(data_dir)],
                                           capture_output=True,text=True,timeout=180)
                collected = json.loads(execution.stdout.strip().splitlines()[-1])
                if collected.get('metadata_only') is not True or collected.get('status') not in ('success','partial'):
                    raise ValueError('Packaged collection did not return a metadata result')
                with sqlite3.connect(data_dir / 'chembrain.sqlite3') as database:
                    imported = database.execute("SELECT COUNT(*) FROM records WHERE kind='source'").fetchone()[0]
                cli_state = 'UPSTREAM_UNAVAILABLE' if not collected.get('discovered') and collected.get('errors') else 'PASS'
                result.update(packaged_cli=cli_state, imported_references=imported, bounded_collection_status=collected['status'])
                if collected.get('discovered',0) and not imported:
                    raise ValueError('Packaged collection did not save its discovered references')
                if list(data_dir.glob('jacs_pdfs/*.pdf')):
                    raise ValueError('Metadata-only observation downloaded a PDF')
    except (AssertionError, ValueError, KeyError, TypeError, IndexError) as error:
        result.update(status='INVALID_RESPONSE', reason=type(error).__name__)
    except Exception as error:
        result['reason'] = type(error).__name__
    Path('jacs-gateway.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__ == '__main__':
    main()
