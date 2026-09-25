# BoundaryLab: mentor ko kaunsa page kaise samjhana hai

**Platform mein 6 main pages hain:** Start, Discover, Define, Verify, Compare aur Handoff. Login sirf secure entry screen hai, product feature page nahi.

## Sabse simple product explanation

“BoundaryLab check karta hai ki user ka access remove hone ke baad bhi kisi purane export, report ya hidden API route se protected data mil toh nahi raha. Hum pehle API ka map banate hain, phir company ka expected access rule define karte hain, controlled real requests se behavior verify karte hain, old aur fixed build compare karte hain, aur reviewable evidence export karte hain.”

## Discover aur Verify ka one-line difference

- **Discover = map dekhna:** API contract aur optional traffic sample padhkar batata hai ki risk kahan ho sakta hai. Target API ko request nahi bhejta.
- **Verify = darwaza test karna:** Approved policy, test identities aur allowlisted target ke saath controlled HTTP requests bhejkar prove karta hai ki access sach mein allow/deny ho raha hai.

Mentor ko bolo: **“Discover possibility batata hai; Verify evidence ke saath actual behavior prove karta hai.”**

## 00 — Start page

**Page ka purpose:** 20 seconds mein problem aur complete journey samjhana.

**Kya dikhana hai:**

1. Permission change ke baad background export ya cached artifact old access retain kar sakta hai.
2. Teen primary actions: map the API, run verification, compare repair.
3. Neeche real system facts: deterministic verdict, bounded runner, persisted evidence, optional AI.

**Kya bolna hai:**

“Normal security check ek endpoint ko ek moment par test karta hai. Hum poora permission lifecycle test karte hain—access milna, data use hona, revoke hona aur revoke ke baad retrieval.”

## 01 — Discover page

**Page ka purpose:** Real OpenAPI source se attack surface aur possible authorization rules nikalna.

### Buttons ka kaam

- **Connect & import:** GitHub repository se selected OpenAPI JSON server ke through import karta hai. Public repo direct chalega; private token browser mein nahi aata.
- **Choose local file:** Local OpenAPI JSON use karta hai.
- **Choose HAR:** Optional traffic sample deta hai, jisse observed route aur documented route compare hote hain.
- **Use demo traffic:** Safe sample HAR fill karta hai, taaki shadow-route feature demonstrate ho.
- **Map API boundary:** Contract validate karta hai, operations inventory banata hai, ownership-sensitive candidates propose karta hai, optional HAR compare karta hai aur analysis persist karta hai.
- **Approve candidate / Reject:** Reviewer rationale ke saath candidate ko append-only decision ledger mein record karta hai. Tool khud policy approve nahi karta.

### Map click ke baad screen par kya dikhega

1. **Validate source** — JSON parse aur size/path limits.
2. **Inventory operations** — method, path, schema aur auth hints.
3. **Infer access risks** — resource IDs aur ownership rule candidates.
4. **Compare traffic** — optional HAR routes ka contract se diff.
5. Final card exact counts, saved analysis ID aur “No target called” show karega.

**Kya bolna hai:**

“Is step mein hum system ko attack nahi kar rahe. Hum repository ke real contract ko read karke batate hain ki human reviewer ko kaunse object-level access rules verify karne chahiye.”

## 02 — Define page

**Page ka purpose:** Business expectation ko executable policy banana.

**Kya dikhana hai:**

- Resource owner ko kya allowed hai.
- Active collaborator ko kya allowed hai.
- Revoked collaborator aur outside tenant ko kya deny hona chahiye.
- Kaunsa field sirf owner ko dikhna chahiye.
- Revocation kitne milliseconds mein effective honi chahiye.
- Policy hash aur required case count.

**Kya bolna hai:**

“OpenAPI batata hai endpoint ko call kaise karna hai. Ye page batata hai data dekhne ka haq kisko, kis state mein aur kitne time tak hai. Isi reviewed policy se verdict niklega.”

## 03 — Verify page

**Page ka purpose:** Controlled real HTTP requests se policy ka actual behavior prove karna.

### Buttons ka kaam

