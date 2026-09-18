/**
 * TechJobDetail — Technician's view of a specific job.
 * Actions: update status, submit quote (after inspection).
 */
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import API from '../api/axios'
import LoadingSpinner from '../components/LoadingSpinner'
import StatusBadge from '../components/StatusBadge'
import {
  ArrowLeft, MapPin, Calendar, Clock, Phone, User, MessageSquare,
  Truck, Search, FileText, Wrench, CheckCircle, IndianRupee, Plus, Trash2,
  AlertCircle, Send
} from 'lucide-react'

const TECH_ACTIONS = {
  assigned:    { next: 'on_way',           label: 'Mark On the Way',  icon: Truck,       desc: 'Heading to customer location' },
  on_way:      { next: 'inspection',       label: 'Start Inspection', icon: Search,      desc: 'Arrived at location, starting inspection' },
  in_progress: { next: 'completed',        label: 'Mark Completed',   icon: CheckCircle, desc: 'Service completed successfully' },
}

export default function TechJobDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [booking, setBooking] = useState(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [error, setError] = useState('')

  // Quote form (used during inspection)
  const [quoteForm, setQuoteForm] = useState({
    labour_charge: '',
    technician_notes: '',
    parts_used: [],
  })

  const fetchBooking = () => {
    API.get(`/bookings/${id}/`)
      .then((res) => {
        setBooking(res.data)
        if (res.data.labour_charge) {
          setQuoteForm({
            labour_charge: res.data.labour_charge || '',
            technician_notes: res.data.technician_notes || '',
            parts_used: res.data.parts_used || [],
          })
        }
      })
      .catch(() => setError('Job not found'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchBooking() }, [id])

  const handleStatusUpdate = async (newStatus) => {
    setActionLoading(true)
    setError('')
    try {
      await API.patch(`/bookings/${id}/status/`, { status: newStatus })
      fetchBooking()
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update status')
    }
    setActionLoading(false)
  }

  const handleSubmitQuote = async () => {
    if (!quoteForm.labour_charge || parseFloat(quoteForm.labour_charge) <= 0) {
      setError('Please enter a valid labour charge')
      return
    }
    setActionLoading(true)
    setError('')
    try {
      await API.post(`/bookings/${id}/quote/`, {
        labour_charge: parseFloat(quoteForm.labour_charge),
        parts_used: quoteForm.parts_used,
        technician_notes: quoteForm.technician_notes,
      })
      fetchBooking()
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit quote')
    }
    setActionLoading(false)
  }

  const addPart = () => {
    setQuoteForm({
      ...quoteForm,
      parts_used: [...quoteForm.parts_used, { name: '', quantity: 1, price: 0 }],
    })
  }

  const updatePart = (idx, key, val) => {
    const parts = [...quoteForm.parts_used]
    parts[idx] = { ...parts[idx], [key]: key === 'name' ? val : Number(val) }
    setQuoteForm({ ...quoteForm, parts_used: parts })
  }

  const removePart = (idx) => {
    setQuoteForm({
      ...quoteForm,
      parts_used: quoteForm.parts_used.filter((_, i) => i !== idx),
    })
  }

  if (loading) return <LoadingSpinner text="Loading job..." />

  if (!booking) {
    return (
      <div className="page-container text-center py-20">
        <p className="text-lg text-white">Job not found</p>
        <button onClick={() => navigate(-1)} className="text-blue-400 hover:underline text-sm mt-2">Go back</button>
      </div>
    )
  }

  const action = TECH_ACTIONS[booking.status]

  return (
    <div className="relative">
      <div className="orb orb-cyan w-[300px] h-[300px] -top-20 right-0 animate-orb" />

      <div className="page-container max-w-3xl mx-auto">
        <button onClick={() => navigate('/technician')} className="flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6">
          <ArrowLeft size={16} /> Back to Dashboard
        </button>

        {/* Job Info */}
        <div className="glass-card-static p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-xl font-bold text-white mb-1">{booking.service_name}</h1>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Job #{booking._id?.slice(-8)}</p>
            </div>
            <StatusBadge status={booking.status} />
          </div>

          <div className="glass-card-static p-3 mb-4">
            <p className="text-sm flex items-start gap-2" style={{ color: 'var(--text-secondary)' }}>
              <MessageSquare size={14} className="text-blue-400 mt-0.5 shrink-0" />
              {booking.problem_description}
            </p>
          </div>

          {booking.ai_diagnosis_summary && (
            <div className="p-3 rounded-xl bg-purple-500/5 border border-purple-500/10 mb-4">
              <p className="text-xs font-medium text-purple-400 mb-1">🤖 AI Diagnosis:</p>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                {typeof booking.ai_diagnosis_summary === 'string'
                  ? booking.ai_diagnosis_summary
                  : JSON.stringify(booking.ai_diagnosis_summary)}
              </p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>Customer Address</span>
              <p className="text-white mt-1 text-xs flex items-start gap-1">
                <MapPin size={12} className="mt-0.5 shrink-0" />
                {booking.address}, {booking.city} {booking.pincode}
                {booking.landmark && ` (${booking.landmark})`}
              </p>
            </div>
            <div>
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>Schedule</span>
              <p className="text-white mt-1 text-xs flex items-center gap-1">
                <Calendar size={12} /> {booking.scheduled_date} at {booking.scheduled_time}
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20 mb-6">
            <AlertCircle size={16} className="text-red-400 shrink-0" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Status Actions */}
        {action && (
          <div className="glass-card-static p-6 mb-6">
            <h3 className="font-semibold text-white mb-2">Next Step</h3>
            <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>{action.desc}</p>
            <button
              onClick={() => handleStatusUpdate(action.next)}
              disabled={actionLoading}
              className="btn-primary flex items-center gap-2"
            >
              {actionLoading ? (
                <div className="spinner-3d" style={{ width: 16, height: 16, borderWidth: 2 }} />
              ) : (
                <>
                  <action.icon size={16} />
                  {action.label}
                </>
              )}
            </button>
          </div>
        )}

        {/* Quote Form (during inspection) */}
        {booking.status === 'inspection' && (
          <div className="glass-card-static p-6 mb-6">
            <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
              <FileText size={16} className="text-amber-400" />
              Submit Repair Quote
            </h3>
            <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>
              After inspection, provide the customer with a detailed cost estimate.
            </p>

            <div className="space-y-4">
              <div>
                <label className="label">Labour Charge (₹)</label>
                <input
                  type="number"
                  className="input-field"
                  placeholder="e.g., 500"
                  value={quoteForm.labour_charge}
                  onChange={(e) => setQuoteForm({ ...quoteForm, labour_charge: e.target.value })}
                  min="0"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="label mb-0">Parts Used</label>
                  <button onClick={addPart} className="btn-secondary btn-sm flex items-center gap-1 text-xs">
                    <Plus size={12} /> Add Part
                  </button>
                </div>
                {quoteForm.parts_used.map((part, i) => (
                  <div key={i} className="grid grid-cols-12 gap-2 mb-2">
                    <input
                      className="input-field col-span-5"
                      placeholder="Part name"
                      value={part.name}
                      onChange={(e) => updatePart(i, 'name', e.target.value)}
                    />
                    <input
                      type="number"
                      className="input-field col-span-2"
                      placeholder="Qty"
                      value={part.quantity}
                      onChange={(e) => updatePart(i, 'quantity', e.target.value)}
                      min="1"
                    />
                    <input
                      type="number"
                      className="input-field col-span-4"
                      placeholder="Price ₹"
                      value={part.price}
                      onChange={(e) => updatePart(i, 'price', e.target.value)}
                      min="0"
                    />
                    <button onClick={() => removePart(i)} className="text-red-400 hover:text-red-300 flex items-center justify-center">
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
              </div>

              <div>
                <label className="label">Notes for Customer</label>
                <textarea
                  className="input-field"
                  rows={3}
                  placeholder="Describe what was found and what needs to be done..."
                  value={quoteForm.technician_notes}
                  onChange={(e) => setQuoteForm({ ...quoteForm, technician_notes: e.target.value })}
                />
              </div>

              {/* Quote Preview */}
              <div className="glass-card-static p-4">
                <p className="text-xs font-medium text-slate-400 mb-2">Quote Preview</p>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span style={{ color: 'var(--text-muted)' }}>Visit Charge</span>
                    <span className="text-white">₹{booking.visit_charge || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span style={{ color: 'var(--text-muted)' }}>Inspection</span>
                    <span className="text-white">₹{booking.inspection_charge || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span style={{ color: 'var(--text-muted)' }}>Labour</span>
                    <span className="text-white">₹{quoteForm.labour_charge || 0}</span>
                  </div>
                  {quoteForm.parts_used.map((p, i) => (
                    <div key={i} className="flex justify-between">
                      <span style={{ color: 'var(--text-muted)' }}>{p.name || 'Part'} ×{p.quantity || 1}</span>
                      <span className="text-white">₹{(p.price || 0) * (p.quantity || 1)}</span>
                    </div>
                  ))}
                  <hr style={{ borderColor: 'var(--glass-border)' }} />
                  <div className="flex justify-between font-semibold">
                    <span className="text-white">Total</span>
                    <span className="text-emerald-400">
                      ₹{(booking.visit_charge || 0) + (booking.inspection_charge || 0) +
                        parseFloat(quoteForm.labour_charge || 0) +
                        quoteForm.parts_used.reduce((s, p) => s + (p.price || 0) * (p.quantity || 1), 0)}
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={handleSubmitQuote}
                disabled={actionLoading}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {actionLoading ? (
                  <div className="spinner-3d" style={{ width: 16, height: 16, borderWidth: 2 }} />
                ) : (
                  <>
                    <Send size={16} /> Submit Quote to Customer
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Completed pricing */}
        {booking.final_price > 0 && booking.status !== 'inspection' && (
          <div className="glass-card-static p-6 mb-6">
            <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
              <IndianRupee size={16} className="text-emerald-400" />
              Pricing
            </h3>
            <div className="flex justify-between text-sm font-semibold">
              <span className="text-white">Total</span>
              <span className="text-emerald-400">₹{booking.final_price}</span>
            </div>
            <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
              Payment: {booking.payment_status || 'unpaid'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
