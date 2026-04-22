// Purpose: Bootstrap React root for frontend application.
// Callers: Browser entrypoint loaded by Vite index.html.
// Deps: react, react-dom, App component.
// API: Renders App into #root.
// Side effects: Mounts full UI tree.
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);