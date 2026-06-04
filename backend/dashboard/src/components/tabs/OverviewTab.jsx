import StatsCard from '../shared/StatsCard';
import LoadingSpinner from '../shared/LoadingSpinner';

const PHASES = ['init', 'plan', 'writing', 'generate', 'done'];
const PHASE_LABELS = {
  init: '初始化',
  plan: '规划中',
  writing: '写作中',
  generate: '生成素材',
  done: '已完成',
};

export default function OverviewTab({ project }) {
  if (!project) {
    return <EmptyState text="选择一个项目查看概览" />;
  }

  const { stats = {}, current_episode, total_episodes, phase, title } = project;
  const epPct = total_episodes > 0 ? Math.round((current_episode / total_episodes) * 100) : 0;
  const phaseIdx = PHASES.indexOf(phase);

  return (
    <div className="overview-tab">
      <div className="project-hero">
        <h2 className="project-hero-title">{title || '未命名项目'}</h2>
        <span className={`phase-badge phase-${phase}`}>{PHASE_LABELS[phase] || phase}</span>
      </div>

      <div className="stats-row">
        <StatsCard label="已写集数" value={stats.episodes_written || 0} total={total_episodes} color="#7c3aed" />
        <StatsCard label="已审查" value={stats.episodes_reviewed || 0} color="#06b6d4" />
        <StatsCard label="已生成镜头" value={stats.shots_generated || 0} color="#10b981" />
      </div>

      <div className="progress-section">
        <h3>剧集进度</h3>
        <div className="progress-bar-track">
          <div className="progress-bar-fill" style={{ width: `${epPct}%` }}>
            <span className="progress-label">{epPct}%</span>
          </div>
        </div>
        <p className="progress-text">{current_episode} / {total_episodes} 集</p>
      </div>

      <div className="phase-timeline">
        <h3>当前阶段</h3>
        <div className="phase-steps">
          {PHASES.map((p, i) => (
            <div key={p} className={`phase-step${i <= phaseIdx ? ' done' : ''}${p === phase ? ' current' : ''}`}>
              <div className="phase-dot" />
              <span className="phase-step-label">{PHASE_LABELS[p]}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="meta-section">
        <div className="meta-card">
          <h3>角色 ({project.characters?.length || 0})</h3>
          {project.characters?.length > 0 ? (
            <ul className="meta-list">{project.characters.map((c) => <li key={c}>{c}</li>)}</ul>
          ) : <p className="muted">暂无</p>}
        </div>
        <div className="meta-card">
          <h3>场景 ({project.scenes?.length || 0})</h3>
          {project.scenes?.length > 0 ? (
            <ul className="meta-list">{project.scenes.map((s) => <li key={s}>{s}</li>)}</ul>
          ) : <p className="muted">暂无</p>}
        </div>
      </div>
    </div>
  );
}

function EmptyState({ text }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">&#128466;</div>
      <p>{text}</p>
    </div>
  );
}
