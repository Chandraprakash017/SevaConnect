import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import ProtectedRoute from './components/ProtectedRoute'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Services from './pages/Services'
import AIAssistant from './pages/AIAssistant'
import BookService from './pages/BookService'
import Dashboard from './pages/Dashboard'
import BookingDetail from './pages/BookingDetail'
import TechDashboard from './pages/TechDashboard'
import TechJobDetail from './pages/TechJobDetail'
import AdminDashboard from './pages/AdminDashboard'
import Invoice from './pages/Invoice'

export default function App() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        <Routes>
          {/* Public */}
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/services" element={<Services />} />
          <Route path="/ai-assist" element={<AIAssistant />} />

          {/* Customer */}
          <Route path="/book/:serviceId" element={
            <ProtectedRoute roles={['customer']}><BookService /></ProtectedRoute>
          } />
          <Route path="/dashboard" element={
            <ProtectedRoute roles={['customer']}><Dashboard /></ProtectedRoute>
          } />
          <Route path="/bookings/:id" element={
            <ProtectedRoute roles={['customer', 'technician', 'admin']}><BookingDetail /></ProtectedRoute>
          } />
          <Route path="/invoice/:id" element={
            <ProtectedRoute roles={['customer', 'technician', 'admin']}><Invoice /></ProtectedRoute>
          } />

          {/* Technician */}
          <Route path="/technician" element={
            <ProtectedRoute roles={['technician']}><TechDashboard /></ProtectedRoute>
          } />
          <Route path="/technician/jobs/:id" element={
            <ProtectedRoute roles={['technician']}><TechJobDetail /></ProtectedRoute>
          } />

          {/* Admin */}
          <Route path="/admin" element={
            <ProtectedRoute roles={['admin']}><AdminDashboard /></ProtectedRoute>
          } />
        </Routes>
      </main>
      <Footer />
    </>
  )
}
