/**
 * TechDashboard — Technician's main dashboard.
 * Shows available jobs (to accept) and their active/completed jobs.
 */
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import API from '../api/axios'
import { useAuth } from '../context/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import StatusBadge from '../components/StatusBadge'
import {
  Briefcase, Clock, CheckCircle, MapPin, Calendar,
  ArrowRight, Star, IndianRupee, User, Zap
} from 'lucide-react'

export default function TechDashboard() {
  const { user } = useAuth()
  const [myJobs, setMyJobs] = useState([])
  const [availableJobs, setAvailableJobs] = useState([])
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('active') // active | available | completed
  const [accepting, setAccepting] = useState(null)

  useEffect(() => {
    Promise.all([
      API.get('/bookings/').then(r => r.data || []),
      API.get('/bookings/available/').then(r => r.data || []),
      API.get('/technicians/me/').then(r => r.data).catch(() => null),
    ]).then(([jobs, available, prof]) => {
      setMyJobs(jobs)
      setAvailableJobs(available)
      setProfile(prof)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const handleAccept = async (bookingId) => {
    setAccepting(bookingId)
    try {
      await API.post(`/bookings/${bookingId}/accept/`)
      // Move job from available to myJobs
      const job = availableJobs.find(j => j._id === bookingId)
      if (job) {
        setAvailableJobs(prev => prev.filter(j => j._id !== bookingId))
        setMyJobs(prev => [{ ...job, status: 'assigned' }, ...prev])
      }
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to accept job')
    }
    setAccepting(null)
  }

  const activeJobs = myJobs.filter(j => !['completed', 'cancelled'].includes(j.status))
  const completedJobs = myJobs.filter(j => j.status === 'completed')

  const totalEarnings = completedJobs.reduce((sum, j) => sum + (j.final_price || 0), 0)

  if (loading) return <LoadingSpinner text="Loading dashboard..." />

  return (
    <div className="relative">
      <div className="orb orb-purple w-[300px] h-[300px] -top-10 -right-10 animate-orb" />

      <div className="page-container">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white">
            Technician <span className="text-gradient">Dashboard</span>
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            Welcome back, {user?.name || 'Technician'}
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Active Jobs', value: activeJobs.length, icon: Briefcase, color: 'text-blue-400' },
            { label: 'Available', value: availableJobs.length, icon: Zap, color: 'text-amber-400' },
            { label: 'Completed', value: completedJobs.length, icon: CheckCircle, color: 'text-emerald-400' },
            { label: 'Earnings', value: `₹${totalEarnings}`, icon: IndianRupee, color: 'text-purple-400' },
          ].map((stat, i) => (
            <div key={i} className="glass-card-static p-4 text-center">
              <stat.icon size={20} className={`${stat.color} mx-auto mb-2`} />
              <p className="text-xl font-bold text-white">{stat.value}</p>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Profile Card */}
        {profile && (
          <div className="glass-card-static p-4 mb-8 flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
              <User size={22} className="text-white" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-white">{profile.name}</p>
              <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--text-muted)' }}>
                {profile.city && <span className="flex items-center gap-1"><MapPin size={11} /> {profile.city}</span>}
                <span className="flex items-center gap-1"><Star size={11} className="text-amber-400" /> {profile.ratings_avg || 0}</span>
                <span>{profile.total_jobs || 0} jobs</span>
              </div>
            </div>
            {!profile.is_verified && (
              <span className="badge-yellow badge text-xs">Pending Verification</span>
            )}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {[
            { key: 'active', label: `Active (${activeJobs.length})` },
            { key: 'available', label: `Available (${availableJobs.length})` },
            { key: 'completed', label: `Completed (${completedJobs.length})` },
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

        {/* Job Lists */}
        <div className="space-y-4">
          {tab === 'active' && activeJobs.map((job, i) => (
            <Link
              key={job._id}
              to={`/technician/jobs/${job._id}`}
              className="glass-card p-5 flex items-center justify-between animate-slide-up"
              style={{ animationDelay: `${i * 0.05}s` }}
            >
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="font-semibold text-white">{job.service_name}</h3>
                  <StatusBadge status={job.status} />
                </div>
                <p className="text-xs line-clamp-1" style={{ color: 'var(--text-muted)' }}>{job.problem_description}</p>
                <div className="flex gap-3 mt-2 text-xs" style={{ color: 'var(--text-muted)' }}>
                  <span className="flex items-center gap-1"><MapPin size={11} /> {job.city} {job.pincode}</span>
                  <span className="flex items-center gap-1"><Calendar size={11} /> {job.scheduled_date}</span>
                </div>
              </div>
              <ArrowRight size={18} className="text-slate-500" />
            </Link>
          ))}

          {tab === 'available' && availableJobs.map((job, i) => (
            <div
              key={job._id}
              className="glass-card-static p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 animate-slide-up"
              style={{ animationDelay: `${i * 0.05}s` }}
            >
              <div className="flex-1">
                <h3 className="font-semibold text-white mb-1">{job.service_name}</h3>
                <p className="text-xs line-clamp-2 mb-2" style={{ color: 'var(--text-muted)' }}>{job.problem_description}</p>
                <div className="flex gap-3 text-xs" style={{ color: 'var(--text-muted)' }}>
                  <span className="flex items-center gap-1"><MapPin size={11} /> {job.city} {job.pincode}</span>
                  <span className="flex items-center gap-1"><Calendar size={11} /> {job.scheduled_date}</span>
                  <span className="flex items-center gap-1"><Clock size={11} /> {job.scheduled_time}</span>
                </div>
              </div>
              <button
                onClick={() => handleAccept(job._id)}
                disabled={accepting === job._id}
                className="btn-primary btn-sm flex items-center gap-2 shrink-0"
              >
                {accepting === job._id ? (
                  <div className="spinner-3d" style={{ width: 14, height: 14, borderWidth: 2 }} />
                ) : (
                  <>Accept Job</>
                )}
              </button>
            </div>
          ))}

          {tab === 'completed' && completedJobs.map((job, i) => (
            <Link
              key={job._id}
              to={`/technician/jobs/${job._id}`}
              className="glass-card p-5 flex items-center justify-between animate-slide-up"
              style={{ animationDelay: `${i * 0.05}s` }}
            >
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="font-semibold text-white">{job.service_name}</h3>
                  <StatusBadge status="completed" />
                </div>
                <div className="flex gap-3 mt-1 text-xs" style={{ color: 'var(--text-muted)' }}>
                  <span>{job.scheduled_date}</span>
                  <span>{job.city}</span>
                </div>
              </div>
              {job.final_price > 0 && (
                <span className="text-emerald-400 font-semibold text-sm">₹{job.final_price}</span>
              )}
            </Link>
          ))}

          {/* Empty states */}
          {tab === 'active' && activeJobs.length === 0 && (
            <div className="text-center py-16 glass-card-static"><p style={{ color: 'var(--text-muted)' }}>No active jobs. Check available jobs to accept one!</p></div>
          )}
          {tab === 'available' && availableJobs.length === 0 && (
            <div className="text-center py-16 glass-card-static"><p style={{ color: 'var(--text-muted)' }}>No jobs available right now. Check back later!</p></div>
          )}
          {tab === 'completed' && completedJobs.length === 0 && (
            <div className="text-center py-16 glass-card-static"><p style={{ color: 'var(--text-muted)' }}>No completed jobs yet.</p></div>
          )}
        </div>
      </div>
    </div>
  )
}
