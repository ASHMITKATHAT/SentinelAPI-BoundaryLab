import { Component, FormEvent, Fragment, ReactNode, useCallback, useEffect, useMemo, useRef, useState, useSyncExternalStore } from 'react'
import { api, getApiStatus, subscribeApiStatus } from './api'
import { ApiError } from './http'
import type { CandidateReview, Capabilities, CaseResult, Comparison, DiscoveryAnalysis, Evidence, Explanation, PolicySummary, Report, Run, RunEvent, SpecSummary, Target, Verdict } from './types'

type View = 'overview' | 'runs' | 'discovery' | 'policy' | 'compare' | 'reports'
type StageView = Exclude<View, 'overview'>

const viewMeta: Record<View, { index: string; label: string; short: string; icon: IconName }> = {
  overview: { index: '00', label: 'Mentor walkthrough', short: 'Start', icon: 'home' },
  discovery: { index: '01', label: 'API discovery', short: 'Discover', icon: 'radar' },
  policy: { index: '02', label: 'Policy contract', short: 'Define', icon: 'shield' },
  runs: { index: '03', label: 'Verification runs', short: 'Verify', icon: 'pulse' },
  compare: { index: '04', label: 'Repair compare', short: 'Compare', icon: 'compare' },
  reports: { index: '05', label: 'Evidence handoff', short: 'Handoff', icon: 'report' },
}

const stageOrder: StageView[] = ['discovery', 'policy', 'runs', 'compare', 'reports']

const stageGuide: Record<StageView, { question: string; proof: string; features: string[] }> = {
  discovery: { question: 'Where could protected data escape?', proof: 'Show the API inventory, ownership candidates and any route seen in traffic but missing from the contract.', features: ['OpenAPI inventory', 'HAR route diff', 'Shadow route detection'] },
  policy: { question: 'Who is allowed to see which data, and when?', proof: 'Show that business promises become versioned, hashed acceptance cases before requests are sent.', features: ['Ownership rules', 'Field-level privacy', 'Revocation deadline'] },
  runs: { question: 'Does the real permission journey behave correctly?', proof: 'Show the request timeline, post-revoke export probe, case verdicts, sanitized evidence and repair guidance.', features: ['Lifecycle replay', 'Multiple identities', 'Evidence + remediation'] },
  compare: { question: 'Did the fix close the leak without breaking the product?', proof: 'Compare the old build with the candidate and point to fixed, preserved, regressed and unresolved cases.', features: ['Regression proof', 'Release decision', 'No deny-everyone fix'] },
  reports: { question: 'Can engineering, security and CI use the result?', proof: 'Export a human report or machine evidence bundle tied to the tested build and policy.', features: ['HTML handoff', 'JSON evidence', 'CI/CD gate'] },
}

type IconName = 'home' | 'radar' | 'shield' | 'pulse' | 'compare' | 'report' | 'chevron' | 'refresh' | 'lock' | 'alert'

function Icon({ name, size = 17 }: { name: IconName; size?: number }) {
  const paths: Record<IconName, ReactNode> = {
    home: <><path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10.5V20h13v-9.5M9.5 20v-6h5v6"/></>,
    radar: <><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 2v2M22 12h-2M12 22v-2M2 12h2M14.2 9.8l4-4"/></>,
    shield: <><path d="M12 3 19 6v5c0 4.7-2.8 8-7 10-4.2-2-7-5.3-7-10V6l7-3Z"/><path d="m9 12 2 2 4-5"/></>,
    pulse: <><path d="M3 12h4l2-6 4 12 2-6h6"/></>,
    compare: <><path d="M7 4 3 8l4 4M3 8h14M17 20l4-4-4-4M21 16H7"/></>,
    report: <><path d="M6 3h9l3 3v15H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/></>,
    chevron: <path d="m9 18 6-6-6-6"/>,
    refresh: <><path d="M20 6v5h-5M4 18v-5h5"/><path d="M18.5 9A7 7 0 0 0 6 6.5L4 9M5.5 15A7 7 0 0 0 18 17.5l2-2.5"/></>,
    lock: <><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></>,
    alert: <><path d="M12 3 2.8 20h18.4L12 3Z"/><path d="M12 9v5M12 17h.01"/></>,
  }
  return <svg className="icon" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>
}

class AppErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false }
  static getDerivedStateFromError() { return { failed: true } }
  render() {
    if (!this.state.failed) return this.props.children
    return <main className="fatal-state"><div className="mark mark-large">B</div><div className="fatal-copy"><p className="eyebrow">Workbench recovery</p><h1>The interface hit an unexpected state.</h1><p>Your persisted runs and evidence are safe. Reload the local console to rebuild the view from the control API.</p><button className="button primary" onClick={() => window.location.reload()}>Reload workbench</button></div></main>
  }
}

const verdictLabel: Record<Verdict, string> = {
  pass: 'Pass', violation: 'Violation', inconclusive: 'Inconclusive', skipped: 'Skipped',
}

function identityLabel(identity: string) {
  return ({ alice: 'resource owner', bob: 'temporary user', mallory: 'external tenant', anonymous: 'anonymous' } as Record<string, string>)[identity.toLowerCase()] || identity
}

function caseLabel(name: string) {
  return name.replaceAll('Alice', 'Resource owner').replaceAll('Bob', 'Temporary user').replaceAll('Mallory', 'External tenant')
}

function StatusBadge({ value }: { value: string | null }) {
  const normalized = (value || 'pending').replaceAll('_', '-')
  return <span className={`status status-${normalized}`}>{(value || 'Pending').replaceAll('_', ' ')}</span>
}

function Login({ onLogin }: { onLogin: () => void }) {
  const [secret, setSecret] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [showSecret, setShowSecret] = useState(false)
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('')
    const normalizedSecret = secret.trim()
    if (normalizedSecret.length < 16) { setError('Paste only the bootstrap secret. It must contain at least 16 characters.'); setBusy(false); return }
    try { await Promise.all([api.login(normalizedSecret), new Promise(resolve => window.setTimeout(resolve, 500))]); onLogin() }
    catch (caught) {
      setError(caught instanceof ApiError && caught.status === 401
        ? 'Secret rejected by this running server. Copy the exact value after “Bootstrap secret” without bullets, backticks or extra spaces.'
        : caught instanceof Error ? caught.message : 'Login failed')
    }
    finally { setBusy(false) }
  }
  return <main className="login-shell">
    <section className="login-brand" aria-label="BoundaryLab overview">
      <div className="mark mark-large">B</div><p className="eyebrow light">SentinelAPI / AmiHacks</p>
      <h1>Prove the boundary.<br/><span>Preserve the product.</span></h1>
      <p>Run bounded authorization checks against an API you control and keep reviewable, redacted evidence.</p>
      <div className="login-proof"><b>GET</b><span>read-only real probes</span><b>0</b><span>secrets persisted</span></div>
    </section>
    <section className="login-card">
      <p className="eyebrow">Local operator access</p><h2>Open the workbench</h2>
      <p className="muted">Enter the one-time secret printed by the local server. The secret stays in this request and is never stored by the browser.</p>
      <form onSubmit={submit} aria-busy={busy}>
        <label htmlFor="secret">Bootstrap secret</label>
        <div className="secret-field"><input id="secret" type={showSecret ? 'text' : 'password'} autoComplete="current-password" minLength={16} required disabled={busy} value={secret} onChange={e => setSecret(e.target.value)} /><button type="button" disabled={busy} onClick={() => setShowSecret(current => !current)} aria-label={showSecret ? 'Hide secret value' : 'Reveal secret value'}>{showSecret ? 'Hide' : 'Show'}</button></div>
        {error && <p className="form-error" role="alert">{error}</p>}
        {busy && <div className="login-progress" role="status" aria-live="polite"><div className="spinner"/><div><strong>Creating secure local session…</strong><span>Checking the running server, then loading targets, policy and saved evidence.</span><div className="loading-track"><i/></div></div></div>}
        <button className="button primary wide" disabled={busy}>{busy ? 'Connecting to BoundaryLab…' : 'Enter BoundaryLab'}</button>
      </form>
      <p className="micro">Local single-operator profile · bound to 127.0.0.1</p>
    </section>
  </main>
}

