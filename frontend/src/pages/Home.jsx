/**
 * Home — stunning landing page with 3D hero, department cards, stats, and CTA.
 */
import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import API from '../api/axios'
import {
  Sparkles, ArrowRight, Shield, Clock, Star, Zap,
  Wrench, Users, CheckCircle, TrendingUp
} from 'lucide-react'

const FEATURES = [
  {
    icon: Sparkles,
    title: 'AI Problem Diagnosis',
    desc: 'Describe your issue and our AI instantly identifies the problem, suggests solutions, and estimates costs.',
    gradient: 'from-blue-500 to-cyan-500',
  },
  {
    icon: Shield,
    title: 'Verified Technicians',
    desc: 'Every technician is background-verified and skill-tested before being listed on our platform.',
    gradient: 'from-purple-500 to-pink-500',
  },
  {
    icon: Clock,
    title: 'Real-Time Tracking',
    desc: 'Track your service request from booking to completion with live status updates.',
    gradient: 'from-amber-500 to-orange-500',
  },
  {
    icon: Zap,
    title: 'Transparent Pricing',
    desc: 'No hidden charges. See the full breakdown — visit, inspection, labour, and parts — before you approve.',
    gradient: 'from-emerald-500 to-teal-500',
  },
]

const STATS = [
  { value: '500+', label: 'Technicians', icon: Users },
  { value: '10K+', label: 'Bookings', icon: CheckCircle },
  { value: '4.8', label: 'Avg Rating', icon: Star },
  { value: '50+', label: 'Services', icon: Wrench },
]

export default function Home() {
  const [departments, setDepartments] = useState([])

  useEffect(() => {
    API.get('/departments/')
      .then((res) => setDepartments(res.data || []))
      .catch(() => {})
  }, [])

  return (
    <div className="relative overflow-hidden">
      {/* Background Orbs */}
      <div className="orb orb-blue w-[500px] h-[500px] -top-40 -left-40 animate-orb" />
      <div className="orb orb-purple w-[400px] h-[400px] top-20 right-[-100px] animate-orb" style={{ animationDelay: '5s' }} />
      <div className="orb orb-cyan w-[300px] h-[300px] bottom-40 left-1/3 animate-orb" style={{ animationDelay: '10s' }} />

      {/* ── Hero Section ── */}
      <section className="relative py-20 md:py-32 px-4">
        <div className="max-w-7xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 badge-purple mb-6 animate-slide-up">
            <Sparkles size={14} />
            <span>AI-Powered Service Platform</span>
          </div>

          {/* Heading */}
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold leading-tight mb-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            Fix Any Problem<br />
            <span className="text-gradient">With One Click</span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg md:text-xl max-w-2xl mx-auto mb-10 animate-slide-up" style={{ color: 'var(--text-muted)', animationDelay: '0.2s' }}>
            Describe your problem to our AI assistant. We'll diagnose it, match you with the right technician,
            and give you transparent pricing — all before you book.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up" style={{ animationDelay: '0.3s' }}>
            <Link to="/ai-assist" className="btn-primary flex items-center gap-2 text-base px-8 py-4">
              <Sparkles size={18} />
              Try AI Diagnosis
              <ArrowRight size={18} />
            </Link>
            <Link to="/services" className="btn-secondary flex items-center gap-2 text-base px-8 py-4">
              Browse All Services
            </Link>
          </div>
        </div>
      </section>

      {/* ── Stats ── */}
      <section className="relative py-12 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="glass-card-static p-1 rounded-2xl">
            <div className="grid grid-cols-2 md:grid-cols-4">
              {STATS.map((stat, i) => (
                <div key={i} className={`flex flex-col items-center py-6 px-4 ${i < 3 ? 'border-r border-white/5' : ''}`}>
                  <stat.icon size={20} className="text-blue-400 mb-2" />
                  <span className="text-2xl md:text-3xl font-bold text-white">{stat.value}</span>
                  <span className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{stat.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="relative py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="section-title">Why SevaConnect?</h2>
            <p className="section-subtitle mt-2">Everything you need for hassle-free home and vehicle services</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {FEATURES.map((feature, i) => (
              <div
                key={i}
                className="card-3d p-6 group"
                style={{ animationDelay: `${i * 0.1}s` }}
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4 transition-transform duration-500 group-hover:scale-110 group-hover:rotate-3`}>
                  <feature.icon size={22} className="text-white" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-muted)' }}>
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Departments ── */}
      {departments.length > 0 && (
        <section className="relative py-20 px-4 bg-gradient-mesh">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-14">
              <h2 className="section-title">Service Categories</h2>
              <p className="section-subtitle mt-2">Choose a category to explore available services</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {departments.map((dept) => (
                <Link
                  key={dept._id}
                  to={`/services?dept=${dept._id}`}
                  className="card-3d p-5 text-center group"
                >
                  <div className="text-4xl mb-3 transition-transform duration-500 group-hover:scale-125">
                    {dept.icon || '🔧'}
                  </div>
                  <h3 className="text-sm font-semibold text-white">{dept.name}</h3>
                  <p className="text-xs mt-1 line-clamp-2" style={{ color: 'var(--text-muted)' }}>
                    {dept.description || 'Professional services'}
                  </p>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ── How It Works ── */}
      <section className="relative py-20 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="section-title">How It Works</h2>
            <p className="section-subtitle mt-2">Book a service in 3 simple steps</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: '01', title: 'Describe Your Problem', desc: 'Tell our AI what\'s wrong. It will analyze and suggest the right service.', color: 'from-blue-500 to-cyan-500' },
              { step: '02', title: 'Book a Technician', desc: 'Choose a service, pick a time slot, and confirm your booking instantly.', color: 'from-purple-500 to-pink-500' },
              { step: '03', title: 'Get It Fixed', desc: 'A verified technician arrives, inspects, quotes, and fixes your problem.', color: 'from-emerald-500 to-teal-500' },
            ].map((item, i) => (
              <div key={i} className="glass-card p-6 text-center relative">
                <div className={`text-5xl font-black mb-4 bg-gradient-to-br ${item.color} bg-clip-text text-transparent`}>
                  {item.step}
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{item.desc}</p>
                {i < 2 && (
                  <div className="hidden md:block absolute top-1/2 -right-6 transform -translate-y-1/2">
                    <ArrowRight size={20} style={{ color: 'var(--text-muted)' }} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Final CTA ── */}
      <section className="relative py-20 px-4">
        <div className="max-w-3xl mx-auto">
          <div className="glass-card p-10 text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10" />
            <div className="relative">
              <TrendingUp size={40} className="text-blue-400 mx-auto mb-4" />
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-3">Ready to Get Started?</h2>
              <p className="text-sm mb-6" style={{ color: 'var(--text-muted)' }}>
                Join thousands of customers who trust SevaConnect for reliable, affordable home and vehicle services.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
                <Link to="/register" className="btn-primary flex items-center gap-2">
                  Create Free Account
                  <ArrowRight size={16} />
                </Link>
                <Link to="/ai-assist" className="btn-outline flex items-center gap-2">
                  <Sparkles size={16} />
                  Try AI First
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
