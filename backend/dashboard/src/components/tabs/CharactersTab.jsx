import { useState } from 'react';
import LoadingSpinner from '../shared/LoadingSpinner';
import ImageModal from '../shared/ImageModal';

export default function CharactersTab({ project }) {
  const [selectedChar, setSelectedChar] = useState(null);
  const [modalSrc, setModalSrc] = useState(null);

  if (!project) {
    return <div className="empty-state"><div className="empty-icon">&#128100;</div><p>选择一个项目查看角色</p></div>;
  }

  const characters = project.assets?.characters || {};

  if (Object.keys(characters).length === 0) {
    return <div className="empty-state"><div className="empty-icon">&#128100;</div><p>暂无角色素材，先生成角色四视图</p></div>;
  }

  return (
    <div className="characters-tab">
      <div className="characters-grid">
        {Object.entries(characters).map(([name, data]) => {
          const variants = data.variants || [];
          const baseVariant = variants.find((v) => v.is_base) || variants[0];
          const thumbnailUrl = baseVariant?.tos_url || baseVariant?.local_path || '';

          return (
            <button
              key={name}
              className={`character-card${selectedChar === name ? ' selected' : ''}`}
              onClick={() => setSelectedChar(selectedChar === name ? null : name)}
            >
              <div className="character-card-img">
                {thumbnailUrl ? (
                  <img src={thumbnailUrl} alt={name} loading="lazy" />
                ) : (
                  <div className="character-card-placeholder">?</div>
                )}
              </div>
              <div className="character-card-name">{name}</div>
              <div className="character-card-count">{variants.length} 套着装</div>
            </button>
          );
        })}
      </div>

      {selectedChar && (
        <CharacterDetail
          name={selectedChar}
          data={characters[selectedChar]}
          onImageClick={(url) => setModalSrc(url)}
        />
      )}

      {modalSrc && <ImageModal src={modalSrc} alt={selectedChar} onClose={() => setModalSrc(null)} />}
    </div>
  );
}

function CharacterDetail({ name, data, onImageClick }) {
  const variants = data.variants || [];
  return (
    <div className="character-detail">
      <h3>{name} · 着装版本</h3>
      <div className="variant-grid">
        {variants.map((v) => (
          <div key={v.outfit} className="variant-card">
            <div
              className="variant-img"
              onClick={() => onImageClick(v.tos_url || v.local_path)}
            >
              {(v.tos_url || v.local_path) ? (
                <img src={v.tos_url || v.local_path} alt={v.outfit} loading="lazy" />
              ) : (
                <div className="character-card-placeholder">?</div>
              )}
            </div>
            <div className="variant-label">
              <span>{v.outfit}</span>
              {v.is_base && <span className="base-tag">基础</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
