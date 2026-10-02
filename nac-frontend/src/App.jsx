import { useState, useEffect } from 'react';
import { loginDevice, getDevices, getLogs, updateDeviceVlan } from './services/api';

function App() {
  const [mac, setMac] = useState('AA:BB:CC:DD:EE:FF');
  const [username, setUsername] = useState('egemen.keles');
  const [password, setPassword] = useState('AdminPassword123!');

  const [devices, setDevices] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loginStatus, setLoginStatus] = useState(null);
  const [liveFlows, setLiveFlows] = useState([]);

  // --- ADMIN MODU STATE'LERİ ---
  const [isAdmin, setIsAdmin] = useState(false);
  const [selectedVlans, setSelectedVlans] = useState({});

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
    } catch (error) {
      setLoginStatus({ type: 'error', data: error.response?.data || { detail: "Bağlantı hatası" } });
    } finally {
      fetchData();
    }
  };

  // --- ADMIN FONKSİYONLARI ---
  const handleAdminLogin = () => {
    const pass = prompt("SOC Yöneticisi Parolası:");
    if (pass === "admin") {
      setIsAdmin(true);
      alert("Admin yetkileri aktif edildi! Tablodan cihazlara müdahale edebilirsiniz.");
    } else if (pass) {
      alert("Hatalı parola!");
    }
  };

  const handleVlanSelect = (deviceId, vlan) => {
    setSelectedVlans(prev => ({ ...prev, [deviceId]: vlan }));
  };

  const handleVlanChange = async (deviceId) => {
    const newVlan = selectedVlans[deviceId];
    if (!newVlan) return;

    try {
      await updateDeviceVlan(deviceId, newVlan);
      alert(`Cihaz başarıyla VLAN ${newVlan} ağına taşındı.`);
      fetchData();
    } catch (error) {
      alert("VLAN değiştirilirken hata oluştu!");
      console.error(error);
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
      <header className="bg-slate-900/50 backdrop-blur-md border-b border-slate-800/80 sticky top-0 z-50 relative">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 shrink-0">
              <span className="text-white font-black text-xl"></span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-wide">ZeroTrust <span className="text-cyan-400">NAC</span></h1>
              <p className="text-slate-500 text-xs font-mono uppercase tracking-widest">Security Operations Center</p>
            </div>
          </div>

          <div className="flex gap-4 items-center">
            {/* ADMIN GİRİŞ BUTONU */}
            <button
              onClick={isAdmin ? () => setIsAdmin(false) : handleAdminLogin}
              className={`px-4 py-2 rounded-md text-xs font-bold transition-all border relative z-20 cursor-pointer ${isAdmin ? 'bg-rose-500/20 text-rose-400 border-rose-500/30 hover:bg-rose-500/30' : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'}`}
            >
              {isAdmin ? "Admin Çıkış" : "Admin Girişi"}
            </button>

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
        <div className="lg:col-span-4 relative">
          <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden rounded-xl">
            <div className="absolute top-[-10%] left-[-10%] w-[300px] h-[300px] bg-cyan-600/10 rounded-full blur-[80px]"></div>
            <div className="absolute bottom-[-10%] right-[-10%] w-[300px] h-[300px] bg-blue-600/10 rounded-full blur-[80px]"></div>
          </div>

          <div className="relative z-10 bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-xl p-6 shadow-2xl overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-blue-600"></div>
            <h2 className="text-sm font-bold mb-6 text-white uppercase tracking-wider flex items-center gap-2">
              <svg width="20" height="20" className="text-cyan-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.071 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4" />
              </svg>
              Auth İstemcisi (802.1X)
            </h2>

            <form onSubmit={handleLogin} className="space-y-5 relative z-20">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1.5">KULLANICI ADI</label>
                <input type="text" value={username} onChange={(e) => setUsername(e.target.value)}
                  className="relative z-30 w-full bg-slate-950/80 border border-slate-800 rounded p-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1.5">PAROLA</label>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                  className="relative z-30 w-full bg-slate-950/80 border border-slate-800 rounded p-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1.5">MAC ADRESİ</label>
                <input type="text" value={mac} onChange={(e) => setMac(e.target.value)}
                  className="relative z-30 w-full bg-slate-950/80 border border-slate-800 rounded p-2.5 font-mono text-cyan-400 text-sm focus:outline-none focus:border-cyan-500/50 transition-all uppercase tracking-widest" />
              </div>
              <button type="submit" className="relative z-30 w-full bg-slate-800 text-white font-bold py-3.5 rounded-lg border border-slate-700 hover:bg-slate-700 hover:border-cyan-500/50 shadow-[0_0_15px_rgba(0,0,0,0.2)] hover:shadow-[0_0_20px_rgba(6,182,212,0.2)] active:scale-[0.98] cursor-pointer transition-all mt-6 flex justify-center items-center gap-2">
                SİSTEME BAĞLAN
              </button>
            </form>

            {loginStatus && (
              <div className={`mt-6 p-4 rounded-lg text-sm border font-mono relative z-20 ${loginStatus.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-rose-500/10 border-rose-500/30 text-rose-400'}`}>
                {loginStatus.type === 'success' ? '> AUTH_SUCCESS: ' : '> AUTH_FAILED: '}
                {loginStatus.data.message || loginStatus.data.detail}
              </div>
            )}
          </div>
        </div>

        {/* SAĞ PANEL */}
        <div className="lg:col-span-8 space-y-6">

          {/* Cihazlar Tablosu */}
          <div className="bg-slate-900/80 rounded-xl border border-slate-800 shadow-xl overflow-hidden relative z-10">
            <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center bg-slate-900">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">Ağ Envanteri & Posture</h2>
            </div>
            <div className="overflow-x-auto overflow-visible">
              <table className="w-full text-sm text-left">
                <thead className="bg-slate-950/50 text-slate-400 text-xs uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th className="px-6 py-4">Node Bilgisi</th>
                    <th className="px-6 py-4 text-center">Anti-Virüs</th>
                    <th className="px-6 py-4 text-center">Eksik Yama</th>
                    <th className="px-6 py-4 text-center">Mevcut VLAN</th>
                    {/* ADMİN AKTİF İSE AKSİYON SÜTUNU */}
                    {isAdmin && <th className="px-6 py-4 text-right">NAC Aksiyonu</th>}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {devices?.map(device => (
                    <tr key={device.id} className="hover:bg-slate-800/30 transition-colors group">
                      <td className="px-6 py-4">
                        <div className="font-bold text-slate-200">{device.hostname || 'Unknown_Device'}</div>
                        <div className="font-mono text-xs text-slate-500 group-hover:text-cyan-400 transition-colors">{device.mac_address}</div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        {device.av_active !== false ? (
                          <span className="text-emerald-400 font-bold">AKTİF</span>
                        ) : (
                          <span className="text-rose-500 font-bold">KAPALI</span>
                        )}
                      </td>
                      {/* EKSİK YAMA (PATCH) SÜTUNU GERİ GELDİ */}
                      <td className="px-6 py-4 text-center">
                        <span className={`font-mono font-bold ${device.missing_patches > 0 ? 'text-amber-400' : 'text-slate-500'}`}>
                          {device.missing_patches || 0}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-center">{getVlanBadge(device.assigned_vlan)}</td>

                      {/* ADMİN MÜDAHALE MENÜSÜ */}
                      {isAdmin && (
                        <td className="px-6 py-4 text-right relative z-30">
                          <div className="flex justify-end items-center gap-2">
                            <select
                              onChange={(e) => handleVlanSelect(device.id, e.target.value)}
                              className="bg-slate-950 border border-slate-700 text-slate-300 text-xs rounded p-2 focus:outline-none focus:border-cyan-500 cursor-pointer"
                              defaultValue=""
                            >
                              <option value="" disabled>Seç...</option>
                              <option value="10">Üretim (10)</option>
                              <option value="66">Karantina (66)</option>
                              <option value="99">İzole (99)</option>
                            </select>
                            <button
                              onClick={() => handleVlanChange(device.id)}
                              disabled={!selectedVlans[device.id]}
                              className="bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-bold py-2 px-3 rounded transition-all shadow-[0_0_10px_rgba(6,182,212,0.3)] cursor-pointer"
                            >
                              UYGULA
                            </button>
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                  {devices?.length === 0 && (
                    <tr><td colSpan={isAdmin ? 5 : 4} className="text-center py-8 text-slate-600 font-mono text-xs">NO_DEVICES_FOUND</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* AI Flow Analiz Paneli */}
          <div className="bg-slate-950 rounded-xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col relative z-10">
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