import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Layout from './components/Layout'
import Home from './pages/Home'
import Companies from './pages/Companies'
import Calls from './pages/Calls'
import Appointments from './pages/Appointments'
import Documents from './pages/Documents'
import RagChunks from './pages/RagChunks'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="companies" element={<Companies />} />
            <Route path="calls" element={<Calls />} />
            <Route path="appointments" element={<Appointments />} />
            <Route path="documents" element={<Documents />} />
            <Route path="rag-chunks" element={<RagChunks />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App

