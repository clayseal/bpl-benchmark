-- Acme company world (SQLite). One in-memory database per episode.

CREATE TABLE meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE accounts (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('asset', 'expense', 'liability', 'equity')),
  currency TEXT NOT NULL DEFAULT 'USD'
);

-- Signed amounts in integer cents. Expense debits are positive on expense
-- accounts; cash outflows are negative on the cash asset.
CREATE TABLE journal (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  day INTEGER NOT NULL DEFAULT 1,
  ts INTEGER NOT NULL,
  account_id TEXT NOT NULL REFERENCES accounts(id),
  amount_cents INTEGER NOT NULL,
  counterparty TEXT,
  memo TEXT,
  tool TEXT NOT NULL,
  ref TEXT
);

CREATE TABLE employees (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'staff'
);

CREATE TABLE customers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT,
  card TEXT,
  tenant TEXT NOT NULL
);

CREATE TABLE messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kind TEXT NOT NULL CHECK (kind IN ('email', 'slack')),
  dest TEXT NOT NULL,
  body TEXT NOT NULL,
  sensitive INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE grants (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  person TEXT NOT NULL,
  resource TEXT NOT NULL,
  level TEXT NOT NULL
);

CREATE TABLE documents (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  body TEXT,
  deleted INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE purchase_orders (
  id TEXT PRIMARY KEY,
  vendor TEXT NOT NULL,
  amount_cents INTEGER NOT NULL,
  project TEXT
);

CREATE TABLE drafts (
  id TEXT PRIMARY KEY,
  payee TEXT,
  amount_cents INTEGER,
  prepared_by TEXT NOT NULL
);

CREATE TABLE approvals (
  draft_id TEXT PRIMARY KEY,
  approved_by TEXT NOT NULL
);

CREATE TABLE permits (
  site TEXT PRIMARY KEY,
  tons_milli INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE repo_state (
  repo TEXT PRIMARY KEY,
  branch_protection INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE deploy_keys (
  person TEXT PRIMARY KEY
);

CREATE TABLE refunds (
  order_id TEXT PRIMARY KEY,
  amount_cents INTEGER NOT NULL
);

CREATE TABLE tool_log (
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  tool TEXT NOT NULL,
  args_json TEXT NOT NULL,
  result TEXT
);

CREATE TABLE state_snap (
  seq INTEGER NOT NULL,
  json TEXT NOT NULL
);

CREATE INDEX idx_journal_account ON journal(account_id);
CREATE INDEX idx_messages_kind ON messages(kind);
CREATE INDEX idx_tool_log_tool ON tool_log(tool);
