import { FormEvent, useCallback, useEffect, useMemo, useState } from 'react'
import { api } from './api'
import type { CaseResult, Comparison, Evidence, Report, Run, Target, Verdict } from './types'

type View = 'runs' | 'policy' | 'compare' | 'reports'

const verdictLabel: Record<Verdict, string> = {
  pass: 'Pass', violation: 'Violation', inconclusive: 'Inconclusive', skipped: 'Skipped',
}

function StatusBadge({ value }: { value: string | null }) {
  const normalized = (value || 'pending').replaceAll('_', '-')
  return <span className={`status status-${normalized}`}>{(value || 'Pending').replaceAll('_', ' ')}</span>
}

function Login({ onLogin }: { onLogin: () => void }) {
  const [secret, setSecret] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('')
    try { await api.login(secret); onLogin() } catch (caught) { setError(caught instanceof Error ? caught.message : 'Login failed') }
    finally { setBusy(false) }
  }
  return <main className="login-shell">
    <section className="login-brand" aria-label="BoundaryLab overview">
      <div className="mark mark-large">B</div><p className="eyebrow light">SentinelAPI / AmiHacks</p>
      <h1>Prove the boundary.<br/><span>Preserve the product.</span></h1>
      <p>Authorization regression evidence across the full permission lifecycle—from grant to revocation and retrieval.</p>
      <div className="login-proof"><b>12</b><span>declared policy cases</span><b>3</b><span>disclosed fixture builds</span></div>
    </section>
    <section className="login-card">
      <p className="eyebrow">Local operator access</p><h2>Open the workbench</h2>
      <p className="muted">Enter the one-time secret printed by the local server. The secret stays in this request and is never stored by the browser.</p>
      <form onSubmit={submit}>
        <label htmlFor="secret">Bootstrap secret</label>
        <input id="secret" type="password" autoComplete="current-password" minLength={16} required value={secret} onChange={e => setSecret(e.target.value)} />
        {error && <p className="form-error" role="alert">{error}</p>}
        <button className="button primary wide" disabled={busy}>{busy ? 'Checking…' : 'Enter BoundaryLab'}</button>
      </form>
      <p className="micro">Local single-operator profile · bound to 127.0.0.1</p>
    </section>
  </main>
}

function SideNav({ view, setView, logout }: { view: View; setView: (view: View) => void; logout: () => void }) {
  const items: Array<[View, string, string]> = [
    ['runs', '01', 'Live runs'], ['policy', '02', 'Policy'], ['compare', '03', 'Compare repairs'], ['reports', '04', 'Report handoff'],
  ]
  return <aside className="sidebar">
    <div><div className="brand"><div className="mark">B</div><div><strong>BoundaryLab</strong><small>SentinelAPI</small></div></div>
      <nav aria-label="Product navigation">{items.map(([id, number, label]) =>
        <button key={id} className={view === id ? 'active' : ''} onClick={() => setView(id)} aria-current={view === id ? 'page' : undefined}>
          <span>{number}</span>{label}
        </button>)}</nav>
    </div>
    <div className="side-footer"><div className="scope-dot"><i/>Local trusted scope</div><button className="text-button" onClick={logout}>Sign out</button></div>
  </aside>
}

function RunList({ runs, selected, select }: { runs: Run[]; selected?: string; select: (run: Run) => void }) {
  return <div className="run-list" aria-label="Recent runs">
    {runs.length === 0 && <div className="empty-small">No runs yet.</div>}
    {runs.map(run => <button key={run.id} className={selected === run.id ? 'run-row selected' : 'run-row'} onClick={() => select(run)}>
      <div><strong>{run.target_alias.replace('demo-', '')}</strong><small>{new Date(run.created_at).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})} · {run.id.slice(-6)}</small></div>
      <StatusBadge value={run.assessment || run.state}/>
    </button>)}
  </div>
}