function SideNav({ view, setView, logout, activeRuns }: { view: View; setView: (view: View) => void; logout: () => void; activeRuns: number }) {
  const items: View[] = ['overview', ...stageOrder]
  return <aside className="sidebar">
    <div><div className="brand"><div className="mark">B</div><div><strong>BoundaryLab</strong><small>SentinelAPI · v0.3.2</small></div></div>
      <p className="nav-section">Release workflow</p>
      <nav aria-label="Product navigation">{items.map(id =>
        <button key={id} className={view === id ? 'active' : ''} onClick={() => setView(id)} aria-current={view === id ? 'page' : undefined}>
          <Icon name={viewMeta[id].icon}/><span className="nav-label"><b>{viewMeta[id].short}</b><small>{viewMeta[id].label}</small></span>{id === 'runs' && activeRuns > 0 && <em>{activeRuns}</em>}
        </button>)}</nav>
    </div>
    <div className="side-context"><Icon name="lock"/><div><strong>Local trusted scope</strong><span>Loopback control plane</span></div></div>
    <div className="side-footer"><span>Operator session</span><button className="text-button" onClick={logout}>Sign out</button></div>
  </aside>
}

function WorkspaceHeader({ view, activeRuns, policyLabel, connected }: { view: View; activeRuns: number; policyLabel: string; connected: boolean }) {
  return <header className="topbar"><div className="breadcrumbs"><span className="stage-index">{viewMeta[view].index}</span><strong>{viewMeta[view].label}</strong></div><div className="topbar-actions"><span className={`control-status ${connected ? '' : 'offline'}`}><i/>{connected ? activeRuns ? `${activeRuns} run${activeRuns > 1 ? 's' : ''} active` : 'Ready' : 'Server offline'}</span><span className="policy-pill"><code>{policyLabel}</code></span></div></header>
}

function WorkflowRail({ view, setView }: { view: View; setView: (view: View) => void }) {
  if (view === 'overview') return null
  return <nav className="workflow-rail" aria-label="Five-stage mentor walkthrough">
    {stageOrder.map(id => <button key={id} className={view === id ? 'current' : ''} onClick={() => setView(id)} aria-label={`${viewMeta[id].index} ${viewMeta[id].short}: ${stageGuide[id].question}`} aria-current={view === id ? 'step' : undefined}>
      <span>{viewMeta[id].index}</span><b>{viewMeta[id].short}</b>
    </button>)}
  </nav>
}

function StageBrief({ view, setView }: { view: StageView; setView: (view: View) => void }) {
  const guide = stageGuide[view]
  const currentIndex = stageOrder.indexOf(view)
  const next = stageOrder[currentIndex + 1]
  return <section className="stage-brief" aria-label={`${viewMeta[view].short} mentor guide`}>
    <div className="stage-brief-number">{viewMeta[view].index}</div>
    <div><p className="eyebrow">Question this stage answers</p><h2>{guide.question}</h2><p>{guide.proof}</p><div className="feature-chips">{guide.features.map(feature => <span key={feature}>{feature}</span>)}</div></div>
    <button className="button secondary compact" onClick={() => setView(next || 'overview')}>{next ? `Next: ${viewMeta[next].short}` : 'Back to overview'} <span aria-hidden="true">→</span></button>
  </section>
}

function MentorOverview({ setView, runs, targets, capabilities }: { setView: (view: View) => void; runs: Run[]; targets: Target[]; capabilities: Capabilities | null }) {
  const completed = runs.filter(run => run.state === 'completed')
  const violationCount = completed.reduce((total, run) => total + run.counts.violation, 0)
  const featureGroups = [
    { label: 'Discover', title: 'Find every data door', question: 'Where could data escape?', body: 'Map OpenAPI operations, infer ownership-sensitive routes and compare captured traffic to reveal undeclared shadow routes.', features: ['OpenAPI mapping', 'HAR traffic diff', 'Ownership candidates', 'Shadow APIs'], view: 'discovery' as View },
    { label: 'Define', title: 'Turn access promises into tests', question: 'Who should see what?', body: 'Bind identities, owner-only fields and revocation timing to a versioned policy before any active request runs.', features: ['Role expectations', 'Field privacy', 'Revocation SLA', 'Hashed policy'], view: 'policy' as View },
    { label: 'Verify', title: 'Replay the permission journey', question: 'Does revoke really work?', body: 'Exercise access before sharing, during sharing and after revoke—including old exports—then keep redacted case-level proof.', features: ['Identity isolation', 'Export-after-revoke', 'Evidence timeline', 'Root-cause guidance'], view: 'runs' as View },
    { label: 'Compare', title: 'Prove the repair is safe', question: 'Did the fix break anything?', body: 'Compare an old build with a release candidate and separate repaired controls from preserved behavior and regressions.', features: ['Fixed cases', 'Preserved behavior', 'Regression detection', 'Release Gate'], view: 'compare' as View },
    { label: 'Handoff', title: 'Make the proof reusable', question: 'Can the team act on it?', body: 'Export human and machine evidence, connect the same deterministic verdict to CI and retain a build-specific audit trail.', features: ['HTML report', 'JSON evidence', 'CI/CD exit gate', 'SHA-256 trace'], view: 'reports' as View },
  ]
  return <>
    <section className="mentor-hero">
      <div><p className="eyebrow light">Mentor walkthrough · start here</p><h1>One permission story.<br/><span>Five layers of proof.</span></h1><p>BoundaryLab finds every API door, defines who may use it, tests the full access lifecycle, proves the repair and packages the result for release.</p><div className="mentor-actions"><button className="button primary" onClick={() => setView('discovery')}>Start the 5-step demo</button><button className="button dark-secondary" onClick={() => setView('runs')}>Open live evidence</button></div></div>
      <div className="breach-story"><p className="eyebrow light">The breach in four moments</p><ol><li><span>1</span><div><strong>Temporary access works</strong><small>A partner can read an invoice and create an export.</small></div></li><li><span>2</span><div><strong>Access is revoked</strong><small>The main screen correctly hides the invoice.</small></div></li><li className="danger"><span>3</span><div><strong>An old API door stays open</strong><small>The saved export URL still returns protected data.</small></div></li><li><span>4</span><div><strong>BoundaryLab proves the fix</strong><small>The old door returns deny while valid access still works.</small></div></li></ol></div>
    </section>
    <section className="live-proof-strip" aria-label="Current workspace proof"><div><span>Persisted runs</span><strong>{completed.length}</strong></div><div className={violationCount ? 'danger' : ''}><span>Observed violations</span><strong>{violationCount}</strong></div><div><span>Target modes</span><strong>{targets.some(target => !target.synthetic_fixture) ? 'Lab + staging' : 'Disclosed lab'}</strong></div><div><span>AI role</span><strong>{capabilities?.remediation.ai_configured ? 'Optional review ready' : 'Optional · verdicts stay deterministic'}</strong></div></section>
    <section className="mentor-section-head"><div><p className="eyebrow">Complete product journey</p><h2>Show these stages in order.</h2><p>Every card answers one mentor question and opens the exact working screen that proves it.</p></div><span>Click any stage to inspect it</span></section>
    <section className="feature-journey">{featureGroups.map((group, index) => <article className="card journey-card" key={group.label}><div className="journey-top"><span>{String(index + 1).padStart(2, '0')}</span><p>{group.label}</p></div><p className="journey-question">{group.question}</p><h3>{group.title}</h3><p className="journey-body">{group.body}</p><div className="feature-list">{group.features.map(feature => <span key={feature}>✓ {feature}</span>)}</div><button className="journey-link" aria-label={`Show ${group.label} proof`} onClick={() => setView(group.view)}>Show this proof <Icon name="chevron" size={13}/></button></article>)}</section>
    <section className="production-proof card"><div><p className="eyebrow">Built for a real staging boundary</p><h2>The demo is disclosed. The execution path is production-shaped.</h2><p>Real mode binds one reviewed OpenAPI operation to allowlisted loopback or forwarded staging origins. Credentials stay in environment references; browser-supplied URLs, redirects and raw secrets are rejected.</p></div><div className="production-facts"><span><Icon name="lock"/>GET-only real probe</span><span><Icon name="shield"/>HttpOnly + CSRF session</span><span><Icon name="pulse"/>Bounded requests + cancellation</span><span><Icon name="report"/>Redacted, hashed evidence</span></div></section>
  </>
}

