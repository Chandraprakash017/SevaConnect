/**
 * BookingDetail — full booking info with status timeline, actions, and review.
 * Used by customers to track their booking.
 */
import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import API from '../api/axios'
import { useAuth } from '../context/AuthContext'
import LoadingSpinner from '../components/LoadingSpinner'
import StatusBadge from '../components/StatusBadge'
import StarRating from '../components/StarRating'
import {
  MapPin, Calendar, Clock, Phone, User, FileText,
  CheckCircle, XCircle, IndianRupee, ArrowLeft, Send, MessageSquare
} from 'lucide-react'

const STATUS_ORDER = ['requested', 'assigned', 'on_way', 'inspection', 'waiting_approval', 'in_progress', 'completed']

export default function BookingDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [booking, setBooking] = useState(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [review, setReview] = useState({ rating: 0, comment: '' })
  const [existingReview, setExistingReview] = useState(null)
  const [reviewSubmitting, setReviewSubmitting] = useState(false)
  const [error, setError] = useState('')

  const fetchBooking = () => {
    API.get(`/bookings/${id}/`)
      .then((res) => setBooking(res.data))
      .catch(() => setError('Booking not found'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchBooking()
    // Check if review exists
    API.get(`/bookings/${id}/review/me/`)
      .then((res) => { if (res.data.reviewed) setExistingReview(res.data.review) })
      .catch(() => {})
  }, [id])

  const handleStatusUpdate = async (newStatus) => {
    setActionLoading(true)
    try {
      await API.patch(`/bookings/${id}/status/`, { status: newStatus })
      fetchBooking()
    } catch (err) {
      setError(err.response?.data?.error || 'Action failed')
    }
    setActionLoading(false)
  }

  const submitReview = async () => {
    if (review.rating === 0) return
    setReviewSubmitting(true)
    try {
      const res = await API.post(`/bookings/${id}/review/`, review)
      setExistingReview(res.data)
    } catch (err) {
      setError(err.response?.data?.error || 'Review failed')
    }
    setReviewSubmitting(false)
  }

  if (loading) return <LoadingSpinner text="Loading booking..." />

  if (!booking) {
    return (
      <div className="page-container text-center py-20">
        <p className="text-lg text-white mb-2">Booking not found</p>
        <Link to="/dashboard" className="text-blue-400 hover:underline text-sm">Back to dashboard</Link>
      </div>
    )
  }

  const currentIdx = STATUS_ORDER.indexOf(booking.status)
  const isCancelled = booking.status === 'cancelled'

  return (
    <div className="relative">
      <div className="orb orb-blue w-[300px] h-[300px] -top-20 right-0 animate-orb" />

      <div className="page-container max-w-3xl mx-auto">
        {/* Back */}
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6 transition-colors">
          <ArrowLeft size={16} /> Back
        </button>

        {/* Header */}
        <div className="glass-card-static p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-xl font-bold text-white mb-1">{booking.service_name}</h1>
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                Booking #{booking._id?.slice(-8)}
              </p>
            </div>
            <StatusBadge status={booking.status} />
          </div>

          <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
            <MessageSquare size={14} className="inline mr-1.5 text-blue-400" />
            {booking.problem_description}
          </p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>Location</span>
              <p className="text-white flex items-center gap-1 mt-1"><MapPin size={13} /> {booking.city}</p>
            </div>
            <div>
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>Date</span>
              <p className="text-white flex items-center gap-1 mt-1"><Calendar size={13} /> {booking.scheduled_date}</p>
            </div>
            <div>
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>Time</span>
              <p className="text-white flex items-center gap-1 mt-1"><Clock size={13} /> {booking.scheduled_time}</p>
            </div>
            <div>
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>Address</span>
              <p className="text-white mt-1 text-xs">{booking.address}, {booking.pincode}</p>
            </div>
          </div>
        </div>

        {/* Status Timeline */}
        <div className="glass-card-static p-6 mb-6">
          <h3 className="font-semibold text-white mb-5">Status Timeline</h3>
          <div className="flex items-center gap-1 overflow-x-auto pb-2">
            {STATUS_ORDER.map((s, i) => {
              const isCompleted = !isCancelled && i <= currentIdx
              const isCurrent = !isCancelled && i === currentIdx
              return (
                <div key={s} className="flex items-center">
                  <div className="flex flex-col items-center min-w-[70px]">
                    <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs transition-all ${
                      isCompleted ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30' :
                      isCurrent ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30 animate-pulse-glow' :
                      'bg-white/5 text-slate-600 border border-white/10'
                    }`}>
                      {isCompleted && i < currentIdx ? <CheckCircle size={13} /> : i + 1}
                    </div>
                    <span className={`text-[10px] mt-1.5 text-center ${
                      isCurrent ? 'text-blue-400 font-medium' : 'text-slate-600'
                    }`}>
                      {s.replace('_', ' ')}
                    </span>
                  </div>
                  {i < STATUS_ORDER.length - 1 && (
                    <div className={`w-6 h-0.5 mt-[-16px] ${isCompleted && i < currentIdx ? 'bg-emerald-500' : 'bg-white/10'}`} />
                  )}
                </div>
              )
            })}
            {isCancelled && (
              <div className="flex flex-col items-center min-w-[70px]">
                <div className="w-7 h-7 rounded-full bg-red-500 text-white flex items-center justify-center">
                  <XCircle size={13} />
                </div>
                <span className="text-[10px] mt-1.5 text-red-400 font-medium">Cancelled</span>
              </div>
            )}
          </div>
        </div>

        {/* Pricing */}
        {(booking.final_price > 0 || booking.estimated_min > 0) && (
          <div className="glass-card-static p-6 mb-6">
            <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
              <IndianRupee size={16} className="text-emerald-400" />
              Pricing Breakdown
            </h3>
            <div className="space-y-2 text-sm">
              {booking.visit_charge > 0 && (
                <div className="flex justify-between"><span style={{ color: 'var(--text-muted)' }}>Visit Charge</span><span className="text-white">₹{booking.visit_charge}</span></div>
              )}
              {booking.inspection_charge > 0 && (
                <div className="flex justify-between"><span style={{ color: 'var(--text-muted)' }}>Inspection</span><span className="text-white">₹{booking.inspection_charge}</span></div>
              )}
              {booking.labour_charge > 0 && (
                <div className="flex justify-between"><span style={{ color: 'var(--text-muted)' }}>Labour</span><span className="text-white">₹{booking.labour_charge}</span></div>
              )}
              {booking.parts_used?.length > 0 && booking.parts_used.map((p, i) => (
                <div key={i} className="flex justify-between">
                  <span style={{ color: 'var(--text-muted)' }}>{p.name} ×{p.quantity || 1}</span>
                  <span className="text-white">₹{(p.price || 0) * (p.quantity || 1)}</span>
                </div>
              ))}
              <hr style={{ borderColor: 'var(--glass-border)' }} />
              <div className="flex justify-between font-semibold">
                <span className="text-white">{booking.final_price > 0 ? 'Total' : 'Estimated Range'}</span>
                <span className="text-emerald-400">
                  {booking.final_price > 0 ? `₹${booking.final_price}` : `₹${booking.estimated_min} – ₹${booking.estimated_max}`}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Customer Actions */}
        {user?.role === 'customer' && (
          <div className="space-y-3 mb-6">
            {booking.status === 'requested' && (
              <button onClick={() => handleStatusUpdate('cancelled')} disabled={actionLoading} className="btn-danger w-full flex items-center justify-center gap-2">
                <XCircle size={16} /> Cancel Booking
              </button>
            )}
            {booking.status === 'waiting_approval' && (
              <div className="grid grid-cols-2 gap-3">
                <button onClick={() => handleStatusUpdate('in_progress')} disabled={actionLoading} className="btn-primary flex items-center justify-center gap-2">
                  <CheckCircle size={16} /> Approve Quote
                </button>
                <button onClick={() => handleStatusUpdate('cancelled')} disabled={actionLoading} className="btn-danger flex items-center justify-center gap-2">
                  <XCircle size={16} /> Reject
                </button>
              </div>
            )}
          </div>
        )}

        {/* Invoice Link */}
        {booking.status === 'completed' && booking.invoice_id && (
          <Link to={`/invoice/${booking.invoice_id}`} className="glass-card p-4 flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <FileText size={20} className="text-blue-400" />
              <div>
                <p className="text-sm font-medium text-white">View Invoice</p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Download or print your service invoice</p>
              </div>
            </div>
            <ArrowLeft size={16} className="text-slate-500 rotate-180" />
          </Link>
        )}

        {/* Review */}
        {booking.status === 'completed' && user?.role === 'customer' && (
          <div className="glass-card-static p-6 mb-6">
            <h3 className="font-semibold text-white mb-4">Rate this Service</h3>
            {existingReview ? (
              <div>
                <StarRating rating={existingReview.rating} readonly />
                {existingReview.comment && (
                  <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>{existingReview.comment}</p>
                )}
                <p className="text-xs mt-2 text-emerald-400">✓ Review submitted</p>
              </div>
            ) : (
              <div>
                <StarRating rating={review.rating} onRate={(r) => setReview({ ...review, rating: r })} />
                <textarea
                  className="input-field mt-3"
                  rows={3}
                  placeholder="Share your experience (optional)"
                  value={review.comment}
                  onChange={(e) => setReview({ ...review, comment: e.target.value })}
                />
                <button
                  onClick={submitReview}
                  disabled={review.rating === 0 || reviewSubmitting}
                  className="btn-primary mt-3 flex items-center gap-2"
                >
                  {reviewSubmitting ? (
                    <div className="spinner-3d" style={{ width: 16, height: 16, borderWidth: 2 }} />
                  ) : (
                    <>
                      <Send size={14} /> Submit Review
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20">
            <XCircle size={16} className="text-red-400" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}
      </div>
    </div>
  )
}