function Timeline({ report }: { report: Report }) {
  const operations = ['grantShare', 'queueExport', 'getExportContent', 'revokeShare', 'getMe', 'getExportContent']
  const picked: Evidence[] = []
  let cursor = 0
  for (const operation of operations) {
    const found = report.evidence.find((item, index) => index >= cursor && item.operation_id === operation)
    if (found) { picked.push(found); cursor = report.evidence.indexOf(found) + 1 }
  }
  return <div className="timeline">{picked.map((item, index) =>
    <div className={`timeline-step ${item.status_code && item.status_code >= 400 ? 'denied' : ''}`} key={`${item.evidence_id}-${index}`}>
      <span className="time">+{item.start_offset_ms} ms</span><i/><strong>{item.operation_id}</strong><small>{item.identity} · HTTP {item.status_code}</small>
    </div>)}</div>
}

function EvidenceDrawer({ evidence, close }: { evidence: Evidence; close: () => void }) {
  return <div className="drawer-backdrop" onMouseDown={event => { if (event.currentTarget === event.target) close() }}>
    <aside className="drawer" role="dialog" aria-modal="true" aria-labelledby="evidence-title">
      <div className="drawer-head"><div><p className="eyebrow">Sanitized evidence</p><h2 id="evidence-title">{evidence.operation_id}</h2></div><button className="icon-button" onClick={close} aria-label="Close evidence">×</button></div>
      <dl className="evidence-facts"><div><dt>Identity</dt><dd>{evidence.identity}</dd></div><div><dt>Status</dt><dd>HTTP {evidence.status_code}</dd></div><div><dt>Started</dt><dd>+{evidence.start_offset_ms} ms</dd></div><div><dt>Duration</dt><dd>{evidence.duration_ms} ms</dd></div></dl>
      <h3>Request</h3><pre>{`${evidence.method} ${evidence.path}\n${Object.entries(evidence.request_headers).map(([key,value]) => `${key}: ${value}`).join('\n')}`}</pre>
      <h3>Allowlisted response excerpt</h3><pre>{JSON.stringify(evidence.response_excerpt, null, 2)}</pre>
      <p className="hash">SHA-256 · {evidence.sha256}</p>
      <div className="notice">Credentials and unrestricted response bodies are removed before persistence.</div>
    </aside>
  </div>
}

function RunDetail({ run, cancel }: { run: Run | null; cancel: (id: string) => void }) {
  const [evidence, setEvidence] = useState<Evidence | null>(null)
  if (!run) return <section className="empty-state"><div className="empty-icon">↗</div><h2>Select or start a run</h2><p>Actual evidence and policy outcomes will appear here.</p></section>
  const report = run.report
  const openCase = (item: CaseResult) => {
    const found = report?.evidence.find(e => item.evidence_ids.includes(e.evidence_id)); if (found) setEvidence(found)
  }
  return <>
    <section className="run-hero card">
      <div><p className="eyebrow">Permission lifecycle / {run.id}</p><h2>Can Bob still retrieve the invoice after access is revoked?</h2><p className="muted">Target <code>{run.target_alias}</code> · build <code>{run.build_id || 'pending'}</code></p></div>
      <div className="hero-status"><StatusBadge value={run.assessment || run.state}/>{!['completed','failed','interrupted','cancelled'].includes(run.state) && <button className="button secondary compact" onClick={() => cancel(run.id)}>Cancel</button>}</div>
    </section>
    {!report && <section className="card working"><div className="spinner"/><div><h3>{run.state === 'queued' ? 'Waiting for the single safe worker' : 'Executing bounded target requests'}</h3><p>State and evidence are persisted. Refreshing this page will not lose the run.</p></div></section>}
    {report && <>
      <section className="metrics"><div><span>Pass</span><b>{report.counts.pass}</b></div><div className="metric-danger"><span>Violations</span><b>{report.counts.violation}</b></div><div><span>Inconclusive</span><b>{report.counts.inconclusive}</b></div><div><span>Requests</span><b>{report.request_count}</b></div></section>
      <section className="card"><div className="section-head"><div><p className="eyebrow">Observed sequence</p><h3>Follow the permission</h3></div><span className="scope-chip">2,000 ms grace · 200 ms margin</span></div><Timeline report={report}/></section>
      <section className="card"><div className="section-head"><div><p className="eyebrow">Policy acceptance</p><h3>12 required cases</h3></div><span className="muted micro">Cleanup: {report.cleanup_status}</span></div>
        <div className="table-scroll"><table><thead><tr><th>Case</th><th>Permission promise</th><th>Expected</th><th>Observed</th><th>Verdict</th></tr></thead><tbody>
          {report.cases.map(item => <tr key={item.case_id} className={item.evidence_ids.length ? 'clickable' : ''} onClick={() => openCase(item)}>
            <td><code>{item.case_id}</code></td><td><strong>{item.name}</strong>{item.reason_code && <small>{item.reason_code}</small>}</td><td>{item.expected}</td><td>{item.observed}</td><td><StatusBadge value={item.verdict}/></td>
          </tr>)}</tbody></table></div>
      </section>
    </>}
    {evidence && <EvidenceDrawer evidence={evidence} close={() => setEvidence(null)}/>}
  </>
}