function RunList({ runs, selected, select }: { runs: Run[]; selected?: string; select: (run: Run) => Promise<void> }) {
  return <div className="run-list" aria-label="Recent runs">
    {runs.length === 0 && <div className="empty-small"><Icon name="pulse"/><strong>No verification runs yet</strong><span>Choose a ready target to create evidence.</span></div>}
    {runs.map(run => <button key={run.id} className={selected === run.id ? 'run-row selected' : 'run-row'} onClick={() => void select(run)}>
      <div className="run-row-main"><span className="run-glyph"><Icon name="pulse" size={15}/></span><span><strong>{run.target_alias.replace('demo-', '')}</strong><small>{new Date(run.created_at).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})} · {run.id.slice(-6)}</small></span></div>
      <div className="run-row-end"><StatusBadge value={run.assessment || run.state}/><Icon name="chevron" size={14}/></div>
    </button>)}
  </div>
}

function Timeline({ report }: { report: Report }) {
  const picked: Evidence[] = report.policy_version === 'read-boundary-v1' ? report.evidence : []
  if (!picked.length) {
    const operations = ['grantShare', 'queueExport', 'getExportContent', 'revokeShare', 'getMe', 'getExportContent']
    let cursor = 0
    for (const operation of operations) {
      const found = report.evidence.find((item, index) => index >= cursor && item.operation_id === operation)
      if (found) { picked.push(found); cursor = report.evidence.indexOf(found) + 1 }
    }
  }
  return <div className="timeline">{picked.map((item, index) =>
    <div className={`timeline-step ${item.status_code && item.status_code >= 400 ? 'denied' : ''}`} key={`${item.evidence_id}-${index}`}>
      <span className="time">+{item.start_offset_ms} ms</span><i>{index + 1}</i><strong>{item.operation_id}</strong><small>{identityLabel(item.identity)} · HTTP {item.status_code}</small>
    </div>)}</div>
}

function EvidenceDrawer({ evidence, close }: { evidence: Evidence; close: () => void }) {
  const closeButton = useRef<HTMLButtonElement>(null)
  useEffect(() => {
    const previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    closeButton.current?.focus()
    const onKeyDown = (event: KeyboardEvent) => { if (event.key === 'Escape') close() }
    window.addEventListener('keydown', onKeyDown)
    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', onKeyDown)
      previousFocus?.focus()
    }
  }, [close])
  return <div className="drawer-backdrop" onMouseDown={event => { if (event.currentTarget === event.target) close() }}>
    <aside className="drawer" role="dialog" aria-modal="true" aria-labelledby="evidence-title">
      <div className="drawer-head"><div><p className="eyebrow">Sanitized evidence</p><h2 id="evidence-title">{evidence.operation_id}</h2></div><button ref={closeButton} className="icon-button" onClick={close} aria-label="Close evidence">×</button></div>
      <dl className="evidence-facts"><div><dt>Identity</dt><dd>{evidence.identity}</dd></div><div><dt>Status</dt><dd>HTTP {evidence.status_code}</dd></div><div><dt>Started</dt><dd>+{evidence.start_offset_ms} ms</dd></div><div><dt>Duration</dt><dd>{evidence.duration_ms} ms</dd></div></dl>
      <h3>Request</h3><pre>{`${evidence.method} ${evidence.path}\n${Object.entries(evidence.request_headers).map(([key,value]) => `${key}: ${value}`).join('\n')}`}</pre>
      <h3>Allowlisted response excerpt</h3><pre>{JSON.stringify(evidence.response_excerpt, null, 2)}</pre>
      <p className="hash">SHA-256 · {evidence.sha256}</p>
      <div className="notice">Credentials and unrestricted response bodies are removed before persistence.</div>
    </aside>
  </div>
}

const activityLabels: Record<string, string> = {
  queued: 'Run accepted',
  running: 'Worker claimed',
  scope_verified: 'Safety scope verified',
  executing: 'Cases executing',
  evidence_sealed: 'Evidence sealed',
  completed: 'Verdict ready',
  failed: 'Run failed',
  interrupted: 'Run interrupted',
  cancelled: 'Run cancelled',
}

