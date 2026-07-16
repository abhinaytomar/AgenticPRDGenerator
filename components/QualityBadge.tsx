interface QualityBadgeProps {
  score: number;
  label?: string;
}

export default function QualityBadge({ score, label }: QualityBadgeProps) {
  let colorClass: string;
  if (score >= 90) {
    colorClass = "quality-badge-excellent";
  } else if (score >= 75) {
    colorClass = "quality-badge-good";
  } else if (score >= 60) {
    colorClass = "quality-badge-fair";
  } else {
    colorClass = "quality-badge-poor";
  }

  return (
    <span className={`quality-badge ${colorClass}`}>
      {label && <span className="quality-badge-label">{label}</span>}
      <span className="quality-badge-score">{score}</span>
    </span>
  );
}