function RunsView({ targets, runs, selectedRun, select, refresh }: { targets: Target[]; runs: Run[]; selectedRun: Run | null; select: (run: Run) => void; refresh: () => Promise<void> }) {
  const [target, setTarget] = useState('demo-vulnerable')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function start(alias = target) { setBusy(true); setError(''); try { const run = await api.startRun(alias); select(run); await refresh() } catch (e) { setError(e instanceof Error ? e.message : 'Could not start run') } finally { setBusy(false) } }
  async function matrix() { setBusy(true); setError(''); try { let first: Run | null = null; for (const item of targets) { const run = await api.startRun(item.alias); first ||= run } if (first) select(first); await refresh() } catch (e) { setError(e instanceof Error ? e.message : 'Could not queue matrix') } finally { setBusy(false) } }
  async function cancel(id: string) { try { await api.cancelRun(id); await refresh() } catch (e) { setError(e instanceof Error ? e.message : 'Cancellation failed') } }
  return <><header className="page-head"><div><p className="eyebrow">Live authorization workbench</p><h1>Test the promise, not the endpoint.</h1><p>Run a declared sharing policy through real local HTTP targets and inspect the evidence.</p></div><div className="demo-flag"><i/>Synthetic fixture targets</div></header>
    <section className="launch card"><div className="launch-copy"><span className="step-number">01</span><div><h2>Choose a disclosed implementation</h2><p>Target URLs come from the trusted server registry. This form cannot scan an arbitrary host.</p></div></div><div className="launch-actions"><label htmlFor="target">Target build</label><select id="target" value={target} onChange={e => setTarget(e.target.value)}>{targets.map(item => <option value={item.alias} key={item.alias}>{item.label}</option>)}</select><button className="button primary" onClick={() => start()} disabled={busy}>{busy ? 'Queueing…' : 'Run selected target'}</button><button className="button secondary" onClick={matrix} disabled={busy}>Queue three-build proof</button></div>{error && <p className="form-error full" role="alert">{error}</p>}</section>
    <div className="workspace-grid"><section className="card recent"><div className="section-head"><div><p className="eyebrow">Persisted locally</p><h3>Recent runs</h3></div><button className="icon-button" onClick={refresh} aria-label="Refresh runs">↻</button></div><RunList runs={runs} selected={selectedRun?.id} select={select}/></section><div className="detail-column"><RunDetail run={selectedRun} cancel={cancel}/></div></div>
  </>
}

