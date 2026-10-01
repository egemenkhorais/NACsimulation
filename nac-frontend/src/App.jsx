import { useState, useEffect } from 'react';
import { loginDevice, getDevices, getLogs } from './services/api';

function App() {
  const [mac, setMac] = useState('AA:BB:CC:DD:EE:FF');
  const [username, setUsername] = useState('egemen.keles');
  const [password, setPassword] = useState('AdminPassword123!');

  const [devices, setDevices] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loginStatus, setLoginStatus] = useState(null);
  const [liveFlows, setLiveFlows] = useState([]);

  const fetchData = async () => {
    try {
      const devicesData = await getDevices();
      const logsData = await getLogs();
      setDevices(devicesData || []);
      setLogs(logsData || []);
    } catch (error) {
      console.error("Veri çekme hatası:", error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const flowInterval = setInterval(() => {
      const ports = [80, 443, 22, 3389, 53, 445];
      const flags = ["SYN", "ACK", "PSH,ACK", "FIN"];
      const isAttack = Math.random() > 0.85;

      const newFlow = {
        id: Date.now(),
        time: new Date().toLocaleTimeString('tr-TR'),
        mac: `AA:BB:CC:DD:EE:${Math.floor(Math.random()*99).toString().padStart(2, '0')}`,
        port: ports[Math.floor(Math.random() * ports.length)],
        size: Math.floor(Math.random() * 1400) + 64,
        flag: flags[Math.floor(Math.random() * flags.length)],
        status: isAttack ? 'DETECTED' : 'CLEAN'
      };

      setLiveFlows(prev => [newFlow, ...prev].slice(0, 6));
    }, 2000);
    return () => clearInterval(flowInterval);
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const result = await loginDevice(username, password, mac);
      setLoginStatus({ type: 'success', data: result });
      fetchData();
    } catch (error) {
      setLoginStatus({ type: 'error', data: error.response?.data || { detail: "Bağlantı hatası" } });
    }
      finally {
      // Başarılı da olsa, Zero Trust gereği başarısız da olsa TABLOYU YENİLE!
      fetchData();
      }
  };

  const getVlanBadge = (vlan) => {
    switch (vlan) {
      case 10: return <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-bold rounded border border-emerald-500/20 shadow-[0_0_10px_rgba(52,211,153,0.1)]">VLAN 10 (Üretim)</span>;
      case 66: return <span className="px-2 py-1 bg-amber-500/10 text-amber-400 text-xs font-bold rounded border border-amber-500/20 shadow-[0_0_10px_rgba(251,191,36,0.1)]">VLAN 66 (Karantina)</span>;
      case 99: return <span className="px-2 py-1 bg-rose-500/10 text-rose-400 text-xs font-bold rounded border border-rose-500/20 shadow-[0_0_10px_rgba(244,63,94,0.1)]">VLAN 99 (İzole)</span>;
      default: return <span className="px-2 py-1 bg-slate-700 text-slate-300 text-xs font-bold rounded border border-slate-600">VLAN {vlan}</span>;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 font-sans selection:bg-cyan-900/50">
      {/* HEADER */}
      <header className="bg-slate-900/50 backdrop-blur-md border-b border-slate-800/80 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 shrink-0">
              <span className="text-white font-black text-xl">N</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-wide">ZeroTrust <span className="text-cyan-400">NAC</span></h1>
              <p className="text-slate-500 text-xs font-mono uppercase tracking-widest">Security Operations Center</p>
            </div>
          </div>
          <div className="flex gap-4">
            <div className="bg-slate-900 px-4 py-2 rounded-md border border-slate-700/50 shadow-inner flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-xs text-slate-400 uppercase">Aktif Ajanlar</span>
              <span className="font-bold text-white ml-2">{devices.length}</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 mt-4">

        {/* SOL PANEL (802.1X İstemci) */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-blue-600"></div>
            <h2 className="text-sm font-bold mb-6 text-white uppercase tracking-wider flex items-center gap-2">
              {/* BURADAKİ SVG İKONUNA SABİT BOYUT EKLENDİ */}
              <svg width="20" height="20" className="text-cyan-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.071 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4" /></svg>
              Auth İstemcisi (802.1X)
            </h2>

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">KULLANICI ADI</label>
                <input type="text" value={username} onChange={(e) => setUsername(e.target.value)}
                  className="w-full rounded bg-slate-950 border border-slate-800 p-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">PAROLA</label>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded bg-slate-950 border border-slate-800 p-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">MAC ADRESİ</label>
                <input type="text" value={mac} onChange={(e) => setMac(e.target.value)}
                  className="w-full rounded bg-slate-950 border border-slate-800 p-2.5 font-mono text-cyan-400 text-sm focus:outline-none focus:border-cyan-500/50 transition-all" />
              </div>
              <button type="submit" className="w-full bg-slate-800 text-white font-bold p-3 rounded border border-slate-700 hover:bg-slate-700 hover:border-cyan-500/50 hover:shadow-[0_0_15px_rgba(6,182,212,0.15)] transition-all mt-2">
                SİSTEME BAĞLAN
              </button>
            </form>

            {loginStatus && (
              <div className={`mt-5 p-4 rounded text-sm border font-mono ${loginStatus.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-rose-500/10 border-rose-500/30 text-rose-400'}`}>
                {loginStatus.type === 'success' ? '> AUTH_SUCCESS: ' : '> AUTH_FAILED: '}
                {loginStatus.data.message || loginStatus.data.detail}
              </div>
            )}
          </div>
        </div>

        {/* SAĞ PANEL */}
        <div className="lg:col-span-8 space-y-6">

          {/* Cihazlar Tablosu */}
          <div className="bg-slate-900/80 rounded-xl border border-slate-800 shadow-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center bg-slate-900">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">Ağ Envanteri & Posture</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-slate-950/50 text-slate-400 text-xs uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th className="px-6 py-4">Node Bilgisi</th>
                    <th className="px-6 py-4 text-center">Anti-Virüs</th>
                    <th className="px-6 py-4 text-center">Yama (Patch)</th>
                    <th className="px-6 py-4 text-right">Erişim İzni</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {devices.map(device => (
                    <tr key={device.id} className="hover:bg-slate-800/30 transition-colors group">
                      <td className="px-6 py-4">
                        <div className="font-bold text-slate-200">{device.hostname || 'Unknown_Device'}</div>
                        <div className="font-mono text-xs text-slate-500 group-hover:text-cyan-400 transition-colors">{device.mac_address}</div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        {device.av_active !== false ? (
                          <span className="text-emerald-400">AKTİF</span>
                        ) : (
                          <span className="text-rose-500 font-bold">KAPALI</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className={`font-mono ${device.missing_patches > 0 ? 'text-amber-400' : 'text-slate-500'}`}>
                          {device.missing_patches || 0}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">{getVlanBadge(device.assigned_vlan)}</td>
                    </tr>
                  ))}
                  {devices.length === 0 && (
                    <tr><td colSpan="4" className="text-center py-8 text-slate-600 font-mono text-xs">NO_DEVICES_FOUND</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* AI Flow Analiz Paneli */}
          <div className="bg-slate-950 rounded-xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col">
            <div className="px-4 py-3 border-b border-slate-800 flex justify-between items-center bg-slate-900/80">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-rose-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-amber-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-emerald-500/80"></div>
              </div>
              <span className="text-[10px] text-slate-400 font-mono uppercase tracking-widest">AI Flow IDS (XGBoost_Core)</span>
            </div>

            <div className="p-4 font-mono text-[13px] space-y-1 h-64 overflow-hidden relative">
              {liveFlows.map(flow => (
                <div key={flow.id} className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 py-2 border-b border-slate-800/30 opacity-90 hover:opacity-100 transition-opacity">
                  <span className="text-slate-500 w-20 shrink-0">[{flow.time}]</span>
                  <span className="text-cyan-400 w-36 shrink-0">{flow.mac}</span>
                  <span className="text-slate-400 w-20 shrink-0">P:{flow.port}</span>
                  <span className="text-emerald-400 w-16 shrink-0">{flow.flag}</span>
                  <span className="text-slate-400 w-20 shrink-0">{flow.size}B</span>

                  <span className={`font-bold ml-auto shrink-0 ${flow.status === 'CLEAN' ? 'text-emerald-500/50' : 'text-rose-500 animate-pulse bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/30'}`}>
                    {flow.status === 'CLEAN' ? 'PASS' : '!! ATTACK !!'}
                  </span>
                </div>
              ))}
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;