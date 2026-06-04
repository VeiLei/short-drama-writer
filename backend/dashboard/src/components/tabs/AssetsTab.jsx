import { useState, useMemo } from 'react';
import ImageModal from '../shared/ImageModal';

const FILTERS = [
  { key: 'all', label: '全部' },
  { key: 'character_base', label: '角色基础' },
  { key: 'character_variant', label: '角色变装' },
  { key: 'scene_master', label: '场景全景' },
  { key: 'shot_frame', label: '取景框' },
];

export default function AssetsTab({ project }) {
  const [filter, setFilter] = useState('all');
  const [modalSrc, setModalSrc] = useState(null);

  if (!project) {
    return <div className="empty-state"><div className="empty-icon">&#128247;</div><p>选择一个项目查看素材</p></div>;
  }

  const assets = useMemo(() => {
    const items = [];
    const chars = project.assets?.characters || {};
    const scenes = project.assets?.scenes || {};

    for (const [name, data] of Object.entries(chars)) {
      for (const v of (data.variants || [])) {
        const url = v.tos_url || v.local_path;
        if (url) {
          items.push({
            type: v.is_base ? 'character_base' : 'character_variant',
            label: `${name} · ${v.outfit}`,
            url,
            created: v.created_at,
          });
        }
      }
    }

    for (const [name, data] of Object.entries(scenes)) {
      if (data.master?.tos_url || data.master?.local_path) {
        items.push({
          type: 'scene_master',
          label: `${name} · 全景`,
          url: data.master.tos_url || data.master.local_path,
          created: data.master.created_at,
        });
      }
      for (const f of (data.shot_frames || [])) {
        const url = f.tos_url || f.local_path;
        if (url) {
          items.push({
            type: 'shot_frame',
            label: `${name} · ${f.frame_id}`,
            url,
            created: f.created_at,
          });
        }
      }
    }

    return items;
  }, [project]);

  const filtered = filter === 'all' ? assets : assets.filter((a) => a.type === filter);

  if (assets.length === 0) {
    return <div className="empty-state"><div className="empty-icon">&#128247;</div><p>暂无素材，先生成图片吧</p></div>;
  }

  return (
    <div className="assets-tab">
      <div className="assets-summary">
        <span>{assets.length} 个素材</span>
      </div>
      <div className="asset-filters">
        {FILTERS.map((f) => (
          <button
            key={f.key}
            className={`filter-btn${filter === f.key ? ' active' : ''}`}
            onClick={() => setFilter(f.key)}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="image-grid">
        {filtered.map((item, i) => (
          <button key={i} className="image-grid-item" onClick={() => setModalSrc(item.url)}>
            <img src={item.url} alt={item.label} loading="lazy" />
            <div className="image-grid-label">{item.label}</div>
          </button>
        ))}
      </div>

      {modalSrc && <ImageModal src={modalSrc} onClose={() => setModalSrc(null)} />}
    </div>
  );
}
