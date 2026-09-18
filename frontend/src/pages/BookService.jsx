/**
 * BookService — multi-step booking wizard.
 * Step 1: Service details + problem description
 * Step 2: Address & schedule
 * Step 3: Confirmation
 */
import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import API from '../api/axios'
import LoadingSpinner from '../components/LoadingSpinner'
import {
  ArrowRight, ArrowLeft, MapPin, Calendar, Clock, FileText,
  CheckCircle, IndianRupee, AlertCircle, Sparkles
} from 'lucide-react'

export default function BookService() {
  const { serviceId } = useParams()
  const navigate = useNavigate()
  const [service, setService] = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [step, setStep] = useState(1)
  const [form, setForm] = useState({
    problem_description: '',
    address: '',
    city: '',
    pincode: '',
    landmark: '',
    scheduled_date: '',
    scheduled_time: '',
  })

  useEffect(() => {
    API.get(`/services/${serviceId}/`)
      .then((res) => setService(res.data))
      .catch(() => setError('Service not found'))
      .finally(() => setLoading(false))
  }, [serviceId])

  const update = (key, val) => setForm({ ...form, [key]: val })

  const handleSubmit = async () => {
    setError('')
    setSubmitting(true)
    try {
      const res = await API.post('/bookings/create/', {
        service_id: serviceId,
        ...form,
      })
      navigate(`/bookings/${res.data._id}`)
    } catch (err) {
      setError(err.response?.data?.error || 'Booking failed. Please try again.')
      setSubmitting(false)
    }
  }

  if (loading) return <LoadingSpinner text="Loading service details..." />

  if (!service) {
    return (
      <div className="page-container text-center py-20">
        <p className="text-lg text-white mb-2">Service not found</p>
        <Link to="/services" className="text-blue-400 hover:underline text-sm">Browse all services</Link>
      </div>
    )
  }

  const estimatedMin = (service.visit_charge || 100) + (service.labour_min || 0)
  const estimatedMax = (service.visit_charge || 100) + (service.labour_max || service.base_price || 0)

  return (
    <div className="relative">
      <div className="orb orb-blue w-[300px] h-[300px] -top-10 right-0 animate-orb" />
      <div className="page-container max-w-2xl mx-auto">
        <h1 className="section-title text-center mb-2">Book Service</h1>
        <p className="section-subtitle text-center mb-8">{service.name}</p>

        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-2 mb-10">
          {['Problem', 'Address', 'Confirm'].map((label, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${
                step > i + 1 ? 'bg-emerald-500 text-white' :
                step === i + 1 ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/30' :
                'bg-white/5 text-slate-500 border border-white/10'
              }`}>
                {step > i + 1 ? <CheckCircle size={14} /> : i + 1}
              </div>
              <span className={`text-xs font-medium hidden sm:block ${
                step === i + 1 ? 'text-white' : 'text-slate-500'
              }`}>{label}</span>
              {i < 2 && <div className={`w-8 h-0.5 ${step > i + 1 ? 'bg-emerald-500' : 'bg-white/10'}`} />}
            </div>
          ))}
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20 mb-6">
            <AlertCircle size={16} className="text-red-400 shrink-0" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Step 1: Problem */}
        {step === 1 && (
          <div className="glass-card-static p-6 md:p-8 animate-slide-up">
            <div className="flex items-center gap-3 mb-6">
              <div className="text-3xl">{service.icon || '🔧'}</div>
              <div>
                <h2 className="font-semibold text-white">{service.name}</h2>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  Estimated: ₹{estimatedMin} – ₹{estimatedMax}
                </p>
              </div>
            </div>

            <div className="mb-5">
              <label className="label flex items-center gap-2">
                <FileText size={14} className="text-blue-400" />
                Describe your problem
              </label>
              <textarea
                className="input-field"
                rows={4}
                placeholder="What's the issue? Be as specific as possible..."
                value={form.problem_description}
                onChange={(e) => update('problem_description', e.target.value)}
                required
              />
            </div>

            <div className="flex justify-between items-center">
              <Link to="/ai-assist" className="flex items-center gap-1.5 text-sm text-purple-400 hover:text-purple-300">
                <Sparkles size={14} />
                Use AI to diagnose first
              </Link>
              <button
                onClick={() => {
                  if (!form.problem_description.trim()) { setError('Please describe your problem'); return }
                  setError('')
                  setStep(2)
                }}
                className="btn-primary flex items-center gap-2"
              >
                Next <ArrowRight size={16} />
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Address */}
        {step === 2 && (
          <div className="glass-card-static p-6 md:p-8 animate-slide-up">
            <h2 className="font-semibold text-white mb-6 flex items-center gap-2">
              <MapPin size={18} className="text-blue-400" />
              Service Location & Schedule
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="md:col-span-2">
                <label className="label">Street Address</label>
                <input className="input-field" placeholder="123 Main Street, Apartment 4B" value={form.address} onChange={(e) => update('address', e.target.value)} required />
              </div>
              <div>
                <label className="label">City</label>
                <input className="input-field" placeholder="Mumbai" value={form.city} onChange={(e) => update('city', e.target.value)} required />
              </div>
              <div>
                <label className="label">Pincode</label>
                <input className="input-field" placeholder="400001" value={form.pincode} onChange={(e) => update('pincode', e.target.value)} required />
              </div>
              <div className="md:col-span-2">
                <label className="label">Landmark (optional)</label>
                <input className="input-field" placeholder="Near Reliance petrol pump" value={form.landmark} onChange={(e) => update('landmark', e.target.value)} />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="label flex items-center gap-1.5"><Calendar size={14} className="text-blue-400" /> Preferred Date</label>
                <input type="date" className="input-field" value={form.scheduled_date} onChange={(e) => update('scheduled_date', e.target.value)} min={new Date().toISOString().split('T')[0]} required />
              </div>
              <div>
                <label className="label flex items-center gap-1.5"><Clock size={14} className="text-blue-400" /> Preferred Time</label>
                <select className="input-field" value={form.scheduled_time} onChange={(e) => update('scheduled_time', e.target.value)} required>
                  <option value="">Select time</option>
                  <option value="9:00 AM">9:00 AM</option>
                  <option value="10:00 AM">10:00 AM</option>
                  <option value="11:00 AM">11:00 AM</option>
                  <option value="12:00 PM">12:00 PM</option>
                  <option value="2:00 PM">2:00 PM</option>
                  <option value="3:00 PM">3:00 PM</option>
                  <option value="4:00 PM">4:00 PM</option>
                  <option value="5:00 PM">5:00 PM</option>
                </select>
              </div>
            </div>

            <div className="flex justify-between">
              <button onClick={() => setStep(1)} className="btn-secondary flex items-center gap-2">
                <ArrowLeft size={16} /> Back
              </button>
              <button
                onClick={() => {
                  const req = ['address', 'city', 'pincode', 'scheduled_date', 'scheduled_time']
                  const missing = req.find(f => !form[f]?.trim())
                  if (missing) { setError(`Please fill in the ${missing.replace('_', ' ')}`); return }
                  setError('')
                  setStep(3)
                }}
                className="btn-primary flex items-center gap-2"
              >
                Review <ArrowRight size={16} />
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Confirm */}
        {step === 3 && (
          <div className="glass-card-static p-6 md:p-8 animate-slide-up">
            <h2 className="font-semibold text-white mb-6 flex items-center gap-2">
              <CheckCircle size={18} className="text-emerald-400" />
              Review & Confirm
            </h2>

            <div className="space-y-4 mb-6">
              <div className="flex justify-between text-sm">
                <span style={{ color: 'var(--text-muted)' }}>Service</span>
                <span className="text-white font-medium">{service.name}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span style={{ color: 'var(--text-muted)' }}>Problem</span>
                <span className="text-white text-right max-w-[60%]">{form.problem_description}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span style={{ color: 'var(--text-muted)' }}>Address</span>
                <span className="text-white text-right">{form.address}, {form.city} {form.pincode}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span style={{ color: 'var(--text-muted)' }}>When</span>
                <span className="text-white">{form.scheduled_date} at {form.scheduled_time}</span>
              </div>
              <hr style={{ borderColor: 'var(--glass-border)' }} />
              <div className="flex justify-between text-sm">
                <span style={{ color: 'var(--text-muted)' }}>Estimated Cost</span>
                <span className="text-emerald-400 font-semibold flex items-center gap-1">
                  <IndianRupee size={14} />
                  ₹{estimatedMin} – ₹{estimatedMax}
                </span>
              </div>
            </div>

            <p className="text-xs mb-6" style={{ color: 'var(--text-muted)' }}>
              * The technician will inspect and provide an exact quote before starting work. You can approve or cancel at that point.
            </p>

            <div className="flex justify-between">
              <button onClick={() => setStep(2)} className="btn-secondary flex items-center gap-2">
                <ArrowLeft size={16} /> Edit
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="btn-primary flex items-center gap-2"
              >
                {submitting ? (
                  <div className="spinner-3d" style={{ width: 18, height: 18, borderWidth: 2 }} />
                ) : (
                  <>
                    Confirm Booking
                    <CheckCircle size={16} />
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