function PolicyView({ policy, spec }: { policy: { approved: boolean; sha256: string; document: Record<string, any> } | null; spec: { title: string; openapi: string; operation_count: number; operations: string[] } | null }) {
  if (!policy || !spec) return <section className="empty-state"><div className="spinner"/><h2>Loading reviewed policy</h2></section>
  const document = policy.document
  return <><header className="page-head"><div><p className="eyebrow">Policy before probing</p><h1>Define the boundary explicitly.</h1><p>Schema tells us how to call the API. This reviewed contract tells us what access should mean.</p></div><StatusBadge value={policy.approved ? 'approved' : 'draft'}/></header>
    <section className="policy-grid"><div className="card policy-main"><div className="section-head"><div><p className="eyebrow">{String(document.name)}</p><h2>Invoice sharing policy · v1</h2></div><code>{policy.sha256.slice(0,12)}…</code></div>
      <div className="policy-callout"><span>Revocation promise</span><strong>Fresh export retrieval must stop within {document.revocation.grace_ms} ms.</strong><p>Measured after successful revoke acknowledgement, plus {document.revocation.probe_margin_ms} ms probe margin.</p></div>
      <div className="table-scroll"><table><thead><tr><th>Relation</th><th>Private preview</th><th>Shared detail</th><th>Owner field</th><th>Export after revoke</th></tr></thead><tbody><tr><td>Alice · owner</td><td>Allow</td><td>Allow</td><td>Allow</td><td>Allow</td></tr><tr><td>Bob · active share</td><td>Deny</td><td>Allow</td><td>Deny</td><td>Allow</td></tr><tr><td>Bob · revoked</td><td>Deny</td><td>Deny</td><td>Deny</td><td>Deny</td></tr><tr><td>Mallory · tenant B</td><td>Deny</td><td>Deny</td><td>Deny</td><td>Deny</td></tr></tbody></table></div></div>
      <aside className="card spec-card"><p className="eyebrow">Bound contract</p><h2>{spec.title}</h2><dl><div><dt>Format</dt><dd>OpenAPI {spec.openapi}</dd></div><div><dt>Operations</dt><dd>{spec.operation_count}</dd></div><div><dt>Required cases</dt><dd>{document.required_cases.length}</dd></div><div><dt>Fixture semantics</dt><dd>{document.fixture_semantics_version}</dd></div></dl><h3>Supported operations</h3><div className="code-list">{spec.operations.map(item => <code key={item}>{item}</code>)}</div></aside></section>
  </>
}

function CompareView({ runs }: { runs: Run[] }) {
  const completed = runs.filter(run => run.state === 'completed')
  const [selected, setSelected] = useState<string[]>([])
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [error, setError] = useState('')
  const toggle = (id: string) => setSelected(current => current.includes(id) ? current.filter(x => x !== id) : current.length < 3 ? [...current, id] : current)
  async function compare() { setError(''); try { setComparison(await api.compare(selected)) } catch (e) { setError(e instanceof Error ? e.message : 'Comparison failed') } }
  return <><header className="page-head"><div><p className="eyebrow">Two-sided fix validation</p><h1>Close the leak. Keep the feature.</h1><p>Compare only completed runs under the same policy and case suite.</p></div></header>
    <section className="card compare-picker"><div><h2>Select 2–3 runs</h2><p className="muted">Use vulnerable, owner-only and fixed builds for the strongest mentor demonstration.</p></div><div className="run-checks">{completed.map(run => <label key={run.id} className={selected.includes(run.id) ? 'run-check selected' : 'run-check'}><input type="checkbox" checked={selected.includes(run.id)} onChange={() => toggle(run.id)}/><span><strong>{run.target_alias.replace('demo-','')}</strong><small>{run.id.slice(-6)} · {run.assessment}</small></span></label>)}</div><button className="button primary" disabled={selected.length < 2} onClick={compare}>Compare selected repairs</button>{error && <p className="form-error" role="alert">{error}</p>}</section>
    {comparison && <section className="card"><div className="section-head"><div><p className="eyebrow">Compatible policy · {comparison.policy_version}</p><h2>Repair matrix</h2></div><span className="scope-chip">Same 12-case suite</span></div><div className="table-scroll"><table><thead><tr><th>Case</th><th>Promise</th>{comparison.runs.map(run => <th key={run.id}>{run.target_alias.replace('demo-','')}</th>)}</tr></thead><tbody>{comparison.rows.map(row => <tr key={row.case_id}><td><code>{row.case_id}</code></td><td>{row.name}</td>{row.outcomes.map(outcome => <td key={outcome.run_id}><StatusBadge value={outcome.verdict}/></td>)}</tr>)}</tbody></table></div></section>}
  </>
}

