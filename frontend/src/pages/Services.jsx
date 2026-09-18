/**
 * Services — browse all services with department filter, search, and 3D cards.
 */
import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import API from '../api/axios'
import LoadingSpinner from '../components/LoadingSpinner'
import { Search, Clock, IndianRupee, ArrowRight, Layers } from 'lucide-react'

export default function Services() {
  const [searchParams] = useSearchParams()
  const [services, setServices] = useState([])
  const [departments, setDepartments] = useState([])
  const [activeDept, setActiveDept] = useState(searchParams.get('dept') || '')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    API.get('/departments/').then((res) => setDepartments(res.data || [])).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    const params = {}
    if (activeDept) params.dept_id = activeDept
    if (search.trim()) params.search = search.trim()

    API.get('/services/', { params })
      .then((res) => setServices(res.data || []))
      .catch(() => setServices([]))
      .finally(() => setLoading(false))
  }, [activeDept, search])

  return (
    <div className="relative">
      <div className="orb orb-blue w-[400px] h-[400px] -top-20 -right-20 animate-orb" />

      <div className="page-container">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="section-title">Browse Services</h1>
          <p className="section-subtitle mt-2">Find the exact service you need from our extensive catalog</p>
        </div>

        {/* Search + Filter */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              className="input-field pl-11 pr-4"
              placeholder="Search services (e.g., AC repair, bike service)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>

        {/* Department Tabs */}
        <div className="flex flex-wrap gap-2 mb-8">
          <button
            onClick={() => setActiveDept('')}
            className={`badge transition-all duration-300 cursor-pointer ${
              !activeDept ? 'badge-blue' : 'bg-white/5 text-slate-400 border border-white/10 hover:border-white/20'
            }`}
          >
            <Layers size={13} />
            All Categories
          </button>
          {departments.map((dept) => (
            <button
              key={dept._id}
              onClick={() => setActiveDept(dept._id)}
              className={`badge transition-all duration-300 cursor-pointer ${
                activeDept === dept._id ? 'badge-blue' : 'bg-white/5 text-slate-400 border border-white/10 hover:border-white/20'
              }`}
            >
              {dept.icon || '🔧'} {dept.name}
            </button>
          ))}
        </div>

        {/* Services Grid */}
        {loading ? (
          <LoadingSpinner text="Loading services..." />
        ) : services.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-lg" style={{ color: 'var(--text-muted)' }}>No services found</p>
            <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>Try a different search or category</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {services.map((service, i) => (
              <div
                key={service._id}
                className="card-3d p-6 flex flex-col animate-slide-up"
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="text-3xl">{service.icon || '🔧'}</div>
                  <div className="badge-green">
                    <IndianRupee size={12} />
                    ₹{service.base_price || 0}
                  </div>
                </div>

                <h3 className="text-lg font-semibold text-white mb-2">{service.name}</h3>
                <p className="text-sm flex-1 line-clamp-3 mb-4" style={{ color: 'var(--text-muted)' }}>
                  {service.description || 'Professional service by verified technicians.'}
                </p>

                <div className="flex items-center justify-between pt-4 border-t" style={{ borderColor: 'var(--glass-border)' }}>
                  <div className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
                    <Clock size={13} />
                    {service.duration_minutes || 60} min
                  </div>
                  <Link
                    to={`/book/${service._id}`}
                    className="flex items-center gap-1.5 text-sm font-medium text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    Book Now <ArrowRight size={14} />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