function RunActivity({ run }: { run: Run }) {
  const [events, setEvents] = useState<RunEvent[]>([])
  const [error, setError] = useState('')
  const active = ['queued', 'running'].includes(run.state)
  useEffect(() => {
    let disposed = false
    async function load() {
      try {
        const result = await api.runEvents(run.id)
        if (!disposed) { setEvents(result.events); setError('') }
      } catch (caught) {
        if (!disposed) setError(caught instanceof Error ? caught.message : 'Execution activity unavailable')
      }
    }
    setEvents([]); setError(''); void load()
    if (!active) return () => { disposed = true }
    const timer = window.setInterval(() => void load(), 700)
    return () => { disposed = true; window.clearInterval(timer) }
  }, [run.id, active])
  return <section className={`card execution-activity ${active ? 'is-live' : ''}`} aria-label="Persisted execution activity">
    <div className="section-head"><div><p className="eyebrow">Actual backend activity</p><h3>Execution trace</h3></div><span className={active ? 'live-badge' : 'audit-badge'}><i/>{active ? 'Live' : 'Persisted audit trail'}</span></div>
    <p className="activity-intro">These events come from the worker and database. They are not simulated interface steps.</p>
    {error && <p className="form-error" role="alert">{error}</p>}
    {!error && events.length === 0 && <div className="activity-loading"><div className="spinner"/><span>Reading persisted run events…</span></div>}
    {events.length > 0 && <div className="execution-stream" role="log" aria-live="polite">{events.map((event, index) => <article className={`execution-event event-${event.type}`} key={event.id}><div className="event-meta"><span>{String(index + 1).padStart(2,'0')}</span><time>{new Date(event.created_at).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'})}</time></div><strong>{activityLabels[event.type] || event.type.replaceAll('_',' ')}</strong><p>{event.message.replaceAll('demo-','')}</p></article>)}</div>}
  </section>
}

function RemediationPanel({ run, capabilities }: { run: Run; capabilities: Capabilities | null }) {
  const [result, setResult] = useState<Explanation | null>(null)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  async function explain(mode: 'deterministic' | 'ai') {
    setBusy(mode); setError('')
    try { setResult(await api.explain(run.id, mode)) }
    catch (caught) { setError(caught instanceof Error ? caught.message : 'Remediation analysis failed') }
    finally { setBusy('') }
  }
  return <section className="card remediation">
    <div className="section-head"><div><p className="eyebrow">Root cause + repair</p><h3>Remediation workspace</h3></div>{result && <span className="scope-chip">{result.mode === 'openai_structured' ? `AI · ${result.model}` : 'Deterministic'}</span>}</div>
    <p className="muted">Generate a reviewable guard outline from failed policy cases. Deterministic mode never sends data outside this process.</p>
    <div className="remediation-actions"><button className="button secondary" disabled={!!busy} onClick={() => explain('deterministic')}>{busy === 'deterministic' ? 'Analyzing…' : 'Deterministic triage'}</button><button className="button primary" disabled={!!busy || !capabilities?.remediation.ai_configured} onClick={() => explain('ai')}>{busy === 'ai' ? 'Calling model…' : capabilities?.remediation.ai_configured ? `AI review · ${capabilities.remediation.model}` : 'AI provider not configured'}</button></div>
    {capabilities?.remediation.ai_configured && <p className="micro muted">AI mode sends only failed-case summaries after this explicit click. Raw headers, tokens and response bodies stay local.</p>}
    {error && <p className="form-error" role="alert">{error}</p>}
    {result && <div className="remediation-result"><div className={`risk risk-${result.risk}`}>{result.risk} risk</div><h4>{result.summary}</h4>{result.root_causes.length > 0 && <div className="root-causes">{result.root_causes.map(cause => <article key={`${cause.case_id}-${cause.category}`}><code>{cause.case_id}</code><strong>{cause.category.replaceAll('_',' ')}</strong><p>{cause.explanation}</p><p className="guard">{cause.recommended_guard}</p></article>)}</div>}<div className="repair-grid"><div><h4>Repair steps</h4><ol>{result.remediation_steps.map(item => <li key={item}>{item}</li>)}</ol></div><div><h4>Regression checks</h4><ul>{result.regression_checks.map(item => <li key={item}>{item}</li>)}</ul></div></div><h4>Patch outline</h4><pre>{result.patch_outline}</pre><p className="micro muted">{result.limitations.join(' ')}</p></div>}
  </section>
}

function RunDetail({ run, cancel, capabilities }: { run: Run | null; cancel: (id: string) => void; capabilities: Capabilities | null }) {
  const [evidence, setEvidence] = useState<Evidence | null>(null)
  if (!run) return <section className="empty-state"><div className="empty-icon">↗</div><h2>Select or start a run</h2><p>Actual evidence and policy outcomes will appear here.</p></section>
  const report = run.report
  const realProbe = report?.policy_version === 'read-boundary-v1'
  const openCase = (item: CaseResult) => {
    const found = report?.evidence.find(e => item.evidence_ids.includes(e.evidence_id)); if (found) setEvidence(found)
  }
  return <>
    <section className="run-hero card">
      <div><p className="eyebrow">{realProbe ? 'Real staging boundary' : 'Permission lifecycle'} / {run.id}</p><h2>{realProbe ? 'Do the configured identities respect this resource boundary?' : 'Can a temporary user still retrieve the invoice after access is revoked?'}</h2><p className="muted">Target <code>{run.target_alias}</code> · build <code>{run.build_id || 'pending'}</code></p></div>
      <div className="hero-status"><StatusBadge value={run.assessment || run.state}/>{!['completed','failed','interrupted','cancelled'].includes(run.state) && <button className="button secondary compact" onClick={() => cancel(run.id)}>Cancel</button>}</div>
    </section>
    <RunActivity run={run}/>
    {!report && <section className="card working"><div className="spinner"/><div><h3>{run.state === 'queued' ? 'Waiting for the single safe worker' : 'Executing bounded target requests'}</h3><p>State and evidence are persisted. Refreshing this page will not lose the run.</p></div></section>}
    {report && <>
      {report.execution_error && <section className="notice" role="alert"><strong>Run incomplete.</strong> {report.execution_error}</section>}
      <section className="metrics"><div><span>Pass</span><b>{report.counts.pass}</b></div><div className={report.counts.violation ? 'metric-danger' : 'metric-clear'}><span>Violations</span><b>{report.counts.violation}</b></div><div><span>Inconclusive</span><b>{report.counts.inconclusive}</b></div><div><span>Requests</span><b>{report.request_count}</b></div></section>
      <section className="card"><div className="section-head"><div><p className="eyebrow">Observed requests</p><h3>{realProbe ? 'One bounded read per identity' : 'Follow the permission'}</h3></div><span className="scope-chip">{realProbe ? 'GET only · redirects blocked' : '2,000 ms grace · 200 ms margin'}</span></div><Timeline report={report}/></section>
      <section className="card"><div className="section-head"><div><p className="eyebrow">Policy acceptance</p><h3>{report.cases.length} required cases</h3></div><span className="muted micro">Cleanup: {report.cleanup_status}</span></div>
        <div className="table-scroll"><table><thead><tr><th>Case</th><th>Permission promise</th><th>Expected</th><th>Observed</th><th>Verdict</th></tr></thead><tbody>
          {report.cases.map(item => <tr key={item.case_id} className={item.evidence_ids.length ? 'clickable' : ''} tabIndex={item.evidence_ids.length ? 0 : undefined} aria-label={item.evidence_ids.length ? `Open evidence for ${item.case_id}: ${item.name}` : undefined} onClick={event => { event.currentTarget.focus(); openCase(item) }} onKeyDown={event => { if (item.evidence_ids.length && (event.key === 'Enter' || event.key === ' ')) { event.preventDefault(); openCase(item) } }}>
            <td><code>{item.case_id}</code></td><td><strong>{caseLabel(item.name)}</strong>{item.reason_code && <small>{item.reason_code}</small>}</td><td>{item.expected}</td><td>{item.observed}</td><td><StatusBadge value={item.verdict}/></td>
          </tr>)}</tbody></table></div>
      </section>
      <RemediationPanel run={run} capabilities={capabilities}/>
    </>}
    {evidence && <EvidenceDrawer evidence={evidence} close={() => setEvidence(null)}/>}
  </>
}

function RunsView({ targets, targetAlias, onTargetChange, runs, selectedRun, select, refresh, capabilities }: { targets: Target[]; targetAlias: string; onTargetChange: (alias: string) => void; runs: Run[]; selectedRun: Run | null; select: (run: Run) => Promise<void>; refresh: () => Promise<void>; capabilities: Capabilities | null }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [activity, setActivity] = useState('')
  const selectedTarget = targets.find(item => item.alias === targetAlias) || null
  const labTargets = targets.filter(item => item.synthetic_fixture && item.ready)
  async function start(alias: string) { setBusy(true); setError(''); setActivity(`Creating a bounded run for ${alias.replace('demo-','')}…`); try { const run = await api.startRun(alias); setActivity('Run accepted. Restoring its live state…'); await refresh(); await select(run) } catch (e) { setError(e instanceof Error ? e.message : 'Could not start run') } finally { setBusy(false); setActivity('') } }
  async function matrix() { setBusy(true); setError(''); try { let first: Run | null = null; for (const [index, item] of labTargets.entries()) { setActivity(`Queueing build ${index + 1} of ${labTargets.length}: ${item.label}`); const run = await api.startRun(item.alias); first ||= run } setActivity(`${labTargets.length} builds queued. The safe worker will execute them one at a time.`); await refresh(); if (first) await select(first) } catch (e) { setError(e instanceof Error ? e.message : 'Could not queue lab matrix') } finally { setBusy(false); setActivity('') } }
  async function cancel(id: string) { try { await api.cancelRun(id); await refresh() } catch (e) { setError(e instanceof Error ? e.message : 'Cancellation failed') } }
  async function refreshRuns() { setError(''); try { await refresh() } catch (e) { setError(e instanceof Error ? e.message : 'Could not refresh runs') } }
  const completed = runs.filter(run => run.state === 'completed')
  const activeItems = runs.filter(run => ['queued','running'].includes(run.state))
  const violations = completed.reduce((sum, run) => sum + (run.counts.violation || 0), 0)
  const realMode = selectedTarget?.mode === 'real_read_probe'
  const noTargets = targets.length === 0
  return <><header className="page-head"><div><p className="eyebrow">Runtime verification</p><h1>{noTargets ? 'Connect a target to begin.' : realMode ? 'Test a real access boundary.' : 'Prove access stays revoked.'}</h1><p>{noTargets ? 'Active requests remain disabled until a reviewed staging registry or explicit lab mode is loaded.' : realMode ? 'Send one bounded GET per reviewed identity and keep only redacted proof.' : 'Replay the disclosed sharing lifecycle and see exactly where the permission boundary holds or breaks.'}</p></div><div className="demo-flag"><i/>{realMode ? 'Authorized staging' : targets.length ? 'Disclosed lab' : 'No target configured'}</div></header>
    <section className="overview-strip" aria-label="Verification overview"><div><span>Completed runs</span><strong>{completed.length}</strong></div><div className={violations ? 'danger' : ''}><span>Recorded violations</span><strong>{violations}</strong></div><div><span>Required cases</span><strong>{selectedTarget?.case_count || 0} / run</strong></div><div><span>Evidence mode</span><strong>Redacted + hashed</strong></div></section>
    {(busy || activeItems.length > 0) && <section className="run-progress card" role="status" aria-live="polite"><div className="spinner"/><div><p className="eyebrow">Live verification progress</p><h2>{activity || `${activeItems.length} run${activeItems.length === 1 ? '' : 's'} still processing`}</h2><p>{activeItems.length > 0 ? 'One bounded worker executes requests at a time. The page refreshes automatically and evidence is persisted after every run.' : 'Preparing the trusted target and queue entry. No arbitrary destination or browser credential can be added here.'}</p><div className="loading-track"><i/></div><div className="active-run-chips">{activeItems.map(run => <span key={run.id}><b>{run.target_alias.replace('demo-','')}</b> · {run.state}</span>)}</div></div></section>}
    {targets.length === 0 ? <section className="card target-setup"><span className="setup-icon"><Icon name="lock" size={22}/></span><div><p className="eyebrow">Active testing disabled by default</p><h2>Connect an authorized staging target</h2><p>Start BoundaryLab with a reviewed target registry. Real mode accepts a fixed GET operation on numeric loopback only, so use a local service or an SSH-forwarded staging port. Tokens, resource IDs and proof markers come from environment references and are never accepted from the browser.</p><code>python -m boundarylab.devserver --target-config .\targets\registry.json</code></div></section> :
    <section className="launch card"><div className="launch-copy"><div><h2>Run a verification</h2><p>{realMode ? `Fixed read probe through ${selectedTarget?.origin}` : 'Choose a disclosed lab build. Requests remain inside the local fixture.'}</p><div className="assurance-row"><span><Icon name="lock" size={13}/>Allowlisted</span><span>{selectedTarget?.limits.requests || 0} requests max</span><span>1 at a time</span><span>No redirects</span></div></div></div><div className="launch-actions"><label htmlFor="target">Target to test</label><select id="target" value={targetAlias} onChange={e => onTargetChange(e.target.value)}>{targets.map(item => <option value={item.alias} key={item.alias} disabled={!item.ready}>{item.label}{item.ready ? '' : ' · missing environment'}</option>)}</select><button className="button primary" onClick={() => selectedTarget && start(selectedTarget.alias)} disabled={busy || !selectedTarget?.ready}>{busy ? 'Queueing…' : 'Run verification'}</button>{labTargets.length > 1 && <button className="button secondary" onClick={matrix} disabled={busy}>Run lab matrix</button>}</div>{selectedTarget && !selectedTarget.ready && <p className="form-error full" role="alert">Missing runtime environment references: {selectedTarget.missing_environment.join(', ')}</p>}{error && <p className="form-error full" role="alert">{error}</p>}</section>}
    <div className="workspace-grid"><section className="card recent"><div className="section-head"><div><p className="eyebrow">Evidence index</p><h3>Recent runs</h3></div><button className="icon-button" onClick={() => void refreshRuns()} aria-label="Refresh runs"><Icon name="refresh"/></button></div><RunList runs={runs} selected={selectedRun?.id} select={select}/></section><div className="detail-column"><RunDetail run={selectedRun} cancel={cancel} capabilities={capabilities}/></div></div>
  </>
}

function DiscoveryView({ spec }: { spec: SpecSummary | null }) {
  const [label, setLabel] = useState('Mentor API review')
  const [specText, setSpecText] = useState('')
  const [harText, setHarText] = useState('')
  const [result, setResult] = useState<DiscoveryAnalysis | null>(null)
  const [reviews, setReviews] = useState<CandidateReview[]>([])
  const [rationales, setRationales] = useState<Record<string, string>>({})
  const [reviewBusy, setReviewBusy] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  useEffect(() => { if (spec?.document && !specText) setSpecText(JSON.stringify(spec.document, null, 2)) }, [spec?.document])
  function loadFile(file: File | undefined, target: 'spec' | 'har') {
    if (!file) return
    if (file.size > 2_000_000) { setError('File exceeds the 2 MB analysis limit.'); return }
    file.text().then(text => { setError(''); target === 'spec' ? setSpecText(text) : setHarText(text) }).catch(() => setError('Could not read the selected file.'))
  }
  function loadDemoTraffic() {
    setHarText(JSON.stringify({ log: { entries: [
      { request: { method: 'GET', url: 'https://fixture.local/v1/invoices/INV-1842' } },
      { request: { method: 'GET', url: 'https://fixture.local/v1/exports/EXP-991/content' } },
      { request: { method: 'GET', url: 'https://fixture.local/v1/internal/debug-user/88291' } },
    ] } }, null, 2))
    setError('')
  }
  async function analyze() {
    setBusy(true); setError('')
    try {
      let document: Record<string, unknown>
      let har: Record<string, unknown> | null = null
      try { document = JSON.parse(specText) as Record<string, unknown> }
      catch { throw new Error('OpenAPI JSON is malformed. Fix the highlighted source and analyze again.') }
      if (harText.trim()) {
        try { har = JSON.parse(harText) as Record<string, unknown> }
        catch { throw new Error('HAR JSON is malformed. Fix or remove the traffic sample and analyze again.') }
      }
      const analysis = await api.analyze(label, document, har)
      setResult(analysis); setReviews([]); setRationales({})
    } catch (caught) { setError(caught instanceof Error ? caught.message : 'Discovery analysis failed') }
    finally { setBusy(false) }
  }
  async function reviewCandidate(candidateId: string, decision: 'approved' | 'rejected') {
    const rationale = rationales[candidateId]?.trim() || ''
    if (rationale.length < 8) { setError('Add a decision rationale of at least 8 characters.'); return }
    if (!result) return
    setReviewBusy(candidateId); setError('')
    try {
      const review = await api.reviewCandidate(result.id, candidateId, decision, rationale)
      setReviews(current => [...current, review])
      setRationales(current => ({ ...current, [candidateId]: '' }))
    } catch (caught) { setError(caught instanceof Error ? caught.message : 'Could not record the policy decision') }
    finally { setReviewBusy('') }
  }
  return <><header className="page-head"><div><p className="eyebrow">Passive discovery</p><h1>Map the API boundary.</h1><p>Add an API contract and optional traffic sample. BoundaryLab finds likely ownership rules and shadow routes without sending a request.</p></div><div className="demo-flag"><i/>No active probing</div></header>
    <section className="card discovery-input"><div className="discovery-copy"><div><h2>Add your API sources</h2><p>Start with OpenAPI. Add HAR only when you want documented-versus-observed route analysis.</p></div><div className="input-safety"><Icon name="shield"/><span><strong>Review stays human</strong><small>Candidates never enter policy automatically</small></span></div></div><div className="import-grid"><div className={`source-card ${specText ? 'source-ready' : ''}`}><div className="source-title"><span className="source-icon"><Icon name="report"/></span><span><b>OpenAPI contract</b><small>JSON · required</small></span><em>{specText ? 'Ready' : 'Required'}</em></div><p className="source-help">Operations, schemas and auth schemes</p><div className="source-actions"><label className="button secondary compact" htmlFor="openapi-file">Choose file</label><input id="openapi-file" className="visually-hidden" type="file" accept="application/json,.json" onChange={event => loadFile(event.target.files?.[0], 'spec')}/><span>{specText ? 'Contract loaded' : 'No contract selected'}</span></div><details className="source-details"><summary>Paste or inspect JSON</summary><textarea value={specText} onChange={event => { setSpecText(event.target.value); setError('') }} spellCheck={false} aria-label="OpenAPI JSON source"/></details></div><div className={`source-card ${harText ? 'source-ready' : ''}`}><div className="source-title"><span className="source-icon"><Icon name="radar"/></span><span><b>Traffic sample</b><small>HAR · optional</small></span><em className="optional">{harText ? 'Ready' : 'Optional'}</em></div><p className="source-help">Route diff only; secrets and bodies are discarded</p><div className="source-actions"><label className="button secondary compact" htmlFor="har-file">Choose HAR</label><input id="har-file" className="visually-hidden" type="file" accept="application/json,.har" onChange={event => loadFile(event.target.files?.[0], 'har')}/><button className="text-link" type="button" onClick={loadDemoTraffic}>Use demo traffic</button></div><details className="source-details"><summary>Paste or inspect HAR</summary><textarea value={harText} onChange={event => { setHarText(event.target.value); setError('') }} placeholder="Paste HAR JSON" spellCheck={false} aria-label="HAR JSON source"/></details></div></div><details className="analysis-options"><summary>Analysis options</summary><label className="analysis-name">Analysis label<input value={label} maxLength={120} onChange={event => { setLabel(event.target.value); setError('') }}/></label><div className="limit-row"><span>2 MB max</span><span>500 paths</span><span>5,000 HAR entries</span></div></details><div className="discovery-submit"><button className="button primary" disabled={busy || !label.trim() || !specText.trim()} onClick={analyze}>{busy ? 'Mapping boundary…' : 'Map API boundary'}</button><span className="submit-note">Usually completes in a few seconds</span></div>{error && <p className="form-error" role="alert">{error}</p>}</section>
    {result && <><section className="metrics discovery-metrics"><div><span>Operations</span><b>{result.summary.documented_operations}</b></div><div><span>Ownership candidates</span><b>{result.summary.ownership_candidates}</b></div><div className={result.summary.shadow_operations ? 'metric-danger' : ''}><span>Shadow routes</span><b>{result.summary.shadow_operations}</b></div><div><span>Ledger decisions</span><b>{reviews.length}</b></div></section><section className="discovery-grid"><div className="card"><div className="section-head"><div><p className="eyebrow">Policy candidates</p><h2>Review before replay</h2></div><code>{result.spec.sha256.slice(0,12)}…</code></div>{result.invariant_candidates.length ? <div className="candidate-list">{result.invariant_candidates.map(candidate => {
      const latest = reviews.filter(review => review.candidate_id === candidate.id).at(-1)
      const rationale = rationales[candidate.id] || ''
      return <article key={candidate.id}><div><code>{candidate.method} {candidate.path}</code><span className={`confidence confidence-${candidate.confidence}`}>{candidate.confidence}</span></div><h3>{candidate.operation_id}</h3><p>{candidate.proposed_rule}</p><small>{candidate.required_setup}</small>{latest && <div className={`decision-record decision-${latest.decision}`}><strong>{latest.decision}</strong><span>{latest.rationale}</span><code>{latest.candidate_sha256.slice(0,12)}… · {latest.reviewer}</code></div>}<label className="decision-rationale">Decision rationale<input value={rationale} maxLength={500} placeholder="Why should this rule enter or stay out of policy?" onChange={event => setRationales(current => ({ ...current, [candidate.id]: event.target.value }))}/></label><div className="decision-actions"><button className="button primary compact" disabled={reviewBusy === candidate.id || rationale.trim().length < 8} onClick={() => reviewCandidate(candidate.id, 'approved')}>{reviewBusy === candidate.id ? 'Recording…' : 'Approve candidate'}</button><button className="button secondary compact" disabled={reviewBusy === candidate.id || rationale.trim().length < 8} onClick={() => reviewCandidate(candidate.id, 'rejected')}>Reject</button><span>Append-only decision ledger</span></div></article>
    })}</div> : <div className="empty-small">No resource-ID read/update operations were inferred. Review the contract manually.</div>}</div><aside className="card shadow-panel"><p className="eyebrow">Traffic diff</p><h2>{result.traffic_diff.provided ? 'Observed vs documented' : 'Add HAR for shadow routes'}</h2>{result.traffic_diff.shadow_operations.map(item => <div className="shadow-route" key={`${item.method}-${item.path}`}><code>{item.method}</code><strong>{item.path}</strong><span>{item.sample_count}× · {item.risk}</span></div>)}{result.traffic_diff.provided && !result.traffic_diff.shadow_operations.length && <p className="success-note">No unmatched routes in this traffic sample.</p>}<div className="notice">Unobserved operations are not labelled zombie APIs because a HAR sample can be incomplete.</div></aside></section></>}
  </>
}

function PolicyView({ policy, spec }: { policy: PolicySummary | null; spec: SpecSummary | null }) {
  if (!policy || !spec) return <section className="empty-state"><div className="spinner"/><h2>Loading reviewed policy</h2></section>
  const document = policy.document as Record<string, any>
  if (!policy.approved || !spec.configured) return <><header className="page-head"><div><p className="eyebrow">Access contract</p><h1>No active policy configured.</h1><p>Passive discovery remains available. Active testing starts only after an operator supplies a reviewed target registry.</p></div><StatusBadge value="draft"/></header><section className="card target-setup"><span className="setup-icon"><Icon name="shield" size={22}/></span><div><h2>Fail-closed runtime</h2><p>{String(document.safety || 'Add a reviewed target registry before active testing.')}</p><p className="micro muted">No demo target, token or expected result is silently substituted.</p></div></section></>
  const realPolicy = document.scenario === 'read-boundary-v1'
  return <><header className="page-head"><div><p className="eyebrow">Access contract</p><h1>Define what access means.</h1><p>The API schema explains how to call an endpoint. This policy explains who should receive the data.</p></div><StatusBadge value={policy.approved ? 'approved' : 'draft'}/></header>
    <section className="policy-grid"><div className="card policy-main"><div className="section-head"><div><p className="eyebrow">{String(document.name)}</p><h2>{realPolicy ? 'Reviewed staging read boundary' : 'Invoice sharing policy · v1'}</h2></div><code>{policy.sha256.slice(0,12)}…</code></div>
      {realPolicy ? <><div className="policy-callout"><span>Active safety contract</span><strong>One fixed GET is replayed for each reviewed identity.</strong><p>The configured marker must appear only for allowed identities. Redirects, arbitrary URLs and browser-supplied credentials are rejected.</p></div><div className="table-scroll"><table><thead><tr><th>Identity</th><th>Expected access</th><th>Forbidden response fields</th><th>Operation</th></tr></thead><tbody>{(document.identities || []).map((identity: any) => <tr key={identity.name}><td><strong>{identityLabel(identity.name)}</strong></td><td><StatusBadge value={identity.expectation === 'allow' ? 'approved' : 'blocked'}/></td><td>{identity.forbidden_pointers?.length ? identity.forbidden_pointers.join(', ') : 'None declared'}</td><td><code>{document.operation_id}</code></td></tr>)}</tbody></table></div></> : <><div className="policy-callout"><span>Revocation promise</span><strong>Fresh export retrieval must stop within {document.revocation.grace_ms} ms.</strong><p>Measured after successful revoke acknowledgement, plus {document.revocation.probe_margin_ms} ms probe margin.</p></div><div className="table-scroll"><table><thead><tr><th>Relation</th><th>Private preview</th><th>Shared detail</th><th>Owner field</th><th>Export after revoke</th></tr></thead><tbody><tr><td>Resource owner</td><td>Allow</td><td>Allow</td><td>Allow</td><td>Allow</td></tr><tr><td>Temporary user · active</td><td>Deny</td><td>Allow</td><td>Deny</td><td>Allow</td></tr><tr><td>Temporary user · revoked</td><td>Deny</td><td>Deny</td><td>Deny</td><td>Deny</td></tr><tr><td>External tenant</td><td>Deny</td><td>Deny</td><td>Deny</td><td>Deny</td></tr></tbody></table></div></>}
      </div><aside className="card spec-card"><p className="eyebrow">Bound contract</p><h2>{spec.title}</h2><dl><div><dt>Format</dt><dd>OpenAPI {spec.openapi}</dd></div><div><dt>Operations</dt><dd>{spec.operation_count}</dd></div><div><dt>Required cases</dt><dd>{document.required_cases?.length || 0}</dd></div><div><dt>Execution</dt><dd>{realPolicy ? 'GET only' : document.fixture_semantics_version}</dd></div></dl><h3>Supported operations</h3><div className="code-list">{spec.operations.map(item => <code key={item}>{item}</code>)}</div><div className="notice policy-safety">{String(document.safety || 'Declared fixture policy')}</div></aside></section>
  </>
}

function CompareView({ runs }: { runs: Run[] }) {
  const completed = runs.filter(run => run.state === 'completed')
  const [baselineId, setBaselineId] = useState('')
  const [candidateId, setCandidateId] = useState('')
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [error, setError] = useState('')
  useEffect(() => {
    if (completed.length < 2 || baselineId || candidateId) return
    const vulnerable = completed.find(run => run.target_alias.includes('vulnerable'))
    const fixed = completed.find(run => run.target_alias.includes('fixed'))
    setBaselineId((vulnerable || completed.at(-1))?.id || '')
    setCandidateId((fixed || completed[0])?.id || '')
  }, [completed, baselineId, candidateId])
  async function compare() {
    setError(''); setComparison(null)
    if (!baselineId || !candidateId || baselineId === candidateId) { setError('Choose two different completed runs.'); return }
    try { setComparison(await api.compare([baselineId, candidateId])) } catch (e) { setError(e instanceof Error ? e.message : 'Comparison failed') }
  }
  const runLabel = (run: Run) => `${run.target_alias.replace('demo-','')} · ${run.build_id || run.id.slice(-6)} · ${run.assessment}`
  return <><header className="page-head"><div><p className="eyebrow">Release decision</p><h1>Prove the fix is safe to ship.</h1><p>Choose the old behavior and the release candidate. BoundaryLab counts repaired controls, preserved product behavior and new regressions.</p></div></header>
    <section className="card gate-picker"><div><p className="eyebrow">Step 1 · Baseline</p><h2>What are we replacing?</h2><select aria-label="Baseline run" value={baselineId} onChange={event => { setBaselineId(event.target.value); setComparison(null) }}><option value="">Choose baseline</option>{completed.map(run => <option key={run.id} value={run.id}>{runLabel(run)}</option>)}</select></div><span className="gate-arrow" aria-hidden="true">→</span><div><p className="eyebrow">Step 2 · Candidate</p><h2>What do we want to ship?</h2><select aria-label="Candidate run" value={candidateId} onChange={event => { setCandidateId(event.target.value); setComparison(null) }}><option value="">Choose candidate</option>{completed.map(run => <option key={run.id} value={run.id}>{runLabel(run)}</option>)}</select></div><button className="button primary" disabled={!baselineId || !candidateId || baselineId === candidateId} onClick={compare}>Evaluate release gate</button>{error && <p className="form-error full" role="alert">{error}</p>}</section>
    {comparison && <><section className={`card release-gate gate-${comparison.gate.decision}`}><div className="gate-verdict"><span>{comparison.gate.decision === 'ready' ? '✓' : comparison.gate.decision === 'blocked' ? '!' : '?'}</span><div><p className="eyebrow">Deterministic release gate</p><h2>{comparison.gate.decision === 'ready' ? 'Ready for this tested scope' : comparison.gate.decision === 'blocked' ? 'Do not ship this candidate' : 'More evidence is required'}</h2><p>{comparison.gate.reasons.join(' · ')}</p></div><StatusBadge value={comparison.gate.decision}/></div><div className="gate-metrics"><div><b>{comparison.gate.fixed}</b><span>Fixed</span></div><div><b>{comparison.gate.preserved}</b><span>Passes preserved</span></div><div><b>{comparison.gate.regressed}</b><span>Regressed</span></div><div><b>{comparison.gate.unresolved}</b><span>Unresolved</span></div></div><p className="micro muted">Decision is limited to policy <code>{comparison.policy_version}</code> and the same {comparison.rows.length}-case suite.</p></section><section className="card"><div className="section-head"><div><p className="eyebrow">Case-by-case proof</p><h2>What changed?</h2></div><span className="scope-chip">Baseline → candidate</span></div><div className="table-scroll"><table><thead><tr><th>Case</th><th>Promise</th><th>Before</th><th>After</th><th>Change</th></tr></thead><tbody>{comparison.gate.changes.map(change => <tr key={change.case_id}><td><code>{change.case_id}</code></td><td>{caseLabel(change.name)}</td><td><StatusBadge value={change.before}/></td><td><StatusBadge value={change.after}/></td><td><span className={`change change-${change.classification}`}>{change.classification}</span></td></tr>)}</tbody></table></div></section></>}
  </>
}

function ReportsView({ runs }: { runs: Run[] }) {
  const completed = runs.filter(run => run.state === 'completed' && run.assessment)
  const [busy, setBusy] = useState('')
  const [message, setMessage] = useState('')
  async function download(run: Run, format: 'report_html'|'results_json') { const key=run.id+format; setBusy(key); setMessage(''); try { const artifact=await api.artifact(run.id,format); window.location.assign(artifact.download_path); setMessage(`Artifact ready · SHA-256 ${artifact.sha256.slice(0,16)}…`) } catch(e){ setMessage(e instanceof Error?e.message:'Export failed') } finally{setBusy('')} }
  return <><header className="page-head"><div><p className="eyebrow">Evidence handoff</p><h1>Share the proof.</h1><p>Export the tested cases, build, policy and incomplete context in one reviewable artifact.</p></div></header>
    <section className="report-list">{completed.map(run => <article className="card report-row" key={run.id}><div className={`report-mark ${run.assessment === 'blocked' ? 'danger' : ''}`}>{run.assessment === 'blocked' ? '!' : '✓'}</div><div><p className="eyebrow">{run.id}</p><h2>{run.target_alias.replace('demo-','')}</h2><p>{run.counts.pass} pass · {run.counts.violation} violations · {run.counts.inconclusive} inconclusive · {run.request_count} requests</p></div><StatusBadge value={run.assessment}/><div className="report-actions"><button className="button secondary compact" disabled={!!busy} onClick={()=>download(run,'report_html')}>HTML report</button><button className="button secondary compact" disabled={!!busy} onClick={()=>download(run,'results_json')}>JSON evidence</button></div></article>)}{!completed.length && <section className="empty-state"><h2>Complete a run first</h2><p>Reports are generated only from persisted evidence.</p></section>}</section>{message && <div className="toast" role="status">{message}</div>}
  </>
}

function WorkbenchApp() {
  const [auth, setAuth] = useState<'loading'|'login'|'ready'>('loading')
  const [view, setView] = useState<View>('overview')
  const [targets, setTargets] = useState<Target[]>([])
  const [targetAlias, setTargetAlias] = useState('')
  const [runs, setRuns] = useState<Run[]>([])
  const [selectedRun, setSelectedRun] = useState<Run | null>(null)
  const [policy, setPolicy] = useState<PolicySummary | null>(null)
  const [spec, setSpec] = useState<SpecSummary | null>(null)
  const [capabilities, setCapabilities] = useState<Capabilities | null>(null)
  const [workspaceLoading, setWorkspaceLoading] = useState(true)
  const [workspaceError, setWorkspaceError] = useState('')
  const [workspaceRevision, setWorkspaceRevision] = useState(0)
  const apiStatus = useSyncExternalStore(subscribeApiStatus, getApiStatus, getApiStatus)

  const loadRuns = useCallback(async () => {
    const list = await api.runs(); setRuns(list)
    if (selectedRun) { const updated = await api.run(selectedRun.id); setSelectedRun(updated) }
  }, [selectedRun?.id])
  const loadWorkspace = useCallback(async () => {
    setWorkspaceLoading(true); setWorkspaceError('')
    try {
      const [targetData, runData, capabilityData] = await Promise.all([api.targets(), api.runs(), api.capabilities()])
      const initialAlias = targetData[0]?.alias || ''
      const [policyData, specData] = await Promise.all([api.policy(initialAlias || undefined), api.spec(initialAlias || undefined)])
      setTargetAlias(initialAlias)
      setTargets(targetData); setRuns(runData); setPolicy(policyData); setSpec(specData); setCapabilities(capabilityData)
      if (runData[0]) setSelectedRun(await api.run(runData[0].id))
      return true
    } catch (caught) {
      setWorkspaceError(caught instanceof Error ? caught.message : 'The local control API did not return a complete workspace.')
      return false
    } finally { setWorkspaceLoading(false) }
  }, [])
  useEffect(() => { api.restoreSession().then(() => setAuth('ready')).catch(() => setAuth('login')) }, [])
  useEffect(() => { if (apiStatus.sessionExpired) { setAuth('login'); setWorkspaceError('') } }, [apiStatus.sessionExpired])
  useEffect(() => { if (auth === 'ready') void loadWorkspace() }, [auth, loadWorkspace])
  useEffect(() => { window.scrollTo(0, 0) }, [view])
  const activeRuns = useMemo(() => runs.filter(run => ['queued','running'].includes(run.state)).length, [runs])
  const active = activeRuns > 0
  useEffect(() => { if (!active || auth !== 'ready') return; const timer=window.setInterval(() => loadRuns().catch(()=>undefined),1000); return()=>window.clearInterval(timer) }, [active, auth, loadRuns])
  async function select(run: Run) {
    try { setSelectedRun(await api.run(run.id)) }
    catch (caught) { setWorkspaceError(caught instanceof Error ? caught.message : 'Could not load the selected run.') }
  }
  async function changeTarget(alias: string) {
    setTargetAlias(alias); setWorkspaceError('')
    try {
      const [policyData, specData] = await Promise.all([api.policy(alias), api.spec(alias)])
      setPolicy(policyData); setSpec(specData)
      const related = runs.find(run => run.target_alias === alias)
      setSelectedRun(related ? await api.run(related.id) : null)
    } catch (caught) {
      setWorkspaceError(caught instanceof Error ? caught.message : 'Target context could not be loaded.')
    }
  }
  async function logout() { await api.logout().catch(()=>undefined); setAuth('login') }
  async function reconnect() { if (await loadWorkspace()) setWorkspaceRevision(current => current + 1) }
  if (auth === 'loading') return <main className="boot"><div className="mark mark-large">B</div><div className="spinner light-spinner"/><p>Opening local workbench…</p></main>
  if (auth === 'login') return <Login onLogin={() => setAuth('ready')}/>
  return <div className="app-shell"><SideNav view={view} setView={setView} logout={logout} activeRuns={activeRuns}/><main className="content">
    <WorkspaceHeader view={view} activeRuns={activeRuns} policyLabel={String(policy?.document.scenario || 'no-active-policy')} connected={apiStatus.connection !== 'offline'}/>
    {apiStatus.connection === 'offline' && <section className="connection-banner" role="alert"><Icon name="alert"/><div><strong>Local server disconnected</strong><span>Saved browser content may still be visible, but actions need the BoundaryLab service on port 8080.</span></div><button className="button secondary compact" onClick={() => void reconnect()}>Reconnect</button></section>}
    {workspaceLoading && <section className="workspace-loading" aria-live="polite" aria-busy="true"><div className="spinner"/><div><strong>Opening the authenticated workspace…</strong><span>Loading trusted targets, policy contracts and persisted evidence.</span><div className="loading-track"><i/></div></div></section>}
    {!workspaceLoading && workspaceError && <section className="workspace-recovery card" role="alert"><span className="recovery-icon"><Icon name="alert" size={22}/></span><div><p className="eyebrow">Control API unavailable</p><h1>Workspace data could not be synchronized.</h1><p>{workspaceError}</p><p className="micro">Your session remains open and persisted evidence is unchanged.</p></div><button className="button primary" onClick={() => void loadWorkspace()}>Retry synchronization</button></section>}
    {!workspaceLoading && !workspaceError && <Fragment key={workspaceRevision}>
      <WorkflowRail view={view} setView={setView}/>
      {view !== 'overview' && <StageBrief view={view} setView={setView}/>}
      {view === 'overview' && <MentorOverview setView={setView} runs={runs} targets={targets} capabilities={capabilities}/>}
      {view === 'runs' && <RunsView targets={targets} targetAlias={targetAlias} onTargetChange={alias => void changeTarget(alias)} runs={runs} selectedRun={selectedRun} select={select} refresh={loadRuns} capabilities={capabilities}/>}
      {view === 'discovery' && <DiscoveryView spec={spec}/>}
      {view === 'policy' && <PolicyView policy={policy} spec={spec}/>}
      {view === 'compare' && <CompareView runs={runs}/>}
      {view === 'reports' && <ReportsView runs={runs}/>}
    </Fragment>}
  </main></div>
}

export default function App() {
  return <AppErrorBoundary><WorkbenchApp/></AppErrorBoundary>
}
