/**
 * Customer Dashboard — list of bookings with stats and quick actions.
 */
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import API from '../api/axios'
import { useAuth } from '../context/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import StatusBadge from '../components/StatusBadge'
import {
  CalendarDays, Clock, MapPin, ArrowRight, Plus, Package,
  CheckCircle, AlertCircle, FileText
} from 'lucide-react'

export default function Dashboard() {
  const { user } = useAuth()
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    const params = filter ? { status: filter } : {}
    API.get('/bookings/', { params })
      .then((res) => setBookings(res.data || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [filter])

  const stats = {
    total: bookings.length,
    active: bookings.filter(b => !['completed', 'cancelled'].includes(b.status)).length,
    completed: bookings.filter(b => b.status === 'completed').length,
  }

  return (
    <div className="relative">
      <div className="orb orb-blue w-[300px] h-[300px] -top-10 -right-10 animate-orb" />

      <div className="page-container">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white">
              Welcome back, <span className="text-gradient">{user?.name?.split(' ')[0] || 'User'}</span>
            </h1>
            <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
              Manage your service bookings and track progress
            </p>
          </div>
          <Link to="/services" className="btn-primary flex items-center gap-2 self-start">
            <Plus size={16} />
            Book New Service
          </Link>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          {[
            { label: 'Total Bookings', value: stats.total, icon: Package, color: 'text-blue-400' },
            { label: 'Active', value: stats.active, icon: Clock, color: 'text-amber-400' },
            { label: 'Completed', value: stats.completed, icon: CheckCircle, color: 'text-emerald-400' },
          ].map((stat, i) => (
            <div key={i} className="glass-card-static p-4 text-center">
              <stat.icon size={20} className={`${stat.color} mx-auto mb-2`} />
              <p className="text-2xl font-bold text-white">{stat.value}</p>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Filter */}
        <div className="flex flex-wrap gap-2 mb-6">
          {['', 'requested', 'assigned', 'on_way', 'inspection', 'waiting_approval', 'in_progress', 'completed', 'cancelled'].map((s) => (
            <button
              key={s}
              onClick={() => { setFilter(s); setLoading(true) }}
              className={`badge cursor-pointer transition-all ${
                filter === s ? 'badge-blue' : 'bg-white/5 text-slate-400 border border-white/10 hover:border-white/20'
              }`}
            >
              {s || 'All'}
            </button>
          ))}
        </div>

        {/* Bookings List */}
        {loading ? (
          <LoadingSpinner text="Loading bookings..." />
        ) : bookings.length === 0 ? (
          <div className="text-center py-20 glass-card-static">
            <FileText size={40} className="text-slate-600 mx-auto mb-3" />
            <p className="text-lg text-white mb-1">No bookings yet</p>
            <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>
              {filter ? 'Try a different filter' : 'Browse services to make your first booking'}
            </p>
            <Link to="/services" className="btn-primary inline-flex items-center gap-2">
              <Plus size={16} /> Browse Services
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {bookings.map((booking, i) => (
              <Link
                key={booking._id}
                to={`/bookings/${booking._id}`}
                className="glass-card p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 animate-slide-up"
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-white">{booking.service_name || 'Service'}</h3>
                    <StatusBadge status={booking.status} />
                  </div>
                  <p className="text-sm line-clamp-1 mb-2" style={{ color: 'var(--text-muted)' }}>
                    {booking.problem_description}
                  </p>
                  <div className="flex flex-wrap items-center gap-4 text-xs" style={{ color: 'var(--text-muted)' }}>
                    <span className="flex items-center gap-1"><CalendarDays size={12} /> {booking.scheduled_date}</span>
                    <span className="flex items-center gap-1"><Clock size={12} /> {booking.scheduled_time}</span>
                    <span className="flex items-center gap-1"><MapPin size={12} /> {booking.city}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {booking.final_price > 0 && (
                    <span className="text-emerald-400 font-semibold text-sm">₹{booking.final_price}</span>
                  )}
                  <ArrowRight size={18} className="text-slate-500" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
