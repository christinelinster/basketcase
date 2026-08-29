// Imports:
// >> React
import { useEffect, useState } from 'react';
// >> Router
import { Routes, Route, useNavigate } from 'react-router-dom';
// >> Components
import Nav         from './components/Nav';
import LandingPage from './components/LandingPage';
import BasketPage  from './components/BasketPage';
// >> Services
import BasketService from './services/BasketService';
  
// LocalStorage
const LS_BASKET_PREFIX = 'basket_'
const stripBasketPrefix = (name: string) => name.slice(LS_BASKET_PREFIX.length)
const addBasketPrefix   = (name: string) => `${LS_BASKET_PREFIX}${name}`

function App() {
  const [ baskets, setBaskets ] = useState<string[]>([]); // Array of Basket names
  const navigate = useNavigate();

  // Load baskets from localStorage on initial render. Note that localStorage can only store data as strings:
  // > localStorage { basket_<name1>: <token1>, basket_<name2>: <token2>, ... }
  useEffect(() => {
    const basketNames = Object.keys(localStorage)
      .filter(key => key.startsWith(LS_BASKET_PREFIX))
      .map(stripBasketPrefix)

    setBaskets(basketNames)
  }, [])

  const handleCreateBasket = async (name: string) => {
    const newBasket = await BasketService.createBasket(name) // STUBBED
    setBaskets(baskets.concat(newBasket.name))
    localStorage.setItem(addBasketPrefix(name), newBasket.token)
    // Display popup confirmation -> Show basket URL, token, and option to navigate to basket.
  };

  const handleDeleteBasket = async (name: string) => {
    await BasketService.deleteBasket(name)  // STUBBED
    setBaskets(baskets.filter(bName => bName !== name))
    localStorage.removeItem(addBasketPrefix(name))

    navigate('/');
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)', color: 'var(--color-text)', display: 'flex', flexDirection: 'column' }}>
      <Nav />
      <Routes>
        <Route path="/" 
          element={<LandingPage baskets={baskets} onCreate={handleCreateBasket} />} 
        />

        <Route path="/baskets/:name" 
          element={<BasketPage onDelete={handleDeleteBasket} />}
        />
      </Routes>
    </div>
  );
}

export default App;