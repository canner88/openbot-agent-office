#!/usr/bin/env node
// Live OpenBot agents -> Agent Office events on 127.0.0.1.
// Reads the local OpenBot database. Does not send messages or change agents.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { post } from './net.mjs';

const DB = process.env.OPENBOT_DB
  || path.join(process.env.APPDATA || path.join(os.homedir(), 'AppData', 'Roaming'), 'OpenBot', 'openbot.db');
const PROJECT = process.env.AGENT_OFFICE_PROJECT
  || path.join(os.homedir(), 'OpenBot', 'Shared', 'agent-office-live');
const TEAM_FILE = path.join(PROJECT, '.agent-office.json');

const SQL = `
SELECT a.agent_id AS id, a.agent_json AS json,
  (SELECT t.status FROM projection_turns t
     JOIN projection_threads th ON th.thread_id = t.thread_id
     WHERE th.agent_id = a.agent_id
     ORDER BY t.started_at DESC LIMIT 1) AS turn_status,
  (SELECT th.title FROM projection_threads th
     WHERE th.agent_id = a.agent_id
     ORDER BY th.updated_at DESC LIMIT 1) AS title,
  (SELECT m.item_type FROM projection_thread_messages m
     JOIN projection_threads th ON th.thread_id = m.thread_id
     WHERE th.agent_id = a.agent_id
     ORDER BY m.created_at DESC LIMIT 1) AS item,
  (SELECT COUNT(*) FROM agent_waits w
     WHERE w.agent_id = a.agent_id AND w.woken_at IS NULL) AS waits
FROM projection_agents a
`;

const clip = (s, n = 140) => {
  const t = String(s || '').replace(/\s+/g, ' ').trim();
  return t.length > n ? t.slice(0, n - 1) + '…' : t;
};

function slug(name, id) {
  const map = { ç: 'c', ğ: 'g', ı: 'i', ö: 'o', ş: 's', ü: 'u', Ç: 'c', Ğ: 'g', İ: 'i', Ö: 'o', Ş: 's', Ü: 'u' };
  const raw = [...String(name || '')].map((ch) => map[ch] || ch).join('');
  let s = raw.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  if (!s || s === 'manager') s = 'agent';
  return s;
}

function kindOf(name, title) {
  const n = `${name} ${title}`.toLocaleLowerCase('tr-TR');
  if (/director|görev|architect|borg/.test(n)) return 'backend';
  if (/whatsapp|telegram|sosyal|mesaj/.test(n)) return 'devops';
  if (/copy|research|search|planner|içerik/.test(n)) return 'docs';
  if (/bug|prototype|skill|rea|review|launch/.test(n)) return 'qa';
  if (/frontend|design|ux/.test(n)) return 'frontend';
  return 'data';
}

function readAgents() {
  const db = new DatabaseSync(DB, { readOnly: true, timeout: 1500 });
  try {
    const rows = db.prepare(SQL).all().filter((r) => String(r.id || '').startsWith('agent-'));
    const used = new Map();
    return rows.map((row) => {
      let profile = {};
      try { profile = JSON.parse(row.json || '{}'); } catch { /* bad row */ }
      const name = clip(profile.name || 'agent', 40);
      let id = slug(name, row.id);
      if (used.has(id)) id = `${id}-${String(row.id).slice(-4)}`;
      used.set(id, true);
      const running = row.turn_status === 'running';
      const waiting = Number(row.waits) > 0;
      const status = waiting ? 'wait' : running ? 'work' : 'rest';
      return {
        openbotId: String(row.id),
        id,
        name,
        kind: kindOf(name, profile.title || ''),
        role: clip(profile.title || '', 80),
        status,
        task: clip(row.title || '', 100),
        item: String(row.item || 'edit'),
      };
    });
  } finally {
    db.close();
  }
}

function writeTeam(agents) {
  fs.mkdirSync(PROJECT, { recursive: true });
  const body = {
    team: agents.map((a) => ({ id: a.id, name: a.name, kind: a.kind, role: a.role, openbotId: a.openbotId })),
    docker: false,
    logs: [],
    source: 'openbot',
  };
  const next = JSON.stringify(body, null, 2);
  const prev = fs.existsSync(TEAM_FILE) ? fs.readFileSync(TEAM_FILE, 'utf8') : '';
  if (prev !== next) fs.writeFileSync(TEAM_FILE, next);
}

const toolOf = (item) => {
  const i = String(item || '').toLowerCase();
  if (i.includes('bash') || i === 'cmd') return 'Bash';
  if (i.includes('read') || i.includes('grep')) return 'Read';
  if (i.includes('question') || i === 'ask') return 'Ask';
  if (i.includes('agent') || i.includes('delegate')) return 'Agent';
  return 'Edit';
};

const seen = new Map();
let lastPresence = '';

async function tick() {
  const agents = readAgents();
  writeTeam(agents);
  const events = [];
  const ids = new Set(agents.map((a) => a.id));
  for (const id of [...seen.keys()]) {
    if (!ids.has(id)) {
      events.push({ hook: 'SubagentStop', agent_type: id, agent_id: seen.get(id).openbotId });
      seen.delete(id);
    }
  }
  for (const a of agents) {
    const prev = seen.get(a.id);
    const sig = `${a.status}|${a.task}|${a.item}`;
    if (!prev) {
      if (a.status === 'work' || a.status === 'wait') {
        events.push({ hook: 'SubagentStart', agent_type: a.id, agent_id: a.openbotId });
        events.push({
          hook: 'PreToolUse', agent_type: a.id, agent_id: a.openbotId, tool: toolOf(a.item),
          input: { description: a.task || a.name, subagent_type: a.id },
        });
      }
    } else if (prev.sig !== sig) {
      if ((a.status === 'work' || a.status === 'wait') && prev.status === 'rest') {
        events.push({ hook: 'SubagentStart', agent_type: a.id, agent_id: a.openbotId });
      }
      if (a.status === 'work' || a.status === 'wait') {
        events.push({
          hook: 'PreToolUse', agent_type: a.id, agent_id: a.openbotId, tool: toolOf(a.item),
          input: { description: a.task || a.status, subagent_type: a.id },
        });
      }
      if (a.status === 'rest' && prev.status !== 'rest') {
        events.push({ hook: 'SubagentStop', agent_type: a.id, agent_id: a.openbotId });
      }
    }
    seen.set(a.id, { sig, status: a.status, openbotId: a.openbotId });
  }
  const people = agents.map((a) => ({ id: a.id, name: a.name, status: a.status, task: a.task || '', openbotId: a.openbotId }));
  const presenceSig = people.map((p) => `${p.id}|${p.status}|${p.task}`).join('\n');
  if (presenceSig !== lastPresence) {
    lastPresence = presenceSig;
    events.push({ hook: 'Presence', people });
  }
  if (events.length) await post(events);
  return agents.length;
}

const director = () => {
  /* director keeps their own room; the office manager seat is the local session */
};

await post({ hook: 'SessionStart', cwd: PROJECT, source: 'openbot' });
director();
let fails = 0;
for (;;) {
  try {
    const n = await tick();
    if (fails) console.log(`bridge ok, ${n} agents`);
    fails = 0;
  } catch (err) {
    fails += 1;
    if (fails === 1 || fails % 15 === 0) console.error(`bridge: ${err.message}`);
  }
  await new Promise((r) => setTimeout(r, 2000));
}