- **Target selector:** Vulnerable, over-restrictive ya correct implementation choose karta hai.
- **Start live verification:** Ek selected target par bounded worker run start karta hai.
- **Verify all 3 lab builds:** Teen disclosed implementations queue karta hai; worker unhe one-by-one execute karta hai.
- **Refresh runs:** Persisted backend state dobara load karta hai.
- **Recent run row:** Us run ka trace, verdicts aur evidence kholta hai.
- **Case row:** Exact sanitized request evidence drawer kholta hai.
- **Deterministic triage:** Failed cases se root-cause category aur repair outline banata hai; model key ki zarurat nahi.
- **AI review:** Configure hone par failed-case summary explain karta hai; verdict change nahi karta.

### Run ke waqt kya dikhega

1. Policy load hoti hai.
2. Test identities aur fixture prepare hote hain.
3. Grant, allowed use, revoke aur post-revoke retrieve requests run hoti hain.
4. Redacted evidence seal hota hai.
5. Har case ko pass, violation ya inconclusive verdict milta hai.

**Kya bolna hai:**

“Yahan UI animation fake scan nahi hai. Worker events database se aa rahe hain. Demo run 26 request records seal karta hai aur 12 reviewed permission cases evaluate karta hai.”

## 04 — Compare page

**Page ka purpose:** Security fix ne leak band kiya ya product hi tod diya, ye prove karna.

### Buttons ka kaam

- **Baseline selector:** Purana behavior choose karo, usually vulnerable build.
- **Candidate selector:** Proposed fixed build choose karo.
- **Evaluate release gate:** Dono reports ko same policy cases par compare karta hai.

**Kya dikhana hai:**

- **Fixed:** Pehle violation, ab pass.
- **Preserved:** Valid behavior dono builds mein pass.
- **Regressed:** Pehle pass, ab failure.
- **Unresolved:** Abhi bhi violation/inconclusive.

**Kya bolna hai:**

“Deny everyone karna secure fix nahi hai. Compare page leak close hone ke saath valid owner/collaborator behavior preserve hona bhi prove karta hai.”

## 05 — Handoff page

**Page ka purpose:** Result ko engineering, security reviewer aur CI ke liye usable artifact banana.

### Buttons ka kaam

- **Open HTML report:** Human-readable report kholta hai.
- **Download JSON evidence:** Machine-readable bundle deta hai.

**Kya bolna hai:**

“Finding screenshot par khatam nahi hoti. Evidence tested build, policy hash, case verdict aur redacted request facts ke saath handoff hota hai.”

## 4-minute demo order

1. **Start — 20 sec:** Problem aur one-line solution.
2. **Discover — 45 sec:** GitHub import, Map API boundary, four stages aur candidate result.
3. **Define — 30 sec:** Expected users, states, fields aur revocation deadline.
4. **Verify — 100 sec:** Vulnerable target run, live trace, C10 post-revoke failure aur evidence.
5. **Compare — 40 sec:** Vulnerable vs correct; fixed + preserved + no regression.
6. **Handoff — 20 sec:** HTML/JSON evidence aur CI use.

## Basic but important mentor questions

### 1. Exact problem kya hai?

Access revoke request successful ho sakti hai, lekin old export, cached report ya background artifact protected data deta reh sakta hai. Endpoint-by-endpoint scan is time/state relationship ko miss kar sakta hai. BoundaryLab declared permission promise ko complete lifecycle par test karta hai.

### 2. Authentication aur authorization mein difference?

Authentication batata hai user kaun hai. Authorization batata hai authenticated user is specific resource ko is state mein access kar sakta hai ya nahi. Valid login ke saath bhi wrong invoice/report milna authorization failure hai.

### 3. Discover aur Verify alag kyun hain?

Discover passive aur safe onboarding step hai: files read karke possible rules propose karta hai. Verify active proof step hai: reviewer-approved rule ko allowlisted environment par real requests se test karta hai. Suggestion aur proof ko separate rakhne se false confidence kam hota hai.

### 4. Map API boundary exactly kya karta hai?

OpenAPI validate karta hai, every method/path inventory karta hai, resource identifiers detect karta hai, ownership candidates propose karta hai, optional HAR se undocumented observed routes nikalta hai aur result persist karta hai. Ye target API ko request nahi bhejta.

### 5. Kya results hard-coded ya fake hain?

