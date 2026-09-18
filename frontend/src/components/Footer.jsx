/**
 * Footer — dark theme footer with gradient accents.
 */
import { Wrench, Phone, Mail, Code, Heart } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="relative mt-auto" style={{ background: 'linear-gradient(180deg, var(--bg-primary), #050810)' }}>
      <div className="absolute inset-0 bg-gradient-mesh opacity-30" />
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">

          {/* Brand */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-xl">
                <Wrench size={16} className="text-white" />
              </div>
              <span className="text-lg font-bold text-white">
                Seva<span className="text-gradient">Connect</span>
              </span>
            </div>
            <p className="text-sm leading-relaxed max-w-md" style={{ color: 'var(--text-muted)' }}>
              AI-powered local service booking platform. Instantly diagnose problems,
              find the right technician, and get transparent pricing — all in one place.
            </p>
          </div>

          {/* Quick links */}
          <div>
            <h4 className="text-white font-semibold mb-4 text-sm tracking-wider uppercase">Explore</h4>
            <div className="space-y-2.5">
              <Link to="/services" className="block text-sm hover:text-blue-400 transition-colors duration-300" style={{ color: 'var(--text-muted)' }}>
                Browse Services
              </Link>
              <Link to="/ai-assist" className="block text-sm hover:text-blue-400 transition-colors duration-300" style={{ color: 'var(--text-muted)' }}>
                AI Assistant
              </Link>
              <Link to="/register" className="block text-sm hover:text-blue-400 transition-colors duration-300" style={{ color: 'var(--text-muted)' }}>
                Create Account
              </Link>
              <Link to="/login" className="block text-sm hover:text-blue-400 transition-colors duration-300" style={{ color: 'var(--text-muted)' }}>
                Login
              </Link>
            </div>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-white font-semibold mb-4 text-sm tracking-wider uppercase">Contact</h4>
            <div className="space-y-2.5">
              <div className="flex items-center gap-2.5 text-sm" style={{ color: 'var(--text-muted)' }}>
                <Phone size={14} className="text-blue-400" />
                <span>+91 98765 43210</span>
              </div>
              <div className="flex items-center gap-2.5 text-sm" style={{ color: 'var(--text-muted)' }}>
                <Mail size={14} className="text-purple-400" />
                <span>support@sevaconnect.in</span>
              </div>
              <a
                href="https://github.com/Chandraprakash017/SevaConnect"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2.5 text-sm hover:text-white transition-colors duration-300"
                style={{ color: 'var(--text-muted)' }}
              >
                <Code size={14} />
                <span>GitHub Repo</span>
              </a>
            </div>
          </div>
        </div>

        <div className="border-t mt-10 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4" style={{ borderColor: 'var(--glass-border)' }}>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
            © {new Date().getFullYear()} SevaConnect — B.Tech CSE Final Year Project
          </p>
          <p className="text-xs flex items-center gap-1" style={{ color: 'var(--text-muted)' }}>
            Made with <Heart size={12} className="text-red-400" fill="currentColor" /> by Chandraprakash
          </p>
        </div>
      </div>
    </footer>
  )
}
