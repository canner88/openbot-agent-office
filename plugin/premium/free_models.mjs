#!/usr/bin/env node
// Free stand-in for the paid Synty POLYGON Office pack.
// Original box furniture and a simple named skeleton. Not a copy of Synty meshes.
// Writes ~/.agent-office/premium/models so /premium/ can open.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PREMIUM_DIR = process.env.AGENT_OFFICE_PREMIUM_DIR || path.join(os.homedir(), '.agent-office', 'premium');
const OUT = path.join(PREMIUM_DIR, 'models');

const CHARACTERS = [
  'Boss_Female_01', 'Boss_Male_01', 'Business_Female_01', 'Business_Female_02', 'Business_Female_03', 'Business_Female_04',
  'Business_Male_01', 'Business_Male_02', 'Business_Male_03', 'Business_Male_04', 'Cleaner_Female_01', 'Cleaner_Male_01',
  'Developer_Female_01', 'Developer_Female_02', 'Developer_Male_01', 'Developer_Male_02', 'Security_Female_01', 'Security_Male_01',
].map((n) => `SK_Chr_${n}`);

const BONES = [
  ['Pelvis', null, [0, 1.0, 0]],
  ['spine_01', 'Pelvis', [0, 0.14, 0]],
  ['spine_02', 'spine_01', [0, 0.14, 0]],
  ['spine_03', 'spine_02', [0, 0.14, 0]],
  ['neck_01', 'spine_03', [0, 0.1, 0]],
  ['head', 'neck_01', [0, 0.12, 0]],
  ['UpperArm_L', 'spine_03', [0.16, 0.06, 0]],
  ['lowerarm_l', 'UpperArm_L', [0.24, 0, 0]],
  ['Hand_L', 'lowerarm_l', [0.22, 0, 0]],
  ['UpperArm_R', 'spine_03', [-0.16, 0.06, 0]],
  ['lowerarm_r', 'UpperArm_R', [-0.24, 0, 0]],
  ['Hand_R', 'lowerarm_r', [-0.22, 0, 0]],
  ['Thigh_L', 'Pelvis', [0.09, -0.04, 0]],
  ['calf_l', 'Thigh_L', [0, -0.4, 0]],
  ['Foot_L', 'calf_l', [0, -0.4, 0.02]],
  ['Thigh_R', 'Pelvis', [-0.09, -0.04, 0]],
  ['calf_r', 'Thigh_R', [0, -0.4, 0]],
  ['Foot_R', 'calf_r', [0, -0.4, 0.02]],
];

const LIMB = {
  Pelvis: [0.28, 0.16, 0.18],
  spine_01: [0.26, 0.14, 0.16],
  spine_02: [0.28, 0.14, 0.16],
  spine_03: [0.32, 0.14, 0.18],
  neck_01: [0.1, 0.1, 0.1],
  head: [0.2, 0.22, 0.2],
  UpperArm_L: [0.24, 0.08, 0.08],
  lowerarm_l: [0.22, 0.07, 0.07],
  Hand_L: [0.1, 0.06, 0.04],
  UpperArm_R: [0.24, 0.08, 0.08],
  lowerarm_r: [0.22, 0.07, 0.07],
  Hand_R: [0.1, 0.06, 0.04],
  Thigh_L: [0.1, 0.4, 0.1],
  calf_l: [0.08, 0.38, 0.08],
  Foot_L: [0.1, 0.06, 0.2],
  Thigh_R: [0.1, 0.4, 0.1],
  calf_r: [0.08, 0.38, 0.08],
  Foot_R: [0.1, 0.06, 0.2],
};

