const BASE = '/api';

async function request(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }
  return res.json();
}

export function fetchOverview(projectsRoot = '') {
  const params = projectsRoot ? `?projects_root=${encodeURIComponent(projectsRoot)}` : '';
  return request(`/projects/overview${params}`);
}

export function fetchAssets(projectRoot = '') {
  const params = projectRoot ? `?project_root=${encodeURIComponent(projectRoot)}` : '';
  return request(`/generate/assets${params}`);
}
