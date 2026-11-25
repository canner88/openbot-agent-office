// The plugin's team (from /agent-office:setup) mapped onto the premium office's five seats.
// The Manager is the main Claude session; every other role takes the seat that fits it best.
// Names are the same people as in the free office (app/src/crew.js), and each gets a
// Synty character of the matching gender.
import { setAgentIds, type AgentId } from '../types';
import { PROFILES } from '../agents';
import { assignDesks } from '../../world/layout';
import { ensureBody } from '../../world/runtime';

export interface TeamRole { id: string; name?: string; kind?: string; role?: string; openbotId?: string }

const SPECIAL: Record<string, string> = { devops: 'DevOps', ios: 'iOS', ml: 'ML', ai: 'AI', qa: 'QA', ui: 'UI', ux: 'UX', sre: 'SRE', api: 'API' };
export const prettyRole = (id: string) => id.split(/[-_ ]/).map((w) => SPECIAL[w.toLowerCase()] ?? w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

const KIND_COLOR: Record<string, string> = {
  backend: '#3b82f6', frontend: '#ec4899', devops: '#22c55e', mobile: '#0ea5e9', qa: '#a855f7',
  data: '#7c4dff', design: '#f472b6', docs: '#d97706', security: '#ef4444',
};

const COLORS = ['#3b82f6', '#ec4899', '#22c55e', '#0ea5e9', '#a855f7', '#7c4dff', '#f472b6', '#d97706', '#ef4444', '#14b8a6'];
const CAST = [
  'SK_Chr_Developer_Male_01', 'SK_Chr_Developer_Female_01', 'SK_Chr_Developer_Male_02', 'SK_Chr_Developer_Female_02',
  'SK_Chr_Business_Male_01', 'SK_Chr_Business_Female_01', 'SK_Chr_Business_Male_02', 'SK_Chr_Business_Female_02',
  'SK_Chr_Business_Male_03', 'SK_Chr_Business_Female_03', 'SK_Chr_Business_Male_04', 'SK_Chr_Business_Female_04',
];

/** Synty character per seat; changed when the team arrives. */
export const SEAT_MODEL: Record<string, string> = {
  manager: 'SK_Chr_Boss_Male_01',
  research: 'SK_Chr_Business_Male_02',
  developer: 'SK_Chr_Developer_Male_01',
  designer: 'SK_Chr_Developer_Female_01',
  qa: 'SK_Chr_Developer_Male_02',
};

/** OpenBot agent id for a seat. The director uses the manager seat. */
export const OPENBOT = new Map<string, string>();

/** role id (as Claude Code names the sub-agent) → seat */
export const roleSeat = new Map<string, AgentId>();

const isBoss = (r: TeamRole) => r.id.toLowerCase() === 'director' || /^director$/i.test(r.name ?? '');

export function seatFor(roleId: string | undefined | null): AgentId {
  if (!roleId) return 'manager';
  const id = roleId.replace(/^.*:/, '').toLowerCase();
  if (id === 'manager' || id === 'main' || id === 'director') return 'manager';
  return roleSeat.get(id) ?? (PROFILES[id] ? id : 'manager');
}

export const isVacant = (seat: AgentId) => seat !== 'manager' && !roleSeat.has(seat);

/** One desk per teammate. The director sits in the corner office. */
export function applyTeam(team: TeamRole[]): AgentId[] {
  roleSeat.clear();
  OPENBOT.clear();
  const boss = team.find(isBoss);
  const workers = team.filter((r) => r !== boss && r.id.toLowerCase() !== 'manager');
  Object.assign(PROFILES.manager, {
    name: boss?.name || 'Director',
    role: boss?.role || 'Director',
    bio: 'Köşe ofis. Görevler bu ajana gider.',
  });
  SEAT_MODEL.manager = 'SK_Chr_Boss_Male_01';
  if (boss?.openbotId) OPENBOT.set('manager', boss.openbotId);
  roleSeat.set('manager', 'manager');
  roleSeat.set('director', 'manager');
  const ids = ['manager'];
  workers.forEach((r, i) => {
    const id = r.id.toLowerCase();
    ids.push(id);
    roleSeat.set(id, id);
    PROFILES[id] = {
      id,
      name: r.name || prettyRole(id),
      role: r.role || r.name || prettyRole(id),
      color: KIND_COLOR[r.kind || ''] ?? COLORS[i % COLORS.length],
      bio: r.role || '',
    };
    SEAT_MODEL[id] = CAST[i % CAST.length];
    if (r.openbotId) OPENBOT.set(id, r.openbotId);
  });
  setAgentIds(ids);
  assignDesks(workers.map((r) => r.id.toLowerCase()));
  for (const id of ids) ensureBody(id);
  return ids;
}