function cubeGeometry() {
  const p = [];
  const n = [];
  const faces = [
    [[-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5], [0, 0, 1]],
    [[0.5, -0.5, -0.5], [-0.5, -0.5, -0.5], [-0.5, 0.5, -0.5], [0.5, 0.5, -0.5], [0, 0, -1]],
    [[-0.5, 0.5, 0.5], [0.5, 0.5, 0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5], [0, 1, 0]],
    [[-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, -0.5, 0.5], [-0.5, -0.5, 0.5], [0, -1, 0]],
    [[0.5, -0.5, 0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [0.5, 0.5, 0.5], [1, 0, 0]],
    [[-0.5, -0.5, -0.5], [-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5], [-0.5, 0.5, -0.5], [-1, 0, 0]],
  ];
  const idx = [];
  let v = 0;
  for (const f of faces) {
    for (let i = 0; i < 4; i++) { p.push(...f[i]); n.push(...f[4]); }
    idx.push(v, v + 1, v + 2, v, v + 2, v + 3);
    v += 4;
  }
  return { p: Float32Array.from(p), n: Float32Array.from(n), idx: Uint16Array.from(idx) };
}

function fit(name) {
  const n = name.replace(/^SM_(Prop|Bld|Chr)_/, '');
  const corner = (w, h, d, y = 0) => ({ t: [w / 2, y + h / 2, d / 2], s: [w, h, d] });
  const sit = (w, h, d) => ({ t: [0, h / 2, 0], s: [w, h, d] });
  if (/^Floor_|^Ceiling_/.test(n)) return corner(2.5, 0.04, 2.5, /Ceiling/.test(n) ? 2.96 : -0.04);
  if (/^Wall_|^FeatureWall|^Window_|^Pillar_|^Baseboard|^Trim_|^Garden|^Weather|^Awning/.test(n)) return corner(2.5, 3, 0.14);
  if (/^Door_|^Elevator/.test(n)) return corner(0.9, 2.2, 0.06);
  if (/^Roof_|^Stairs_/.test(n)) return corner(2.5, 0.12, 2.5, 2.9);
  if (/Desk_/.test(n)) return sit(1.6, 0.75, 0.8);
  if (/Chair_|BeanBag|Couch_|Bench/.test(n)) return sit(/Couch/.test(n) ? 1.8 : 0.55, /BeanBag/.test(n) ? 0.45 : 0.9, /Couch/.test(n) ? 0.8 : 0.55);
  if (/Monitor|Screen|TV_|Whiteboard|CorkBoard|Poster|Sign_|Darkboard|Blackboard/.test(n)) return sit(0.7, 0.45, 0.06);
  if (/Table_/.test(n)) return sit(/Conference/.test(n) ? 2.4 : 1.1, 0.75, /Conference/.test(n) ? 1.1 : 0.7);
  if (/Server_Cabinet|Fridge|Photocopier|Vending|Arcade|Jukebox|Locker/.test(n)) return sit(0.7, 1.8, 0.55);
  if (/Plant|Tree|Hedge|LampPost/.test(n)) return sit(0.45, /Tree|LampPost/.test(n) ? 1.8 : 0.7, 0.45);
  if (/Keyboard/.test(n)) return sit(0.4, 0.03, 0.14);
  if (/Mouse_/.test(n)) return sit(0.08, 0.03, 0.12);
  if (/PoolTable|TableFootball|TableTennis/.test(n)) return sit(1.8, 0.75, 1.0);
  if (/CubicalWall/.test(n)) return sit(1.5, 1.3, 0.05);
  if (/Shelf|Cabinet|Counter/.test(n)) return sit(1.0, 1.1, 0.4);
  if (/Rug_/.test(n)) return { t: [0, 0.01, 0], s: [1.6, 0.02, 1.1] };
  if (/Light_|Fluorescent|Aircon|CeilingFan/.test(n)) return { t: [0, 2.7, 0], s: [0.8, 0.08, 0.3] };
  return sit(0.22, 0.18, 0.18);
}

function colorFor(name) {
  const n = name.toLowerCase();
  if (/screen|monitor|tv_/.test(n)) return [0.15, 0.45, 0.75, 1];
  if (/floor_wood|desk|door|shelf|table/.test(n)) return [0.55, 0.38, 0.22, 1];
  if (/floor_carpet|couch|chair|rug/.test(n)) return [0.35, 0.42, 0.55, 1];
  if (/floor_tile|floor_panel|kitchen|fridge/.test(n)) return [0.75, 0.78, 0.8, 1];
  if (/floor_concrete|server|tower/.test(n)) return [0.45, 0.47, 0.5, 1];
  if (/floor_grass|plant|tree|hedge/.test(n)) return [0.25, 0.48, 0.28, 1];
  if (/wall|pillar|ceiling|trim|baseboard/.test(n)) return [0.82, 0.8, 0.75, 1];
  if (/glass|window/.test(n)) return [0.55, 0.7, 0.78, 0.45];
  if (/brick/.test(n)) return [0.55, 0.32, 0.26, 1];
  return [0.62, 0.64, 0.68, 1];
}

function gltfFromNodes(nodes, materials, meshes) {
  const geo = cubeGeometry();
  const bin = Buffer.concat([
    Buffer.from(geo.p.buffer),
    Buffer.from(geo.n.buffer),
    Buffer.from(geo.idx.buffer),
  ]);
  const pBytes = geo.p.byteLength;
  const nBytes = geo.n.byteLength;
  return {
    asset: { version: '2.0', generator: 'openbot-free-office' },
    scene: 0,
    scenes: [{ nodes: nodes.map((_, i) => i).filter((i) => nodes[i].root) }],
    nodes: nodes.map(({ name, mesh, translation, scale, children }) => {
      const o = { name };
      if (mesh !== undefined) o.mesh = mesh;
      if (translation) o.translation = translation;
      if (scale) o.scale = scale;
      if (children?.length) o.children = children;
      return o;
    }),
    meshes,
    materials,
    accessors: [
      { bufferView: 0, componentType: 5126, count: geo.p.length / 3, type: 'VEC3', min: [-0.5, -0.5, -0.5], max: [0.5, 0.5, 0.5] },
      { bufferView: 1, componentType: 5126, count: geo.n.length / 3, type: 'VEC3' },
      { bufferView: 2, componentType: 5123, count: geo.idx.length, type: 'SCALAR' },
    ],
    bufferViews: [
      { buffer: 0, byteOffset: 0, byteLength: pBytes, target: 34962 },
      { buffer: 0, byteOffset: pBytes, byteLength: nBytes, target: 34962 },
      { buffer: 0, byteOffset: pBytes + nBytes, byteLength: geo.idx.byteLength, target: 34963 },
    ],
    buffers: [{ byteLength: bin.length, uri: `data:application/octet-stream;base64,${bin.toString('base64')}` }],
  };
}

function writeProps(names) {
  const mats = [];
  const matOf = new Map();
  const meshes = [];
  const nodes = [{ name: 'props', root: true, children: [] }];
  for (const name of names) {
    const key = colorFor(name).join(',');
    let mi = matOf.get(key);
    if (mi === undefined) {
      mi = mats.length;
      matOf.set(key, mi);
      const c = colorFor(name);
      const glass = c[3] < 1;
      mats.push({
        name: /Monitor|Screen|TV_/.test(name) ? 'Screen' : glass ? 'Glass' : 'Free',
        pbrMetallicRoughness: { baseColorFactor: c, metallicFactor: 0.05, roughnessFactor: 0.85 },
        alphaMode: glass ? 'BLEND' : 'OPAQUE',
        doubleSided: glass,
      });
    }
    const meshIndex = meshes.length;
    meshes.push({ primitives: [{ attributes: { POSITION: 0, NORMAL: 1 }, indices: 2, material: mi }] });
    const { t, s } = fit(name);
    nodes[0].children.push(nodes.length);
    nodes.push({ name, mesh: meshIndex, translation: t.map((v) => Math.round(v * 1000) / 1000), scale: s });
  }
  const gltf = gltfFromNodes(nodes, mats, meshes);
  fs.writeFileSync(path.join(OUT, 'office_props.gltf'), JSON.stringify(gltf));
}

function shirt(model) {
  if (/Boss/.test(model)) return [0.12, 0.14, 0.2, 1];
  if (/Security/.test(model)) return [0.1, 0.16, 0.32, 1];
  if (/Cleaner/.test(model)) return [0.2, 0.38, 0.28, 1];
  if (/Developer/.test(model)) return [0.18, 0.32, 0.62, 1];
  if (/Female/.test(model)) return [0.45, 0.28, 0.42, 1];
  return [0.28, 0.32, 0.38, 1];
}

function writeCharacter(model) {
  const skin = [0.86, 0.7, 0.55, 1];
  const cloth = shirt(model);
  const materials = [
    { name: 'Skin', pbrMetallicRoughness: { baseColorFactor: skin, roughnessFactor: 0.7, metallicFactor: 0 } },
    { name: 'Cloth', pbrMetallicRoughness: { baseColorFactor: cloth, roughnessFactor: 0.8, metallicFactor: 0 } },
  ];
  const meshes = [0, 1].map((material) => ({ primitives: [{ attributes: { POSITION: 0, NORMAL: 1 }, indices: 2, material }] }));
  const index = new Map();
  const nodes = [{ name: model, root: true, children: [] }];
  const clothBones = new Set(['spine_01', 'spine_02', 'spine_03', 'UpperArm_L', 'UpperArm_R', 'Thigh_L', 'Thigh_R', 'calf_l', 'calf_r']);
  for (const [name, parent, translation] of BONES) {
    const i = nodes.length;
    index.set(name, i);
    const size = LIMB[name];
    const meshNode = nodes.length + 1;
    nodes.push({
      name,
      translation,
      children: [meshNode],
    });
    nodes.push({
      name: `${name}_mesh`,
      mesh: clothBones.has(name) ? 1 : 0,
      scale: size,
      translation: name.startsWith('UpperArm') || name.startsWith('lowerarm') || name.startsWith('Hand')
        ? [Math.sign(translation[0] || (name.endsWith('_L') ? 1 : -1)) * size[0] / 2, 0, 0]
        : name.startsWith('Thigh') || name.startsWith('calf')
          ? [0, -size[1] / 2, 0]
          : [0, size[1] / 2, 0],
    });
    if (!parent) nodes[0].children.push(i);
    else nodes[index.get(parent)].children.push(i);
  }
  fs.writeFileSync(path.join(OUT, `${model}.gltf`), JSON.stringify(gltfFromNodes(nodes, materials, meshes)));
}

const propText = fs.readFileSync(path.join(HERE, 'props.txt'), 'utf8');
const srcRoot = path.join(HERE, '..', '..', 'premium-app', 'src');
const extra = [];
function walk(dir) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) walk(p);
    else if (/\.(ts|tsx)$/.test(ent.name)) {
      const text = fs.readFileSync(p, 'utf8');
      for (const m of text.matchAll(/['"]((?:SM_[A-Za-z0-9_]+)|(?:B:[A-Za-z0-9_]+))['"]/g)) {
        const raw = m[1];
        extra.push(raw.startsWith('B:') ? `SM_Bld_${raw.slice(2)}` : raw);
      }
    }
  }
}
walk(srcRoot);
const names = [...new Set([...propText.split(/\s+/).filter((n) => n.startsWith('SM_')), ...extra])];
fs.mkdirSync(OUT, { recursive: true });
writeProps(names);
for (const model of CHARACTERS) writeCharacter(model);
fs.writeFileSync(path.join(OUT, 'manifest.json'), JSON.stringify({
  builtAt: new Date().toISOString(),
  source: 'free-stand-in',
  note: 'Original low-poly stand-ins. The paid Synty pack was not used.',
  props: names.length,
  characters: CHARACTERS.length,
  clips: 0,
}, null, 1));
console.log(`wrote ${names.length} props and ${CHARACTERS.length} characters to ${OUT}`);
