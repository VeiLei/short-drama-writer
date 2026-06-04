export default function StatsCard({ label, value, total, color = '#7c3aed' }) {
  return (
    <div className="stats-card">
      <div className="stats-value" style={{ color }}>{value}</div>
      {total != null && <div className="stats-total">/ {total}</div>}
      <div className="stats-label">{label}</div>
    </div>
  );
}
