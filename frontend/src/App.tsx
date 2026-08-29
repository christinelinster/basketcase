import { useEffect, useState } from 'react';
import type { Basket } from './types/basket';
import { loadBaskets, saveBaskets } from './lib/mockData';
import Nav from './components/Nav';
import LandingPage from './components/LandingPage';
import BasketDetailPage from './components/BasketDetailPage';

function getRoute(): string {
  return (window.location.hash || '#/').replace(/^#\/?/, '');
}

function App() {
  const [route, setRoute] = useState(getRoute());
  const [baskets, setBaskets] = useState<Basket[]>([]);

  useEffect(() => {
    setBaskets(loadBaskets());
    const onHashChange = () => setRoute(getRoute());
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  const handleCreate = (name: string) => {
    setBaskets((prev) => {
      if (prev.some((b) => b.name === name)) return prev;
      const next = [{ name, created: Date.now() }, ...prev];
      saveBaskets(next);
      return next;
    });
    window.location.hash = `#/${name}`;
  };

  const handleDelete = () => {
    setBaskets((prev) => {
      const next = prev.filter((b) => b.name !== route);
      saveBaskets(next);
      return next;
    });
    window.location.hash = '#/';
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)', color: 'var(--color-text)', display: 'flex', flexDirection: 'column' }}>
      <Nav />
      {route ? (
        <BasketDetailPage name={route} onDelete={handleDelete} />
      ) : (
        <LandingPage baskets={baskets} onCreate={handleCreate} />
      )}
    </div>
  );
}

export default App;