Lab data synthetic aur disclosed hai, taaki known ground truth repeatable rahe. Execution real hai: separate local API implementations ko actual HTTP requests jaati hain aur response status/content se verdict banta hai. Browser mein seeded result render nahi hota.

### 6. Real project par chalega?

Passive Discover real GitHub/OpenAPI source par abhi kaam karta hai. Active Verify ke liye authorized staging target, reviewed registry, controlled identities aur test resource marker chahiye. Browser arbitrary URL/token accept nahi karta; onboarding server-side reviewed config se hoti hai.

### 7. GitHub connection ka benefit?

Team wahi API contract import karti hai jo repository mein versioned hai. Result ko repository/ref/path/file SHA se trace kiya ja sakta hai. Private token configured ho toh server environment mein rehta hai.

### 8. 200 response ko violation kyun maana?

Har 200 violation nahi hai. System policy, actor state aur protected marker dekhta hai. Valid `/me` request ka 200 correct ho sakta hai; revoked user ko protected export marker ke saath 200 violation hai.

### 9. Network ya setup fail ho toh kya hota hai?

System usse pass nahi banata. Missing identity, invalid setup, timeout ya insufficient proof **inconclusive** banta hai. Ye false green result ko rokta hai.

### 10. Over-restrictive fix kaise pakadte ho?

Negative cases ke saath positive controls bhi run hote hain. Revoked/outside access deny hona chahiye, lekin owner aur active collaborator ka valid flow pass rehna chahiye. Sabko deny karne wala fix regression banega.

### 11. AI ka role kya hai?

Verdict deterministic engine decide karta hai. AI optional explanation/remediation layer hai jo failed-case summary ko readable banata hai. Model unavailable ho toh discovery, run, evidence, compare aur CI gate kaam karte hain.

### 12. Arbitrary targets ko hit karne se kaise rokte ho?

Reviewed aliases, numeric-loopback restriction for local real probes, GET-only mode, request/body/deadline budgets, one request in flight, redirect block aur browser-supplied credential rejection use hote hain. Active testing authorized staging/lab scope ke liye hai.

### 13. Existing tools se difference kya hai?

Broad API scanners overlap karte hain. BoundaryLab ka focused unit ek **permission promise over time** hai: reviewed intent, multiple identities, revoke deadline, async artifact, positive controls, evidence aur repair comparison ek workflow mein. Ye Postman/Burp/StackHawk ko replace karne ka absolute claim nahi karta.

### 14. Company pay kyun karegi?

Team ko multi-user scripts maintain, permission bugs reproduce, repair verify aur security evidence prepare karne mein engineering time lagta hai. BoundaryLab critical workflows ko repeatable release gate banata hai. Value saved manual hours, faster review, caught regressions aur maintained evidence se measure hogi.

### 15. Business model kya hai?

Start service-assisted paid staging pilot se: one API aur up to three critical workflows onboard karo. Uske baad per-application recurring subscription for maintained workflows, CI gate, evidence history aur support. Enterprise tier customer-owned runner, SSO/RBAC aur private deployment add karega.

### 16. Kya ye production ready hai?

Current product controlled local pilot ke liye working aur production-minded hai: auth, CSRF/origin checks, bounded transport, persistence, evidence redaction, recovery aur CI tests hain. Public multi-tenant SaaS ke liye Postgres, SSO/RBAC, tenant-isolated runners, managed secrets, backups/observability aur independent security review abhi next stage hai.

### 17. Strongest technical proof kya hai?

Same policy three implementations ko correctly separate karti hai: vulnerable build 8 pass/4 violations, bad owner-only repair 7 pass/2 violations/3 inconclusive, aur correct build 12/12 pass in scope. Target name verdict decide nahi karta; observed request evidence karta hai.

### 18. Sabse honest limitation kya hai?

Generic zero-setup active scanning solved nahi hai. Har real product ka permission intent aur identity setup customer-specific hota hai, isliye reviewed adapter/onboarding chahiye. Current proof one deep invoice-sharing/export lifecycle ka hai; next validation independent staging design partners hain.

## Teen lines yaad rakhna

1. **“Access revoked ek instruction hai; access actually band hua ya nahi, woh behavior prove karna padta hai.”**
2. **“Discover risk ka map banata hai; Verify real behavior ka proof deta hai.”**
3. **“Secure repair leak band karta hai bina valid product access tode.”**
