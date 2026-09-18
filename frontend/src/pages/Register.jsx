/**
 * Register page — multi-step form with role selection and premium UI.
 */
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import API from '../api/axios'
import { User, Mail, Lock, Phone, Eye, EyeOff, AlertCircle, UserCheck, Wrench, ArrowRight } from 'lucide-react'

export default function Register() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '', email: '', password: '', phone: '', role: 'customer',
  })
  const [showPwd, setShowPwd] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    setLoading(true)

    try {
      const res = await API.post('/auth/register/', form)
      login(res.data.user, res.data.tokens)
      const role = res.data.user.role
      if (role === 'technician') navigate('/technician')
      else navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const update = (key, val) => setForm({ ...form, [key]: val })

  return (
    <div className="relative min-h-[80vh] flex items-center justify-center px-4 py-12">
      <div className="orb orb-purple w-[400px] h-[400px] top-10 right-10 animate-orb" />
      <div className="orb orb-cyan w-[350px] h-[350px] bottom-10 left-10 animate-orb" style={{ animationDelay: '5s' }} />

      <div className="w-full max-w-md relative animate-slide-up">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
          <p style={{ color: 'var(--text-muted)' }} className="text-sm">Join SevaConnect in seconds</p>
        </div>

        <div className="glass-card-static p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="flex items-center gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20">
                <AlertCircle size={16} className="text-red-400 shrink-0" />
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}

            {/* Role Selection */}
            <div>
              <label className="label">I am a</label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => update('role', 'customer')}
                  className={`flex items-center justify-center gap-2 p-3 rounded-xl border text-sm font-medium transition-all duration-300 ${
                    form.role === 'customer'
                      ? 'border-blue-500 bg-blue-500/10 text-blue-400'
                      : 'border-white/10 text-slate-400 hover:border-white/20'
                  }`}
                >
                  <UserCheck size={16} />
                  Customer
                </button>
                <button
                  type="button"
                  onClick={() => update('role', 'technician')}
                  className={`flex items-center justify-center gap-2 p-3 rounded-xl border text-sm font-medium transition-all duration-300 ${
                    form.role === 'technician'
                      ? 'border-purple-500 bg-purple-500/10 text-purple-400'
                      : 'border-white/10 text-slate-400 hover:border-white/20'
                  }`}
                >
                  <Wrench size={16} />
                  Technician
                </button>
              </div>
            </div>

            <div>
              <label className="label">Full Name</label>
              <div className="relative">
                <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  className="input-field pl-10"
                  placeholder="Rahul Sharma"
                  value={form.name}
                  onChange={(e) => update('name', e.target.value)}
                  required
                />
              </div>
            </div>

            <div>
              <label className="label">Email Address</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="email"
                  className="input-field pl-10"
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={(e) => update('email', e.target.value)}
                  required
                />
              </div>
            </div>

            <div>
              <label className="label">Phone Number</label>
              <div className="relative">
                <Phone size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="tel"
                  className="input-field pl-10"
                  placeholder="9876543210"
                  value={form.phone}
                  onChange={(e) => update('phone', e.target.value)}
                  required
                />
              </div>
            </div>

            <div>
              <label className="label">Password</label>
              <div className="relative">
                <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type={showPwd ? 'text' : 'password'}
                  className="input-field pl-10 pr-10"
                  placeholder="Min 6 characters"
                  value={form.password}
                  onChange={(e) => update('password', e.target.value)}
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowPwd(!showPwd)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                >
                  {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2 py-3.5"
            >
              {loading ? (
                <div className="spinner-3d" style={{ width: 20, height: 20, borderWidth: 2 }} />
              ) : (
                <>
                  Create Account
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          <p className="text-center text-sm mt-6" style={{ color: 'var(--text-muted)' }}>
            Already have an account?{' '}
            <Link to="/login" className="text-blue-400 hover:text-blue-300 font-medium">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
