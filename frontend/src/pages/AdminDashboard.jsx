/**
 * AdminDashboard — admin overview with stats, manage technicians, bookings.
 */
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import API from '../api/axios'
import LoadingSpinner from '../components/LoadingSpinner'
import StatusBadge from '../components/StatusBadge'
import {
  Users, Briefcase, CheckCircle, IndianRupee, ShieldCheck, XCircle,
  ArrowRight, Calendar, MapPin, User, Star, Clock
} from 'lucide-react'

export default function AdminDashboard() {
  const [bookings, setBookings] = useState([])
  const [technicians, setTechnicians] = useState([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('overview') // overview | bookings | technicians
  const [verifyingId, setVerifyingId] = useState(null)

  useEffect(() => {
    Promise.all([
      API.get('/bookings/').then(r => r.data || []),
      API.get('/technicians/').then(r => r.data || []),
    ]).then(([b, t]) => {
      setBookings(b)
      setTechnicians(t)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const stats = {
    totalBookings: bookings.length,
    activeBookings: bookings.filter(b => !['completed', 'cancelled'].includes(b.status)).length,
    completedBookings: bookings.filter(b => b.status === 'completed').length,
    totalTechnicians: technicians.length,
    revenue: bookings.filter(b => b.status === 'completed').reduce((s, b) => s + (b.final_price || 0), 0),
  }

  const handleVerify = async (techId, verified) => {
    setVerifyingId(techId)
    try {
      await API.put(`/technicians/${techId}/verify/`, { is_verified: verified })
      setTechnicians(prev => prev.map(t =>
        t._id === techId ? { ...t, is_verified: verified } : t
      ))
    } catch (err) {
      alert(err.response?.data?.error || 'Action failed')
    }
    setVerifyingId(null)
  }

  if (loading) return <LoadingSpinner text="Loading admin panel..." />

  return (
    <div className="relative">
      <div className="orb orb-purple w-[400px] h-[400px] -top-20 -left-20 animate-orb" />

      <div className="page-container">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white">
            Admin <span className="text-gradient">Dashboard</span>
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            Manage bookings, technicians, and platform overview
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          {[
            { label: 'Total Bookings', value: stats.totalBookings, icon: Briefcase, color: 'text-blue-400' },
            { label: 'Active', value: stats.activeBookings, icon: Clock, color: 'text-amber-400' },
            { label: 'Completed', value: stats.completedBookings, icon: CheckCircle, color: 'text-emerald-400' },
            { label: 'Technicians', value: stats.totalTechnicians, icon: Users, color: 'text-purple-400' },
            { label: 'Revenue', value: `₹${stats.revenue}`, icon: IndianRupee, color: 'text-cyan-400' },
          ].map((stat, i) => (
            <div key={i} className="glass-card-static p-4 text-center">
              <stat.icon size={20} className={`${stat.color} mx-auto mb-2`} />
              <p className="text-xl font-bold text-white">{stat.value}</p>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {[
            { key: 'overview', label: 'Recent Bookings' },
            { key: 'technicians', label: `Technicians (${technicians.length})` },
          ].map(t => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`badge cursor-pointer transition-all ${
                tab === t.key ? 'badge-blue' : 'bg-white/5 text-slate-400 border border-white/10 hover:border-white/20'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Bookings Tab */}
        {tab === 'overview' && (
          <div className="space-y-3">
            {bookings.slice(0, 20).map((booking, i) => (
              <Link
                key={booking._id}
                to={`/bookings/${booking._id}`}
                className="glass-card p-4 flex items-center justify-between animate-slide-up"
                style={{ animationDelay: `${i * 0.03}s` }}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="font-medium text-white text-sm">{booking.service_name}</h3>
                    <StatusBadge status={booking.status} />
                  </div>
                  <div className="flex gap-3 text-xs" style={{ color: 'var(--text-muted)' }}>
                    <span className="flex items-center gap-1"><Calendar size={11} /> {booking.scheduled_date}</span>
                    <span className="flex items-center gap-1"><MapPin size={11} /> {booking.city}</span>
                    {booking.final_price > 0 && (
                      <span className="text-emerald-400">₹{booking.final_price}</span>
                    )}
                  </div>
                </div>
                <ArrowRight size={16} className="text-slate-500" />
              </Link>
            ))}
            {bookings.length === 0 && (
              <div className="text-center py-16 glass-card-static">
                <p style={{ color: 'var(--text-muted)' }}>No bookings yet</p>
              </div>
            )}
          </div>
        )}

        {/* Technicians Tab */}
        {tab === 'technicians' && (
          <div className="space-y-3">
            {technicians.map((tech, i) => (
              <div
                key={tech._id}
                className="glass-card-static p-4 flex items-center justify-between animate-slide-up"
                style={{ animationDelay: `${i * 0.03}s` }}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                    <User size={18} className="text-white" />
                  </div>
                  <div>
                    <p className="font-medium text-white text-sm">{tech.name || 'Technician'}</p>
                    <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--text-muted)' }}>
                      {tech.city && <span className="flex items-center gap-1"><MapPin size={11} /> {tech.city}</span>}
                      <span className="flex items-center gap-1"><Star size={11} className="text-amber-400" /> {tech.ratings_avg || 0}</span>
                      <span>{tech.total_jobs || 0} jobs</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {tech.is_verified ? (
                    <span className="badge-green badge text-xs"><ShieldCheck size={12} /> Verified</span>
                  ) : (
                    <button
                      onClick={() => handleVerify(tech._id, true)}
                      disabled={verifyingId === tech._id}
                      className="btn-primary btn-sm text-xs flex items-center gap-1"
                    >
                      {verifyingId === tech._id ? '...' : <><ShieldCheck size={12} /> Verify</>}
                    </button>
                  )}
                </div>
              </div>
            ))}
            {technicians.length === 0 && (
              <div className="text-center py-16 glass-card-static">
                <p style={{ color: 'var(--text-muted)' }}>No technicians registered yet</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
