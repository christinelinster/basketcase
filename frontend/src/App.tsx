import { useState, useEffect } from 'react';
import Cooltest from './components/something';
import './App.css';
import axios from 'axios';



// Define form event type
interface FormEvent extends React.FormEvent<HTMLFormElement> {
  currentTarget: HTMLFormElement;
}

function App() {
  const [seeWorld, setTheWorld] = useState<string>('Nothing');

  const contactServer = async (): Promise<any> => {
    try {
      let conn = await axios.get('/api');
      setTheWorld(conn.data.success)
    } catch (err) {
      console.log('oops: ', err);
    }
  };

  useEffect(() => {
    void contactServer();
  }, []); // Added empty dependency array to prevent infinite loops

const renderContent = async (): Promise<any> => {
  try{
  let res = await contactServer();
  let theWords = res.data
  setTheWorld(theWords) 
  return theWords
  } catch (err) {
    console.log('oops: ', err)
  }
}

  return (
    <>
      <section id="center" className="note">
        <div className="hero">
        </div>
        <div>
          { seeWorld }
        </div>
      </section>

      <div className="ticks"></div>

      <section id="next-steps">
        <div id="docs">
          <svg className="icon" role="presentation" aria-hidden="true">
            <use href="/icons.svg#documentation-icon"></use>
          </svg>
          <h2>Documentation</h2>
          <p>Your questions, answered</p>
          <ul>
            <li>
              No questions?
            </li>
            <li>
              Great
            </li>
          </ul>
        </div>
        <div id="social">
          <svg className="icon" role="presentation" aria-hidden="true">
            <use href="/icons.svg#social-icon"></use>
          </svg>
          <h2>Connect with us</h2>
          <p>Join the Very Cool community</p>
          <ul>
            <li>
              Say JuiceBeetle three times, might work
            </li>
          </ul>
        </div>
      </section>

      <div className="ticks"></div>
      <section id="spacer"></section>
    </>
  );
}

export default App;