function ReportsView({ runs }: { runs: Run[] }) {
  const completed = runs.filter(run => run.state === 'completed' && run.assessment)
  const [busy, setBusy] = useState('')
  const [message, setMessage] = useState('')
  async function download(run: Run, format: 'report_html'|'results_json') { const key=run.id+format; setBusy(key); setMessage(''); try { const artifact=await api.artifact(run.id,format); window.location.assign(artifact.download_path); setMessage(`Artifact ready · SHA-256 ${artifact.sha256.slice(0,16)}…`) } catch(e){ setMessage(e instanceof Error?e.message:'Export failed') } finally{setBusy('')} }
  return <><header className="page-head"><div><p className="eyebrow">Engineer + mentor handoff</p><h1>Evidence with honest boundaries.</h1><p>Every artifact includes the tested case denominator, build, policy and incomplete context.</p></div></header>
    <section className="report-list">{completed.map(run => <article className="card report-row" key={run.id}><div className={`report-mark ${run.assessment === 'blocked' ? 'danger' : ''}`}>{run.assessment === 'blocked' ? '!' : '✓'}</div><div><p className="eyebrow">{run.id}</p><h2>{run.target_alias.replace('demo-','')}</h2><p>{run.counts.pass} pass · {run.counts.violation} violations · {run.counts.inconclusive} inconclusive · {run.request_count} requests</p></div><StatusBadge value={run.assessment}/><div className="report-actions"><button className="button secondary compact" disabled={!!busy} onClick={()=>download(run,'report_html')}>HTML report</button><button className="button secondary compact" disabled={!!busy} onClick={()=>download(run,'results_json')}>JSON evidence</button></div></article>)}{!completed.length && <section className="empty-state"><h2>Complete a run first</h2><p>Reports are generated only from persisted evidence.</p></section>}</section>{message && <div className="toast" role="status">{message}</div>}
  </>
}

export default function App() {
  const [auth, setAuth] = useState<'loading'|'login'|'ready'>('loading')
  const [view, setView] = useState<View>('runs')
  const [targets, setTargets] = useState<Target[]>([])
  const [runs, setRuns] = useState<Run[]>([])
  const [selectedRun, setSelectedRun] = useState<Run | null>(null)
  const [policy, setPolicy] = useState<any>(null)
  const [spec, setSpec] = useState<any>(null)

  const loadRuns = useCallback(async () => {
    const list = await api.runs(); setRuns(list)
    if (selectedRun) { const updated = await api.run(selectedRun.id); setSelectedRun(updated) }
  }, [selectedRun?.id])
  const loadWorkspace = useCallback(async () => {
    const [targetData, runData, policyData, specData] = await Promise.all([api.targets(), api.runs(), api.policy(), api.spec()])
    setTargets(targetData); setRuns(runData); setPolicy(policyData); setSpec(specData)
    if (runData[0]) setSelectedRun(await api.run(runData[0].id))
  }, [])
  useEffect(() => { api.restoreSession().then(() => setAuth('ready')).catch(() => setAuth('login')) }, [])
  useEffect(() => { if (auth === 'ready') loadWorkspace().catch(() => setAuth('login')) }, [auth, loadWorkspace])
  useEffect(() => { window.scrollTo(0, 0) }, [view])
  const active = useMemo(() => runs.some(run => ['queued','running'].includes(run.state)), [runs])
  useEffect(() => { if (!active || auth !== 'ready') return; const timer=window.setInterval(() => loadRuns().catch(()=>undefined),1000); return()=>window.clearInterval(timer) }, [active, auth, loadRuns])
  async function select(run: Run) { setSelectedRun(await api.run(run.id)) }
  async function logout() { await api.logout().catch(()=>undefined); setAuth('login') }
  if (auth === 'loading') return <main className="boot"><div className="mark mark-large">B</div><div className="spinner light-spinner"/><p>Opening local workbench…</p></main>
  if (auth === 'login') return <Login onLogin={() => setAuth('ready')}/>
  return <div className="app-shell"><SideNav view={view} setView={setView} logout={logout}/><main className="content">
    <div className="topbar"><span><i/>Live local control plane</span><span>Policy <code>invoice-policy-v1</code></span></div>
    {view === 'runs' && <RunsView targets={targets} runs={runs} selectedRun={selectedRun} select={select} refresh={loadRuns}/>}
    {view === 'policy' && <PolicyView policy={policy} spec={spec}/>}
    {view === 'compare' && <CompareView runs={runs}/>}
    {view === 'reports' && <ReportsView runs={runs}/>}
  </main></div>
}
