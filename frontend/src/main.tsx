import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ErrorBoundary } from './ErrorBoundary'

console.log("Main.tsx executing...");
try {
  const root = document.getElementById('root');
  console.log("Root element:", root);

  createRoot(root!).render(
    <StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </StrictMode>,
  )
  console.log("Render called");
} catch (e) {
  console.error("Render failed:", e);
}
