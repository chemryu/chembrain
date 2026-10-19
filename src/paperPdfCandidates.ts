/** Private, unverified pointers from an open PDF. Nothing here is a chemical fact. */
export interface SmilesCandidate {
  notation: string;
  page: number;
  /** One-based line in extracted page text, not a claim about printed line numbers. */
  line: number;
}

export interface DoiCandidate {
  doi: string;
  page: number;
  line: number;
}

export interface PaperCandidates {
  smiles: SmilesCandidate[];
  dois: DoiCandidate[];
  truncated: boolean;
}

const MAX_TEXT = 500_000;
const MAX_CANDIDATES = 100;
const MAX_NOTATION = 3_000;

/**
 * Recognize explicit SMILES labels and DOI strings only. A name, compound number,
 * scheme position, or document instruction cannot become a molecule or edge.
 * The caller must still validate the notation and explicitly review its identity.
 */
export function extractCandidates(text: string, page: number): PaperCandidates {
  if (!Number.isSafeInteger(page) || page < 1) throw new Error('A source page must be a positive integer.');
  const result: PaperCandidates = { smiles: [], dois: [], truncated: text.length > MAX_TEXT };
  const lines = text.slice(0, MAX_TEXT).replace(/\r\n?/g, '\n').split('\n');
  const seenSmiles = new Set<string>();
  const seenDoi = new Set<string>();
  for (let index = 0; index < lines.length; index++) {
    const line = lines[index];
    // Whitespace terminates notation. Wrapped strings are never silently joined.
    const marker = /\b(?:canonical\s+|isomeric\s+)?SMILES(?:\s*\((?:canonical|isomeric)\))?\s*[:=]\s*["'`]?([^\s"'`]+)/gi;
    for (const match of line.matchAll(marker)) {
      const notation = match[1];
      if (notation.length > MAX_NOTATION) { result.truncated = true; continue; }
      if (!notation || !/^[A-Za-z0-9@+\-\[\]()\\/%=#.*:]+$/.test(notation)) continue;
      const key = `${index}:${notation}`;
      if (!seenSmiles.has(key)) {
        if (result.smiles.length >= MAX_CANDIDATES) { result.truncated = true; break; }
        seenSmiles.add(key);
        result.smiles.push({ notation, page, line: index + 1 });
      }
    }
    const doiPattern = /\b10\.\d{4,9}\/[-._;()/:A-Z0-9]+/gi;
    for (const match of line.matchAll(doiPattern)) {
      let doi = match[0].replace(/[.,;:]+$/, '');
      // Citation punctuation may close a surrounding parenthesis, while a DOI
      // itself can legitimately contain balanced parentheses.
      while (doi.endsWith(')') && (doi.match(/\)/g)?.length ?? 0) > (doi.match(/\(/g)?.length ?? 0)) doi = doi.slice(0, -1);
      doi = doi.toLowerCase();
      if (doi.length > 200 || doi.endsWith('/')) continue;
      const key = `${index}:${doi}`;
      if (!seenDoi.has(key)) {
        if (result.dois.length >= MAX_CANDIDATES) { result.truncated = true; break; }
        seenDoi.add(key);
        result.dois.push({ doi, page, line: index + 1 });
      }
    }
  }
  return result;
}
