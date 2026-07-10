/**
 * components/HighlightedText.tsx
 * Renders highlighted phrases from the AI analysis safely.
 * SECURITY.md §5: untrusted content is NEVER set as innerHTML.
 * All text is rendered as DOM text nodes via React.
 */

import type { HighlightedPhrase } from '../types/api';

interface HighlightedTextProps {
  phrases: HighlightedPhrase[];
}

export function HighlightedText({ phrases }: HighlightedTextProps) {
  if (!phrases || phrases.length === 0) return null;

  return (
    <section className="highlighted-phrases" aria-label="Highlighted suspicious phrases">
      <h3 className="highlighted-phrases__title mono">Suspicious Phrases</h3>
      {phrases.map((item, i) => (
        <div key={i} className="phrase-item">
          {/*
           * SECURITY.md §5: phrase and explanation come from the LLM,
           * validated by Pydantic, and rendered as text content only.
           * No innerHTML, no dangerouslySetInnerHTML.
           */}
          <p className="phrase-item__phrase mono">&ldquo;{item.phrase}&rdquo;</p>
          <p className="phrase-item__explanation">{item.explanation}</p>
        </div>
      ))}
    </section>
  );
}
