import { useState, useCallback } from 'react';
import Layout from './components/Layout';
import OverviewTab from './components/tabs/OverviewTab';
import CharactersTab from './components/tabs/CharactersTab';
import EpisodesTab from './components/tabs/EpisodesTab';
import AssetsTab from './components/tabs/AssetsTab';

const TABS = [
  { key: 'overview',    label: '概览', badge: 'OV' },
  { key: 'characters',  label: '角色', badge: 'CH' },
  { key: 'episodes',    label: '剧集', badge: 'EP' },
  { key: 'assets',      label: '素材', badge: 'AS' },
];

const PHASE_LABEL = {
  init: 'INITIALIZED', plan: 'PLANNING', writing: 'WRITING',
  generate: 'GENERATING', done: 'COMPLETED',
};

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedProject, setSelectedProject] = useState(null);

  const handleSelectProject = useCallback((project) => {
    setSelectedProject(project);
  }, []);

  const renderTab = () => {
    const key = `${activeTab}-${selectedProject?.path || 'none'}`;
    switch (activeTab) {
      case 'overview':    return <OverviewTab key={key} project={selectedProject} />;
      case 'characters':  return <CharactersTab key={key} project={selectedProject} />;
      case 'episodes':    return <EpisodesTab key={key} project={selectedProject} />;
      case 'assets':      return <AssetsTab key={key} project={selectedProject} />;
      default:            return null;
    }
  };

  return (
    <Layout
      sidebar={
        <>
          <div className="sidebar-brand">
            <div className="sidebar-logo" />
            <div>
              <div className="sidebar-title">短剧工坊</div>
              <div className="sidebar-subtitle">Production Suite</div>
            </div>
          </div>

          <hr className="sidebar-divider" />

          <nav className="sidebar-nav">
            {TABS.map((tab) => (
              <button
                key={tab.key}
                className={`nav-item${activeTab === tab.key ? ' active' : ''}`}
                onClick={() => setActiveTab(tab.key)}
              >
                {tab.label}
                <span className="nav-badge">{tab.badge}</span>
              </button>
            ))}
          </nav>

          <div className="sidebar-footer">
            <div className="project-info">
              {selectedProject ? (
                <>
                  <div className="project-name">{selectedProject.title}</div>
                  <div className="project-phase">
                    {PHASE_LABEL[selectedProject.phase] || selectedProject.phase}
                  </div>
                </>
              ) : (
                <div className="project-name muted">未选择项目</div>
              )}
            </div>
          </div>
        </>
      }
    >
      <div className="tab-header">
        <h1>{TABS.find((t) => t.key === activeTab)?.label}</h1>
        <div className="project-selector-wrapper">
          <ProjectSelectorInline onSelect={handleSelectProject} selected={selectedProject} />
        </div>
      </div>
      {renderTab()}
    </Layout>
  );
}

function ProjectSelectorInline({ onSelect, selected }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useState(() => {
    import('./api').then(({ fetchOverview }) => {
      fetchOverview()
        .then((data) => setProjects(data.projects || []))
        .catch(() => {})
        .finally(() => setLoading(false));
    });
  }, []);

  useState(() => {
    if (projects.length > 0 && !selected) {
      onSelect(projects[0]);
    }
  }, [projects, selected, onSelect]);

  if (loading) return <span className="muted">加载项目...</span>;
  if (projects.length === 0) return <span className="muted">未找到项目</span>;

  return (
    <select
      className="project-select"
      value={selected?.path || ''}
      onChange={(e) => {
        const p = projects.find((p) => p.path === e.target.value);
        if (p) onSelect(p);
      }}
    >
      {projects.map((p) => (
        <option key={p.path} value={p.path}>
          {p.title}
        </option>
      ))}
    </select>
  );
}
