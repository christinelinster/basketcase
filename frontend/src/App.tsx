// Imports:
// >> React
import { useEffect, useState } from 'react';
// >> Router
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
// >> Components
import Nav         from './components/Nav';
import LandingPage from './components/LandingPage';
import BasketPage  from './components/BasketPage';
// >> Services
import BasketService from './services/BasketService';
import type { CreatedBasket } from './types/basket';
  
// LocalStorage
const LS_BASKET_PREFIX = 'basket_'
const stripBasketPrefix = (name: string) => name.slice(LS_BASKET_PREFIX.length)
const addBasketPrefix   = (name: string) => `${LS_BASKET_PREFIX}${name}`

function App() {
  const [ baskets, setBaskets ] = useState<string[]>([]); // Array of Basket names
  const [ createdBasket, setCreatedBasket ] = useState<CreatedBasket | null>(null);
  const [ errorMessage, setErrorMessage ] = useState('');
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
    setErrorMessage('')

    try {
      const newBasket = await BasketService.createBasket(name)
      localStorage.setItem(addBasketPrefix(newBasket.name), newBasket.token)
      setBaskets(current => current.includes(newBasket.name) ? current : current.concat(newBasket.name))
      setCreatedBasket(newBasket)
    } catch (error) {
      console.error(error)
      setCreatedBasket(null)
      setErrorMessage(`Unable to create basket ${name}.`)
    }
  };

  const handleDeleteBasket = async (name: string) => {
    setErrorMessage('')
    const storageKey = addBasketPrefix(name)
    const token = localStorage.getItem(storageKey)

    if (!token) {
      setErrorMessage(`Unable to delete basket ${name}: ownership token is unavailable.`)
      return
    }

    try {
      await BasketService.deleteBasket(name, token)
    } catch (error) {
      console.error(error)
      setErrorMessage(`Unable to delete basket ${name}.`)
      return
    }

    localStorage.removeItem(storageKey)
    setBaskets(current => current.filter(bName => bName !== name))
    navigate('/baskets');
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--color-bg)', color: 'var(--color-text)', display: 'flex', flexDirection: 'column' }}>
      <Nav />
      {errorMessage && (
        <div role="alert" style={{ margin: '16px auto 0', width: 'min(1024px, calc(100% - 56px))', color: '#d99a9a' }}>
          {errorMessage}
        </div>
      )}
      <Routes>
        <Route path="/" element={<Navigate to="/baskets" replace />} />
        
        <Route path="/baskets" 
          element={<LandingPage baskets={baskets} createdBasket={createdBasket} onCreate={handleCreateBasket} />}
        />

        <Route path="/baskets/:name" 
          element={<BasketPage onDelete={handleDeleteBasket} />}
        />
      </Routes>
    </div>
  );
}

export default App;
