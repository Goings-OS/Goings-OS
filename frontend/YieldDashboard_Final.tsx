
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  Shield, 
  Zap, 
  Database, 
  MessageSquare, 
  PlusCircle, 
  Layout, 
  Settings, 
  Palette,
  AlertCircle
} from 'lucide-react';

const GoingsOSDashboard = () => {
  const [yield_today, setYieldToday] = useState(0);
  const target = 714.28;
  const [activeGem, setActiveGem] = useState('Prophet');

  // Simulated live data sync
  useEffect(() => {
    const timer = setInterval(() => {
      setYieldToday(prev => {
        if (prev >= target) return target;
        return Number((prev + (Math.random() * 50)).toFixed(2));
      });
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  const gems = [
    { id: '01', name: 'Prophet', role: 'Architect', icon: <TrendingUp className="w-5 h-5" /> },
    { id: '02', name: 'Scale', role: 'Money Governor', icon: <Database className="w-5 h-5" /> },
    { id: '03', name: 'Sentry', role: 'The Guard', icon: <Shield className="w-5 h-5" /> },
    { id: '04', name: 'Courier', role: 'The Flow', icon: <Zap className="w-5 h-5" /> },
    { id: '05', name: 'Marketing', role: 'The Voice', icon: <MessageSquare className="w-5 h-5" /> },
    { id: '06', name: 'Expansion', role: 'Multiplier', icon: <PlusCircle className="w-5 h-5" /> },
    { id: '07', name: 'Grace', role: 'The Experience', icon: <Layout className="w-5 h-5" /> },
    { id: '08', name: 'System', role: 'The Vortex', icon: <Settings className="w-5 h-5" /> },
    { id: '09', name: 'Vibe', role: 'The Creative', icon: <Palette className="w-5 h-5" /> },
  ];

  const progress = (yield_today / target) * 100;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      {/* Header / Nav */}
      <div className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tighter text-blue-400">GOINGS OS <span className="text-slate-500 font-normal">v2.0</span></h1>
          <p className="text-xs text-slate-400 uppercase tracking-widest">AWS of the South / Sovereign Engine</p>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-500 uppercase">System Status</div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm font-medium">VORTEX ACTIVE</span>
          </div>
        </div>
      </div>

      {/* Main Yield Monitor */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 relative overflow-hidden">
          <div className="relative z-10">
            <h2 className="text-slate-400 text-sm font-semibold uppercase mb-1">Daily Yield Target</h2>
            <div className="flex items-baseline gap-2">
              <span className="text-5xl font-black text-white">${yield_today.toFixed(2)}</span>
              <span className="text-slate-500 text-xl">/ ${target}</span>
            </div>
            
            {/* Progress Bar */}
            <div className="mt-6 h-4 bg-slate-800 rounded-full overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                className="h-full bg-gradient-to-r from-blue-600 to-cyan-400"
              />
            </div>
            <div className="mt-2 flex justify-between text-xs font-mono text-slate-500">
              <span>PROGRESS: {progress.toFixed(1)}%</span>
              <span>GAP: ${(target - yield_today).toFixed(2)}</span>
            </div>
          </div>
          {/* Subtle Background Icon */}
          <TrendingUp className="absolute -right-8 -bottom-8 w-64 h-64 text-slate-800/20 rotate-12" />
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-center">
           <div className="flex items-center gap-3 mb-4">
             <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400">
               <AlertCircle size={20} />
             </div>
             <h3 className="font-bold">Active Directive</h3>
           </div>
           <p className="text-sm text-slate-400 leading-relaxed">
             Prophet (01) recommends focusing on **Luxury Affairs** lead generation to close the ${ (target - yield_today).toFixed(2) } gap before 5:00 PM.
           </p>
           <button className="mt-6 w-full py-3 bg-blue-600 hover:bg-blue-500 transition-colors rounded-lg font-bold text-sm uppercase tracking-wider">
             Execute Strategy
           </button>
        </div>
      </div>

      {/* The Original Nine Grid */}
      <h3 className="text-slate-500 text-xs font-bold uppercase mb-4 tracking-widest">Executive Board / The Original Nine</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-9 gap-4">
        {gems.map((gem) => (
          <motion.button
            key={gem.id}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveGem(gem.name)}
            className={`p-4 rounded-xl border transition-all text-left flex flex-col gap-2 ${
              activeGem === gem.name 
              ? 'bg-blue-600 border-blue-400 text-white shadow-lg shadow-blue-500/20' 
              : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-600'
            }`}
          >
            <div className="text-[10px] font-mono opacity-60">{gem.id}</div>
            <div className={activeGem === gem.name ? 'text-white' : 'text-blue-400'}>
              {gem.icon}
            </div>
            <div className="font-bold text-xs truncate">{gem.name}</div>
          </motion.button>
        ))}
      </div>

      {/* Gem Detail Area */}
      <AnimatePresence mode='wait'>
        <motion.div
          key={activeGem}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="mt-8 p-8 bg-slate-900/50 border border-slate-800 rounded-2xl backdrop-blur-sm"
        >
          <div className="flex items-center gap-4 mb-4">
            <h2 className="text-2xl font-bold text-white">{activeGem} Intelligence</h2>
            <span className="px-3 py-1 bg-slate-800 rounded-full text-[10px] uppercase font-bold text-slate-400 tracking-tighter">
              Authorized Sync
            </span>
          </div>
          <p className="text-slate-300 max-w-2xl leading-relaxed">
            Connected to Sovereign Bridge V2. Monitoring high-intent traffic for **KIG Consulting** and **Tanita Brinkley Ent.** All parameters within Industrial standards.
          </p>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default GoingsOSDashboard;
