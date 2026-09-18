/**
 * Navbar — responsive navigation with glassmorphism dark theme.
 * Shows different links based on user role.
 */
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Wrench, Menu, X, User, LogOut, LayoutDashboard, Sparkles, Search } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // Close menu on route change
  useEffect(() => { setMenuOpen(false) }, [location])

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const getDashboardLink = () => {
    if (!user) return '/login'
    if (user.role === 'admin') return '/admin'
    if (user.role === 'technician') return '/technician'
    return '/dashboard'
  }

  const isActive = (path) => location.pathname === path

  const navLinkClass = (path) =>
    `flex items-center gap-1.5 text-sm font-medium transition-all duration-300 ${
      isActive(path)
        ? 'text-blue-400'
        : 'text-slate-400 hover:text-white'
    }`

  return (
    <nav
      className={`sticky top-0 z-50 transition-all duration-500 ${
        scrolled
          ? 'bg-[#0a0e1a]/90 backdrop-blur-xl border-b border-white/5 shadow-lg shadow-black/20'
          : 'bg-transparent border-b border-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">

          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="relative">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-xl transition-transform duration-300 group-hover:scale-110 group-hover:shadow-lg group-hover:shadow-blue-500/25">
                <Wrench size={18} className="text-white" />
              </div>
            </div>
            <span className="text-lg font-bold text-white tracking-tight">
              Seva<span className="text-gradient">Connect</span>
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-6">
            <Link to="/services" className={navLinkClass('/services')}>
              <Search size={14} />
              Services
            </Link>
            <Link to="/ai-assist" className={navLinkClass('/ai-assist')}>
              <Sparkles size={14} />
              AI Assistant
            </Link>

            {isAuthenticated ? (
              <div className="flex items-center gap-4">
                <Link to={getDashboardLink()} className={navLinkClass(getDashboardLink())}>
                  <LayoutDashboard size={14} />
                  Dashboard
                </Link>
                <div className="flex items-center gap-2 glass-card-static px-3 py-1.5 rounded-full" style={{ padding: '6px 12px' }}>
                  <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                    <User size={12} className="text-white" />
                  </div>
                  <span className="text-sm font-medium text-slate-300">{user.name?.split(' ')[0]}</span>
                  <span className="badge-blue badge text-[10px] !px-2 !py-0.5 capitalize">{user.role}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-red-400 transition-colors duration-300"
                >
                  <LogOut size={14} />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link to="/login" className="text-sm text-slate-400 hover:text-white transition-colors duration-300 font-medium">
                  Login
                </Link>
                <Link to="/register" className="btn-primary btn-sm">
                  Get Started
                </Link>
              </div>
            )}
          </div>

          {/* Mobile hamburger */}
          <button className="md:hidden p-2 text-slate-400 hover:text-white transition-colors" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>

        {/* Mobile dropdown */}
        {menuOpen && (
          <div className="md:hidden border-t border-white/5 py-4 space-y-3 animate-slide-up">
            <Link to="/services" className="block text-sm text-slate-300 hover:text-white py-2">Browse Services</Link>
            <Link to="/ai-assist" className="block text-sm text-slate-300 hover:text-white py-2">AI Assistant</Link>
            {isAuthenticated ? (
              <>
                <Link to={getDashboardLink()} className="block text-sm text-slate-300 hover:text-white py-2">Dashboard</Link>
                <button onClick={handleLogout} className="block text-sm text-red-400 py-2 w-full text-left">Logout</button>
              </>
            ) : (
              <>
                <Link to="/login" className="block text-sm text-slate-300 hover:text-white py-2">Login</Link>
                <Link to="/register" className="btn-primary btn-sm inline-block mt-2">Get Started</Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}
