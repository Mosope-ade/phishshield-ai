/**
 * components/RecommendationsList.tsx
 * Renders the AI-generated recommendations.
 * SECURITY.md §5: content rendered as text nodes only.
 */

interface RecommendationsListProps {
  recommendations: string[];
}

export function RecommendationsList({ recommendations }: RecommendationsListProps) {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <section className="recommendations" aria-label="Safety recommendations">
      <h3 className="recommendations__title mono">Recommendations</h3>
      <ul className="recommendations__list">
        {recommendations.map((rec, i) => (
          <li key={i} className="recommendations__item">
            {/* SECURITY.md §5: text content only, no HTML */}
            {rec}
          </li>
        ))}
      </ul>
    </section>
  );
}
