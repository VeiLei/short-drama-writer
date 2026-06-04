export default function EpisodesTab({ project }) {
  if (!project) {
    return <div className="empty-state"><div className="empty-icon">&#128196;</div><p>选择一个项目查看剧集</p></div>;
  }

  const { stats = {}, current_episode, total_episodes } = project;
  const written = stats.episodes_written || 0;

  const episodes = [];
  for (let i = 1; i <= Math.max(written, current_episode); i++) {
    episodes.push({
      number: i,
      title: i <= written ? `第${String(i).padStart(4, '0')}集` : '',
      status: i <= written ? 'written' : i <= current_episode ? 'draft' : 'pending',
    });
  }

  if (episodes.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-icon">&#128196;</div>
        <p>暂无剧集，开始写作吧</p>
      </div>
    );
  }

  return (
    <div className="episodes-tab">
      <div className="episode-summary">
        <span>共 {total_episodes} 集计划 · 已完成 {written} 集 · 当前第 {current_episode || 0} 集</span>
      </div>
      <div className="episode-list">
        {episodes.map((ep) => (
          <div key={ep.number} className={`episode-row episode-${ep.status}`}>
            <div className="episode-number">{ep.number}</div>
            <div className="episode-meta">
              <div className="episode-title">{ep.title || `第${String(ep.number).padStart(4, '0')}集`}</div>
              <span className={`status-tag status-${ep.status}`}>
                {ep.status === 'written' ? '已写' : ep.status === 'draft' ? '草稿' : '待写'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
