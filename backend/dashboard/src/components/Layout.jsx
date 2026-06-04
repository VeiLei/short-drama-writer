export default function Layout({ sidebar, children }) {
  return (
    <div className="app-layout">
      <aside className="sidebar">{sidebar}</aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
