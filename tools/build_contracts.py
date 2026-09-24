"""Generate the specification pack's contracts and synthetic fixtures, not a scanner."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def write(path, data):
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def obj(properties, required=None):
    return {'type': 'object', 'additionalProperties': False, 'properties': properties,
            'required': list(properties) if required is None else required}

def arr(items, **kw):
    return {'type': 'array', 'items': items, **kw}

def ref(name):
    return {'$ref': '#/components/schemas/' + name}

STR = {'type': 'string', 'minLength': 1}
BOOL = {'type': 'boolean'}
INT = {'type': 'integer', 'minimum': 0}
HASH = {'type': 'string', 'pattern': '^[a-f0-9]{64}$'}
CASE_IDS = [f'C{i:02}' for i in range(1, 13)]
RUN_STATES = ['queued', 'preflight', 'running', 'finalizing', 'completed', 'failed', 'interrupted', 'cancelled']
VERDICTS = ['pass', 'violation', 'inconclusive', 'skipped']
ASSESSMENTS = ['blocked', 'incomplete', 'pass_in_scope']
LIMITS = {'max_requests': 200, 'main_request_limit': 180, 'cleanup_request_reserve': 20,
          'requests_per_second': 2, 'max_in_flight': 1, 'request_deadline_ms': 5000,
          'run_deadline_ms': 120000, 'cleanup_time_reserve_ms': 10000, 'response_body_bytes': 65536}

policy = {
    'schema_version': '1.0', 'name': 'Invoice sharing and export revocation',
    'scenario': 'invoice-sharing-v1', 'fixture_semantics_version': 'invoice-fixtures-v1',
    'identities': {
        'alice': {'relation': 'owner', 'tenant': 'A', 'credential_ref': 'lab/alice'},
        'bob': {'relation': 'collaborator', 'tenant': 'A', 'credential_ref': 'lab/bob'},
        'mallory': {'relation': 'foreign_tenant', 'tenant': 'B', 'credential_ref': 'lab/mallory'}},
    'resources': {'private_invoice': {'owner': 'alice', 'initially_shared_with': []},
                  'shared_invoice': {'owner': 'alice', 'initially_shared_with': []}},
    'rules': [
        {'id': 'private-preview', 'operation_id': 'getInvoicePreview', 'resource': 'private_invoice', 'allowed_relations': ['owner']},
        {'id': 'shared-detail', 'operation_id': 'getInvoice', 'resource': 'shared_invoice', 'allowed_relations': ['owner', 'active_collaborator']},
        {'id': 'queue-while-shared', 'operation_id': 'queueExport', 'resource': 'shared_invoice', 'allowed_relations': ['owner', 'active_collaborator']},
        {'id': 'read-export-current-access', 'operation_id': 'getExportContent', 'resource': 'shared_invoice', 'allowed_relations': ['owner', 'active_collaborator']}],
    'restricted_fields': [{'operation_id': 'getInvoice', 'pointer': '/internal_bank_ref', 'allowed_relations': ['owner']}],
    'revocation': {'operation_id': 'revokeShare', 'probe_operation_id': 'getExportContent', 'grace_ms': 2000,
                   'probe_margin_ms': 200, 'timing_anchor': 'successful_revoke_ack_monotonic',
                   'applies_to': 'fresh_bearer_requests', 'deny_statuses': [403, 404]},
    'marker_pointer': '/content_marker', 'required_cases': CASE_IDS, 'limits': LIMITS}

identity_schema = obj({'relation': {'enum': ['owner', 'collaborator', 'foreign_tenant']},
                       'tenant': {'enum': ['A', 'B']},
                       'credential_ref': {'type': 'string', 'pattern': '^lab/[a-z]+$'}})
resource_schema = obj({'owner': {'const': 'alice'}, 'initially_shared_with': arr({'enum': ['bob']}, uniqueItems=True)})
limit_schema = obj({key: {'type': 'integer', 'minimum': 1, 'maximum': value} for key, value in LIMITS.items()})
for key in ['max_in_flight']:
    limit_schema['properties'][key] = {'const': LIMITS[key]}
policy_schema = {
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    '$id': 'https://boundarylab.example/schemas/policy-v1.json',
    'title': 'BoundaryLab supported invoice policy v1',
    'description': 'Specification artifact. This intentionally supports one reviewed scenario, not an arbitrary executable DSL.',
    **obj({
        'schema_version': {'const': '1.0'}, 'name': {**STR, 'maxLength': 120},
        'scenario': {'const': 'invoice-sharing-v1'}, 'fixture_semantics_version': {'const': 'invoice-fixtures-v1'},
        'identities': obj({k: identity_schema for k in ['alice', 'bob', 'mallory']}),
        'resources': obj({k: resource_schema for k in ['private_invoice', 'shared_invoice']}),
        'rules': arr(obj({'id': STR, 'operation_id': {'enum': ['getInvoicePreview', 'getInvoice', 'queueExport', 'getExportContent']},
                          'resource': {'enum': ['private_invoice', 'shared_invoice']},
                          'allowed_relations': arr({'enum': ['owner', 'active_collaborator']}, minItems=1, uniqueItems=True)}), minItems=4, maxItems=4),
        'restricted_fields': arr(obj({'operation_id': {'const': 'getInvoice'}, 'pointer': {'const': '/internal_bank_ref'},
                                      'allowed_relations': {'const': ['owner']}}), minItems=1, maxItems=1),
        'revocation': obj({'operation_id': {'const': 'revokeShare'}, 'probe_operation_id': {'const': 'getExportContent'},
                           'grace_ms': {'type': 'integer', 'minimum': 0, 'maximum': 10000},
                           'probe_margin_ms': {'type': 'integer', 'minimum': 200, 'maximum': 1000},
                           'timing_anchor': {'const': 'successful_revoke_ack_monotonic'}, 'applies_to': {'const': 'fresh_bearer_requests'},
                           'deny_statuses': {'const': [403, 404]}}),
        'marker_pointer': {'const': '/content_marker'},
        'required_cases': {'const': CASE_IDS}, 'limits': limit_schema})}
write('contracts/policy.schema.json', policy_schema)
write('examples/invoice-policy.json', policy)

fixture = {
    'status': 'synthetic_expected_fixture_not_executed', 'semantics_version': 'invoice-fixtures-v1',
    'namespace_strategy': 'new opaque namespace per run; cleanup only owns that namespace',
    'identity_bindings': {'alice': {'tenant': 'A', 'owns': ['private_invoice', 'shared_invoice']},
                          'bob': {'tenant': 'A', 'owns': []}, 'mallory': {'tenant': 'B', 'owns': []}},
    'variants': {
        'vulnerable': {'preview_requires_only_auth': True, 'leaks_owner_field_to_collaborator': True,
                       'export_checks_creator_without_current_sharing': True, 'owner_only': False},
        'owner-only': {'preview_requires_only_auth': False, 'leaks_owner_field_to_collaborator': False,
                       'export_checks_creator_without_current_sharing': False, 'owner_only': True},
        'fixed': {'preview_requires_only_auth': False, 'leaks_owner_field_to_collaborator': False,
                  'export_checks_creator_without_current_sharing': False, 'owner_only': False}},
    'independence_rule': 'Scanner assertions must not read variant flags or use the expected-results manifest as observed evidence.',
    'lab_admin': {'create': 'POST /__lab/fixtures', 'cleanup': 'DELETE /__lab/fixtures/{namespace}',
                  'credential_ref': 'lab/factory', 'not_part_of_scanned_openapi': True},
    'c12_setup': 'Independent Alice-created export; C11 independent grant/revoke; C08 attempted independently of C05.',
    'timing': {'max_export_ready_ms': 20000, 'max_polls': 10, 'grace_ms': 2000, 'probe_margin_ms': 200}}
write('examples/fixture-manifest.json', fixture)

core = [
    ('Alice reads private preview', 'getInvoicePreview', 'alice', [], ['pass','pass','pass']),
    ('Bob denied private preview', 'getInvoicePreview', 'bob', ['C01'], ['violation','pass','pass']),
    ('Mallory denied private preview', 'getInvoicePreview', 'mallory', ['C01'], ['violation','pass','pass']),
    ('Anonymous denied private preview', 'getInvoicePreview', 'anonymous', ['C01'], ['pass','pass','pass']),
    ('Bob reads active shared detail', 'getInvoice', 'bob', [], ['pass','violation','pass']),
    ('Owner-only property absent for Bob', 'getInvoice', 'bob', ['C05'], ['violation','inconclusive','pass']),
    ('Owner retains owner-only property', 'getInvoice', 'alice', [], ['pass','pass','pass']),
    ('Bob queues export while shared', 'queueExport', 'bob', [], ['pass','violation','pass']),
    ('Bob retrieves ready export before revoke', 'getExportContent', 'bob', ['C08'], ['pass','inconclusive','pass']),
    ('Bob denied export after revocation deadline', 'getExportContent', 'bob', ['C08','C09'], ['violation','inconclusive','pass']),
    ('Bob denied detail after independent grant/revoke', 'getInvoice', 'bob', [], ['pass','pass','pass']),
    ('Alice retrieves independent owner-created export', 'getExportContent', 'alice', [], ['pass','pass','pass'])]
core_cases = [{'id': f'C{i:02}', 'name': name, 'operation_id': op, 'identity': actor,
               'required': True, 'depends_on': deps,
               'expected': dict(zip(['vulnerable','owner-only','fixed'], outcomes))}
              for i, (name,op,actor,deps,outcomes) in enumerate(core, 1)]
faults = [
    ('expired_token','Required dependent cases inconclusive; never a scoped pass'),
    ('wrong_subject','Preflight identity mismatch; no dependent probes'),
    ('grant_fails','Shared-policy prerequisites incomplete'),
    ('revoke_fails','No post-revocation finding; temporal case inconclusive'),
    ('export_timeout','Bounded polling; dependent case inconclusive'),
    ('unexpected_200_body','Without protected marker, unexpected representation is inconclusive'),
    ('denial_body_leaks_marker','403/404 containing protected marker is violation with valid controls'),
    ('build_changes','Run incomplete and not valid for fixed comparison'),
    ('policy_hash_mismatch','Comparison returns 409 NON_COMPARABLE_RUNS'),
    ('worker_crash_after_mutation','Run interrupted; mutation is not automatically replayed'),
    ('cancel','No new test traffic; bounded permitted cleanup; cancelled run'),
    ('cleanup_fails','Namespace retained with cleanup pending; no broad deletion'),
    ('oversized_body','Read bounded to 65536 decoded bytes; dependent case inconclusive'),
    ('redirect_outside_scope','Redirect not followed; destination receives zero requests'),
    ('external_ref','Import rejects without fetching external reference'),
    ('dns_rebinding','Connected address must match approved pinned resolution; unauthorized destination receives zero requests'),
    ('secret_sentinel','Zero occurrences of sentinel secret in persisted DB, logs and reports'),
    ('cross_origin_control_request','Rejected before state mutation')]
write('examples/evaluation-cases.json', {
    'status': 'expected_results_only_not_test_execution', 'suite_version': 'boundarylab-suite-v1',
    'core_cases': core_cases,
    'failure_cases': [{'id':f'F{i:02}', 'fault':name, 'expected_behavior': result} for i,(name,result) in enumerate(faults,1)],
    'expected_core_counts': {'vulnerable': {'pass':8,'violation':4,'inconclusive':0},
                             'owner-only': {'pass':7,'violation':2,'inconclusive':3},
                             'fixed': {'pass':12,'violation':0,'inconclusive':0}}})

schemas = {
    'Error': obj({'error': obj({'code': STR, 'message': STR, 'request_id': STR,
                                'details': {'type':'object','additionalProperties':True}}, ['code','message','request_id'])}),
    'IdentityReference': identity_schema,
    'PolicyDocument': policy_schema.copy(),
    'SessionRequest': obj({'bootstrap_secret': {**STR, 'writeOnly': True}}),
    'Session': obj({'operator': STR, 'csrf_token': STR, 'expires_in_seconds': {'type':'integer','minimum':1}}),
    'RestoredSession': obj({'operator': STR, 'authenticated': BOOL, 'csrf_token': STR}),
    'Target': obj({'alias':STR, 'label':STR, 'origin':STR, 'synthetic_fixture':BOOL,
                   'limits':obj({'requests':INT,'requests_per_second':INT,'in_flight':INT,'response_bytes':INT})}),
    'SpecImport': obj({'project_id':STR, 'document': {'type':'object','additionalProperties':True}}),
    'OperationCoverage': obj({'operation_id':STR, 'status': {'enum':['supported','unsupported','not_selected']}, 'reason':STR}),
    'Spec': obj({'id':STR, 'sha256':HASH, 'operations':arr(ref('OperationCoverage'))}),
    'PolicyCreate': obj({'project_id':STR, 'spec_id':STR, 'document':ref('PolicyDocument')}),
    'Policy': obj({'id':STR, 'version':{'type':'integer','minimum':1}, 'sha256':HASH, 'approved':BOOL, 'document':ref('PolicyDocument')}),
    'Approval': obj({'sha256':HASH, 'policy_owner_attestation':{**STR,'maxLength':500}}),
    'RunCreate': obj({'target_alias':STR}),
    'Fingerprints': obj({'policy_hash':HASH,'spec_hash':HASH,'suite_hash':HASH,'fixture_semantics_hash':HASH,'engine_version':STR}),
    'Counts': obj({key:INT for key in VERDICTS}),
    'Run': obj({'id':STR, 'state':{'enum':RUN_STATES}, 'assessment':{'enum':ASSESSMENTS+[None]},
                 'has_incomplete_cases':BOOL, 'target_alias':STR, 'build_id':{'type':['string','null']},
                 'counts':ref('Counts'), 'request_count':INT, 'cancellation_requested':BOOL,
                 'cleanup_status':{'enum':['not_started','pending','complete','failed']},
                 'execution_error':{'type':['string','null']}, 'created_at':STR, 'updated_at':STR,
                 'started_at':{'type':['string','null']}, 'completed_at':{'type':['string','null']}},
               ['id','state','assessment','has_incomplete_cases','target_alias','build_id','counts','request_count',
                'cancellation_requested','cleanup_status','execution_error','created_at','updated_at','started_at','completed_at']),
    'Event': obj({'id':INT,'run_id':STR,'type':STR,'message':STR,'created_at':STR}),
    'Evidence': obj({'id':STR,'operation_id':STR,'identity':STR,'method':STR,'templated_path':STR,
                      'status_code':{'type':['integer','null']},'marker_match':{'type':['boolean','null']},
                      'redacted_excerpt':{'type':'string','maxLength':8192},'start_offset_ms':INT,'duration_ms':INT,'sha256':HASH}),
    'CaseResult': obj({'case_id':STR,'required':BOOL,'verdict':{'enum':VERDICTS},'reason_code':STR,
                        'expected':STR,'observed':STR,'evidence_ids':arr(STR)}),
    'Finding': obj({'id':STR,'case_id':STR,'kind':{'enum':['security_violation','functional_regression']},
                     'category':{'enum':['bola','property_exposure','revocation','legitimate_access']},
                     'severity':{'enum':['high','medium','low']},'rule_id':STR,'explanation':STR,'evidence_ids':arr(STR)}),
    'Results': obj({'run_id':STR,'cases':arr(ref('CaseResult')),'findings':arr(ref('Finding')),'evidence':arr(ref('Evidence'))}),
    'ComparisonRequest': obj({'run_ids':arr(STR,minItems=2,maxItems=3,uniqueItems=True)}),
    'ComparisonOutcome': obj({'run_id':STR,'target_alias':STR,'build_id':{'type':['string','null']},
                              'verdict':{'enum':VERDICTS},'kind':{'type':['string','null']}}),
    'ComparisonRow': obj({'case_id':STR,'name':STR,'outcomes':arr(ref('ComparisonOutcome'),minItems=2,maxItems=3)}),
    'Comparison': obj({'compatible':{'const':True},'policy_version':STR,
                       'runs':arr(ref('Run'),minItems=2,maxItems=3),'rows':arr(ref('ComparisonRow'))}),
    'ArtifactRequest': obj({'format':{'enum':['report_html','results_json']}}),
    'Artifact': obj({'id':STR,'run_id':STR,'format':{'enum':['report_html','results_json']},
                     'sha256':HASH,'created_at':STR,'download_path':STR}),
    'DiscoveryRequest': obj({'label':{**STR,'maxLength':120},'document':{'type':'object','additionalProperties':True},
                             'har':{'type':['object','null'],'additionalProperties':True}}),
    'DiscoveryAnalysis': {'type':'object','additionalProperties':True,
                          'required':['id','label','created_at','analysis_version','spec','summary','operations',
                                      'invariant_candidates','traffic_diff','safety','limitations']},
    'ExplanationRequest': obj({'mode':{'enum':['deterministic','ai']}}),
    'Explanation': {'type':'object','additionalProperties':True,
                    'required':['id','run_id','mode','provider_status','summary','risk','root_causes',
                                'remediation_steps','regression_checks','patch_outline','limitations']},
    'Capabilities': {'type':'object','additionalProperties':True,'required':['discovery','remediation']}}
schemas['PolicyDocument'].pop('$id', None)
schemas['PolicyDocument'].pop('$schema', None)

control = {'openapi':'3.1.0', 'info':{'title':'SentinelAPI BoundaryLab control API','version':'0.2.0'},
           'servers':[{'url':'http://127.0.0.1:8080/api/v1','description':'Implemented local single-operator control plane'}],
           'security':[{'OperatorSession':[]}], 'paths':{},
           'components':{'securitySchemes':{'OperatorSession':{'type':'apiKey','in':'cookie','name':'boundarylab_session'}},'schemas':schemas}}

def add_control(path, method, operation, summary, response_schema=None, request_schema=None, status='200', public=False):
    op={'operationId':operation,'summary':summary,'responses':{status:{'description':'Successful operation'}}}
    if response_schema:
        op['responses'][status]['content']={'application/json':{'schema':response_schema}}
    op['responses']['default']={'description':'Typed error; see documentation for 401/403/409/413/422/429/503',
                                'content':{'application/json':{'schema':ref('Error')}}}
    params=[]
    import re
    for name in re.findall(r'\{([^}]+)\}',path):
        params.append({'name':name,'in':'path','required':True,'schema':STR})
    if method in ['post','delete'] and not public:
        params.append({'name':'X-CSRF-Token','in':'header','required':True,'schema':STR})
    if params: op['parameters']=params
    if request_schema: op['requestBody']={'required':True,'content':{'application/json':{'schema':request_schema}}}
    if public: op['security']=[]
    control['paths'].setdefault(path,{})[method]=op
    return op

add_control('/session','post','createSession','Local bootstrap login; Origin checked; request body not logged',ref('Session'),ref('SessionRequest'),'201',public=True)
add_control('/session','get','getSession','Restore an authenticated local session',ref('RestoredSession'))
add_control('/session','delete','deleteSession','Invalidate session',status='204')
add_control('/targets','get','listTargets','Trusted configured targets',arr(ref('Target')))
add_control('/capabilities','get','getCapabilities','Runtime discovery and remediation capability disclosure',ref('Capabilities'))
add_control('/policy','get','getPolicy','Reviewed invoice permission policy and exact hash',{'type':'object','additionalProperties':True})
add_control('/spec','get','getSpecification','Bundled target contract and operation inventory',{'type':'object','additionalProperties':True})
add_control('/discovery/analyses','post','createDiscoveryAnalysis','Passively analyze OpenAPI plus optional HAR; 2 MB cap; no external refs',ref('DiscoveryAnalysis'),ref('DiscoveryRequest'),'201')
op=add_control('/discovery/analyses','get','listDiscoveryAnalyses','List persisted passive analyses',arr(ref('DiscoveryAnalysis')))
op['parameters']=[{'name':'limit','in':'query','schema':{'type':'integer','minimum':1,'maximum':50,'default':20}}]
add_control('/runs','post','createRun','Queue a trusted target adapter and approved scenario',ref('Run'),ref('RunCreate'),'202')
op=add_control('/runs','get','listRuns','Recent runs',arr(ref('Run')))
op['parameters']=[{'name':'limit','in':'query','schema':{'type':'integer','minimum':1,'maximum':100,'default':20}}]
add_control('/runs/{run_id}','get','getRun','Run state, scoped assessment and report',{'type':'object','additionalProperties':True})
op=add_control('/runs/{run_id}/events','get','getEvents','Ordered events after cursor',obj({'events':arr(ref('Event')),'next_cursor':INT}))
op['parameters'] += [{'name':'after','in':'query','schema':{'type':'integer','minimum':0,'default':0}},{'name':'limit','in':'query','schema':{'type':'integer','minimum':1,'maximum':100,'default':100}}]
add_control('/runs/{run_id}/cancel','post','cancelRun','Idempotent cancellation request',ref('Run'),'dummy' if False else None,'202')
add_control('/comparisons','post','compareRuns','Compare 2–3 compatible completed runs; 409 on policy/case mismatch',ref('Comparison'),ref('ComparisonRequest'))
add_control('/runs/{run_id}/artifacts','post','createArtifact','Generate sanitized report with replay manifest',ref('Artifact'),ref('ArtifactRequest'),'201')
add_control('/runs/{run_id}/explanations','post','createExplanation','Persist deterministic triage or explicit opt-in structured AI remediation',ref('Explanation'),ref('ExplanationRequest'),'201')
op=add_control('/artifacts/{artifact_id}','get','getArtifact','Download authorized generated artifact')
op['responses']['200']['content']={'text/html':{'schema':{'type':'string'}},'application/json':{'schema':{'type':'object'}}}
write('contracts/control-api.openapi.json',control)

invoice = obj({'id':STR,'owner_id':STR,'tenant_id':STR,'content_marker':STR,'internal_bank_ref':STR}, ['id','owner_id','tenant_id','content_marker'])
export = obj({'id':STR,'invoice_id':STR,'creator_id':STR,'state':{'enum':['queued','ready']}})
demo = {'openapi':'3.1.0','info':{'title':'BoundaryLab synthetic invoice fixture API','version':'1.0.0',
                                'description':'Implemented synthetic test target; seeded defects are disclosed in fixture-manifest.json. No lab-admin routes are scan targets.'},
        'servers':[{'url':'http://demo-fixed:8000','description':'Informational only; scanner requires trusted target alias'}],
        'security':[{'BearerAuth':[]}], 'paths':{},
        'components':{'securitySchemes':{'BearerAuth':{'type':'http','scheme':'bearer'}},
                      'schemas':{'Invoice':invoice,'Export':export,'Error':obj({'code':STR,'message':STR})}}}

def add_demo(path,method,operation,response_schema,status='200',body=None,public=False):
    import re
    op={'operationId':operation,'responses':{status:{'description':'Expected success'}},
        'parameters':[{'name':n,'in':'path','required':True,'schema':STR} for n in re.findall(r'\{([^}]+)\}',path)]}
    if response_schema: op['responses'][status]['content']={'application/json':{'schema':response_schema}}
    for code in ['401','403','404']:
        op['responses'][code]={'description':'Authentication/permission/not-found response; protected data must not be disclosed',
                               'content':{'application/json':{'schema':ref('Error')}}}
    if body: op['requestBody']={'required':True,'content':{'application/json':{'schema':body}}}
    if public: op['security']=[]
    demo['paths'].setdefault(path,{})[method]=op

add_demo('/healthz','get','health',obj({'build_id':STR,'fixture_semantics_version':STR}),public=True)
add_demo('/v1/me','get','getMe',obj({'subject_id':STR,'tenant_id':STR}))
add_demo('/v1/invoices','get','listInvoices',arr(ref('Invoice')))
add_demo('/v1/invoices/{invoice_id}','get','getInvoice',ref('Invoice'))
add_demo('/v1/invoices/{invoice_id}/preview','get','getInvoicePreview',obj({'id':STR,'content_marker':STR}))
add_demo('/v1/invoices/{invoice_id}/shares','post','grantShare',obj({'subject_id':STR,'active':BOOL}),'201',obj({'subject_id':STR}))
add_demo('/v1/invoices/{invoice_id}/shares/{subject_id}','delete','revokeShare',None,'204')
add_demo('/v1/invoices/{invoice_id}/exports','post','queueExport',ref('Export'),'202')
add_demo('/v1/exports/{export_id}','get','getExport',ref('Export'))
add_demo('/v1/exports/{export_id}/content','get','getExportContent',obj({'invoice_id':STR,'content_marker':STR}))
write('contracts/demo-api.openapi.json',demo)
write('design/tokens.json',{'status':'implemented_design_tokens', 'colors':{'canvas':'#f3f5f8','surface':'#ffffff','ink':'#0b1b33','muted':'#536174','action':'#b4232b',
                                                            'border':'#dce2ea','danger':'#8f1e27','warning':'#855500','success':'#15365e'},
                            'spacing_px':[4,8,12,16,24,32,48], 'radius_px':12,'min_control_height_px':44,
                            'font':{'body':'system-ui, sans-serif','code':'ui-monospace, monospace'},'max_content_width_px':1360})
print('Generated 7 JSON contract/example/token artifacts.')
