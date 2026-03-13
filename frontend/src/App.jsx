import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Dashboard  from './pages/Dashboard'
import LeadDetail from './pages/LeadDetail'

export default function App() {
  return (
    <BrowserRouter>
      <Toaster 
        position="top-right" 
        toastOptions={{
          style: {
            background: '#1a1f26',
            color: '#fff',
            border: '1px solid rgba(255,255,255,0.1)',
            backdropFilter: 'blur(10px)',
            borderRadius: '12px',
          },
        }}
      />
      <Routes>
        <Route path="/"         element={<Dashboard />}  />
        <Route path="/lead/:id" element={<LeadDetail />} />
      </Routes>
    </BrowserRouter>
  )
}
