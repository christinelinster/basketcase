// Imports:
// >> React
import { useEffect, useState } from 'react';
// >> Router
import { Routes, Route, useParams, useNavigate } from 'react-router-dom';
// >> Components
import Nav         from './components/Nav';
import LandingPage from './components/LandingPage';
import BasketPage  from './components/BasketPage';
// >> Types
import type { Basket }  from './types/basket';

// Temporary mock data while backend is stubbed:
import { loadBaskets, saveBaskets }                from './lib/mockData';

function App() {
  const [baskets, setBaskets] = useState<Basket[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    setBaskets(loadBaskets());
  }, []);

  const handleCreate = (name: string) => {
    setBaskets((prev) => {
      if (prev.some((b) => b.name === name)) return prev;
      const next = [{ name, created: Date.now() }, ...prev];
      saveBaskets(next);
      return next;
    });
    navigate(`/baskets/${name}`);
  };

  const handleDelete = (name: string) => {
    setBaskets((prev) => {
      const next = prev.filter((b) => b.name !== name);
      saveBaskets(next);
      return next;
    });
    navigate('/');
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)', color: 'var(--color-text)', display: 'flex', flexDirection: 'column' }}>
      <Nav />
      <Routes>
        <Route path="/" 
          element={<LandingPage baskets={baskets} onCreate={handleCreate} />} 
        />

        <Route path="/baskets/:name" 
        element={<BasketDetailRoute onDelete={handleDelete} />} />
      </Routes>
    </div>
  );
}

function BasketDetailRoute({ onDelete }: { onDelete: (name: string) => void }) {
  const { name = '' } = useParams();
  return <BasketPage name={name} onDelete={() => onDelete(name)} />;
}

export default App;
