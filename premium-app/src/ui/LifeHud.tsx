import { AnimatePresence, motion } from 'motion/react';
import { useOffice } from '../store/useOffice';
import { Btn } from './common';

export function LifeHud() {
  const hint = useOffice((s) => s.hint);
  const style = useOffice((s) => s.cameraStyle);
  const blocked = useOffice((s) => !!(s.chatWith || s.modal || s.menuOpen));
  return (
    <>
      {style === 'first' && !blocked && (
        <div className="pointer-events-none fixed left-1/2 top-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/80 shadow-[0_0_6px_rgba(0,0,0,0.8)]" />
      )}
      <AnimatePresence>
        {hint && !blocked && (
          <motion.div key={hint} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }}
            className="pointer-events-none fixed bottom-28 left-1/2 z-20 -translate-x-1/2 rounded-xl border border-white/15 bg-slate-950/85 px-4 py-2.5 text-[14px] font-semibold shadow-xl">
            {/^(Press E|E ile|E ·)/.test(hint) ? <><span className="kbd mr-2">E</span>{hint.replace(/^(Press E( ·)?|E ile|E ·)\s*/, '')}</> : hint}
          </motion.div>
        )}
      </AnimatePresence>
      <div className="pointer-events-none fixed bottom-4 left-1/2 z-20 flex -translate-x-1/2 flex-wrap items-center justify-center gap-x-3 gap-y-1 rounded-xl bg-slate-950/60 px-3 py-2 text-[11.5px] text-muted">
        <span><span className="kbd">W</span><span className="kbd">A</span><span className="kbd">S</span><span className="kbd">D</span> yürü</span>
        <span><span className="kbd">Shift</span> koş</span>
        <span><span className="kbd">Space</span> zıpla</span>
        <span><span className="kbd">E</span> etkile</span>
        <span><span className="kbd">V</span> 1. / 3. şahıs</span>
        <span>tıkla → fareyle bak · sürüklemek de olur</span>
        <span><span className="kbd">Esc</span> menü</span>
      </div>
    </>
  );
}

export function PauseMenu() {
  const s = useOffice();
  return (
    <motion.div className="pointer-events-auto fixed inset-0 z-40 flex items-center justify-center bg-black/55" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      <motion.div initial={{ scale: 0.96 }} animate={{ scale: 1 }} className="panel w-[340px] p-5">
        <h2 className="mb-1 text-[18px] font-bold">Duraklatıldı</h2>
        <p className="mb-4 text-[12.5px] text-muted">Sen dururken takım çalışmaya devam eder.</p>
        <div className="flex flex-col gap-2">
          <Btn variant="primary" onClick={() => s.setMenu(false)}>Yürümeye devam</Btn>
          <Btn onClick={() => s.setCameraStyle(s.cameraStyle === 'third' ? 'first' : 'third')}>Kamera: {s.cameraStyle === 'third' ? '3. şahıs → 1. şahsa geç' : '1. şahıs → 3. şahsa geç'}</Btn>
          <Btn onClick={() => { s.setMenu(false); s.openModal('whiteboard'); }}>Proje tahtasını aç</Btn>
          <Btn onClick={() => { s.setMenu(false); s.setDashboard(!s.dashboardOpen); }}>Panoyu {s.dashboardOpen ? 'gizle' : 'göster'}</Btn>
          <Btn onClick={() => s.setMode('overview')}>Genel bakışa dön</Btn>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-1 text-[11.5px] text-muted">
          <span><span className="kbd">WASD</span> yürü</span><span><span className="kbd">Shift</span> koş</span>
          <span><span className="kbd">Space</span> zıpla</span><span><span className="kbd">E</span> konuş / kullan</span>
          <span><span className="kbd">V</span> kamera</span><span><span className="kbd">Esc</span> menü</span>
        </div>
      </motion.div>
    </motion.div>
  );
}
