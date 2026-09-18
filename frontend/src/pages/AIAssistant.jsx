/**
 * AIAssistant — two-step AI diagnosis flow with chat interface.
 *
 * Step 1: User describes problem → AI returns diagnosis + follow-up questions
 * Step 2: User answers follow-up questions → AI refines diagnosis
 * Then: User can book the recommended service
 */
import { useState } from 'react'
import { Link } from 'react-router-dom'
import API from '../api/axios'
import {
  Sparkles, Send, AlertCircle, Brain, ArrowRight, RefreshCw,
  Lightbulb, CheckCircle, HelpCircle, Wrench, MessageSquare
} from 'lucide-react'

export default function AIAssistant() {
  const [problem, setProblem] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [initialDiagnosis, setInitialDiagnosis] = useState(null)
  const [finalDiagnosis, setFinalDiagnosis] = useState(null)
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [step, setStep] = useState(1) // 1=describe, 2=followup, 3=result

  const handleDiagnose = async (e) => {
    e.preventDefault()
    if (!problem.trim()) return
    setError('')
    setLoading(true)

    try {
      const res = await API.post('/ai/diagnose/', { problem: problem.trim() })
      setSessionId(res.data.session_id)
      setInitialDiagnosis(res.data.initial_diagnosis)
      setStep(2)
    } catch (err) {
      setError(err.response?.data?.error || 'AI service is unavailable right now. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleFollowup = async () => {
    const questions = initialDiagnosis?.follow_up_questions || []
    const answerList = questions.map((q) => ({
      question: q,
      answer: answers[q] || 'Not answered',
    }))

    setError('')
    setLoading(true)

    try {
      const res = await API.post('/ai/followup/', {
        session_id: sessionId,
        answers: answerList,
      })
      setFinalDiagnosis(res.data.final_diagnosis)
      setStep(3)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to get refined diagnosis.')
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setProblem('')
    setSessionId(null)
    setInitialDiagnosis(null)
    setFinalDiagnosis(null)
    setAnswers({})
    setError('')
    setStep(1)
  }

  const diagnosis = finalDiagnosis || initialDiagnosis

  return (
    <div className="relative">
      <div className="orb orb-purple w-[400px] h-[400px] -top-20 left-10 animate-orb" />
      <div className="orb orb-cyan w-[300px] h-[300px] bottom-20 right-10 animate-orb" style={{ animationDelay: '7s' }} />

      <div className="page-container max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 badge-purple mb-4">
            <Brain size={14} />
            Powered by Google Gemini AI
          </div>
          <h1 className="section-title">AI Problem Diagnosis</h1>
          <p className="section-subtitle mt-2">
            Describe your problem in plain language. Our AI will analyze it and suggest the best solution.
          </p>
        </div>

        {/* Step 1: Describe */}
        {step === 1 && (
          <div className="glass-card-static p-6 md:p-8 animate-slide-up">
            <form onSubmit={handleDiagnose}>
              <label className="label flex items-center gap-2">
                <MessageSquare size={16} className="text-blue-400" />
                What's the problem?
              </label>
              <textarea
                className="input-field mb-4"
                rows={4}
                placeholder="E.g., My bike is not starting. The self-start makes a clicking sound but the engine doesn't turn over. The headlight and horn still work fine."
                value={problem}
                onChange={(e) => setProblem(e.target.value)}
                maxLength={1000}
                required
              />
              <div className="flex items-center justify-between">
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  {problem.length}/1000 characters
                </span>
                <button type="submit" disabled={loading || !problem.trim()} className="btn-primary flex items-center gap-2">
                  {loading ? (
                    <div className="spinner-3d" style={{ width: 18, height: 18, borderWidth: 2 }} />
                  ) : (
                    <>
                      <Sparkles size={16} />
                      Diagnose Problem
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Step 2: Follow-up Questions */}
        {step === 2 && initialDiagnosis && (
          <div className="space-y-6 animate-slide-up">
            {/* Initial Diagnosis Card */}
            <div className="glass-card-static p-6">
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb size={18} className="text-amber-400" />
                <h3 className="font-semibold text-white">Initial Assessment</h3>
              </div>
              {initialDiagnosis.problem_summary && (
                <p className="text-sm mb-3" style={{ color: 'var(--text-secondary)' }}>
                  {initialDiagnosis.problem_summary}
                </p>
              )}
              {initialDiagnosis.possible_causes && (
                <div className="mb-3">
                  <p className="text-xs font-medium text-slate-400 mb-2">Possible Causes:</p>
                  <div className="flex flex-wrap gap-2">
                    {(Array.isArray(initialDiagnosis.possible_causes)
                      ? initialDiagnosis.possible_causes
                      : [initialDiagnosis.possible_causes]
                    ).map((cause, i) => (
                      <span key={i} className="badge-yellow badge text-xs">{cause}</span>
                    ))}
                  </div>
                </div>
              )}
              {initialDiagnosis.recommended_service && (
                <div className="flex items-center gap-2 mt-3">
                  <Wrench size={14} className="text-blue-400" />
                  <span className="text-sm text-blue-400 font-medium">
                    Recommended: {initialDiagnosis.recommended_service}
                  </span>
                </div>
              )}
            </div>

            {/* Follow-up Questions */}
            {initialDiagnosis.follow_up_questions?.length > 0 && (
              <div className="glass-card-static p-6">
                <div className="flex items-center gap-2 mb-4">
                  <HelpCircle size={18} className="text-cyan-400" />
                  <h3 className="font-semibold text-white">A few more questions...</h3>
                </div>
                <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>
                  Help us narrow down the problem by answering these:
                </p>
                <div className="space-y-4">
                  {initialDiagnosis.follow_up_questions.map((q, i) => (
                    <div key={i}>
                      <label className="label">{q}</label>
                      <input
                        type="text"
                        className="input-field"
                        placeholder="Type your answer..."
                        value={answers[q] || ''}
                        onChange={(e) => setAnswers({ ...answers, [q]: e.target.value })}
                      />
                    </div>
                  ))}
                </div>
                <div className="flex items-center justify-between mt-6">
                  <button onClick={() => { setStep(3) }} className="btn-secondary btn-sm">
                    Skip Questions
                  </button>
                  <button
                    onClick={handleFollowup}
                    disabled={loading}
                    className="btn-primary flex items-center gap-2"
                  >
                    {loading ? (
                      <div className="spinner-3d" style={{ width: 18, height: 18, borderWidth: 2 }} />
                    ) : (
                      <>
                        Get Refined Diagnosis
                        <ArrowRight size={16} />
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Step 3: Final Result */}
        {step === 3 && diagnosis && (
          <div className="space-y-6 animate-slide-up">
            <div className="glass-card-static p-6 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-blue-500/5" />
              <div className="relative">
                <div className="flex items-center gap-2 mb-4">
                  <CheckCircle size={18} className="text-emerald-400" />
                  <h3 className="font-semibold text-white">
                    {finalDiagnosis ? 'Final Diagnosis' : 'AI Assessment'}
                  </h3>
                  {diagnosis.confidence && (
                    <span className={`badge text-xs ${
                      diagnosis.confidence === 'high' ? 'badge-green' :
                      diagnosis.confidence === 'medium' ? 'badge-yellow' : 'badge-red'
                    }`}>
                      {diagnosis.confidence} confidence
                    </span>
                  )}
                </div>

                {(diagnosis.problem_summary || diagnosis.diagnosis) && (
                  <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
                    {diagnosis.problem_summary || diagnosis.diagnosis}
                  </p>
                )}

                {diagnosis.possible_causes && (
                  <div className="mb-4">
                    <p className="text-xs font-medium text-slate-400 mb-2">Root Causes:</p>
                    <ul className="space-y-1">
                      {(Array.isArray(diagnosis.possible_causes)
                        ? diagnosis.possible_causes
                        : [diagnosis.possible_causes]
                      ).map((c, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                          <span className="text-amber-400 mt-0.5">•</span>
                          {c}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {diagnosis.recommended_service && (
                  <div className="glass-card-static p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Wrench size={20} className="text-blue-400" />
                      <div>
                        <p className="text-sm font-medium text-white">Recommended Service</p>
                        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{diagnosis.recommended_service}</p>
                      </div>
                    </div>
                    <Link to="/services" className="btn-primary btn-sm flex items-center gap-1.5">
                      Book Now <ArrowRight size={14} />
                    </Link>
                  </div>
                )}

                {diagnosis.technician_note && (
                  <div className="mt-4 p-3 rounded-xl bg-blue-500/5 border border-blue-500/10">
                    <p className="text-xs font-medium text-blue-400 mb-1">💡 Tip for the technician:</p>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{diagnosis.technician_note}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="text-center">
              <button onClick={reset} className="btn-secondary flex items-center gap-2 mx-auto">
                <RefreshCw size={16} />
                Diagnose Another Problem
              </button>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 p-4 rounded-xl bg-red-500/10 border border-red-500/20 mt-6">
            <AlertCircle size={16} className="text-red-400 shrink-0" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}
      </div>
    </div>
  )
}
