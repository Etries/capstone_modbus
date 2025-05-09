import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function LED({ label, state }) {
  return (
    <div className="led-container">
      <div className={`led ${state ? 'on' : 'off'}`}></div>
      <span>{label}</span>
    </div>
  );
}

function RegisterBox({ label, value }) {
  return (
    <div className="reg-box font-digital bg-slate-800 text-white">
      <label>{label}</label>
      <div className="reg-value font-digital">{value}</div>
    </div>
  );
}

function App() {
  const [ip, setIp] = useState('');
  const [port, setPort] = useState('8000');
  const [token, setToken] = useState('');
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const pollingRef = useRef(null);

  const fetchData = async () => {
    try {
      setError('');
      const res = await fetch(`http://${ip}:${port}/`, {
        headers: {
          'Authorization': `Token ${token}`
        }
      });
      if (!res.ok) throw new Error('Unauthorized or server error');

      const json = await res.json();
      setData(json);

      if (!pollingRef.current) {
        pollingRef.current = setInterval(fetchData, 1000);
      }

    } catch (err) {
      setError(err.message);
      setData(null);

      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    }
  };

  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);

  const parseBools = (s) => s?.split(',').map(b => b.trim() === '1') || [];
  const parseInts = (s) => s?.split(',').map(v => parseInt(v.trim(), 10)) || [];

  return (
    <div className='w-screen h-screen flex flex-col py-6 justify-center items-center space-y-5'>
      <div className="w-full flex flex-wrap gap-4 justify-center align-center">
        <input type="text" placeholder="IP Address" value={ip} onChange={e => setIp(e.target.value)} />
        <input type="text" placeholder="Port" value={port} onChange={e => setPort(e.target.value)} />
        <input type="text" placeholder="Token" value={token} onChange={e => setToken(e.target.value)} />
        <button onClick={fetchData}>Fetch Modbus Data</button>
      </div>

      {error && <p className="text-red-500">{error}</p>}

      {data && (
        <div className='w-full max-w-4xl border-slate-800 shadow-2xl border border-2 bg-gray-200 flex flex-col p-6 rounded-xl'>
          <div className="modbus-box">
            <div className="meta">
              <p><strong>User:</strong> {data.user}</p>
              <p><strong>IP:</strong> {data.ip}</p>
            </div>

            <div className="register-grid">
              <div className="reg-row items-center">
                <div>Registers Input: &nbsp;&nbsp;</div>
                {parseInts(data.ir).map((val, i) => (
                  <RegisterBox key={i} label={`IR${i}`} value={val} />
                ))}
              </div>
              <div className="reg-row items-center">
                <div>Holding Registers: </div>
                {parseInts(data.hr).map((val, i) => (
                  <RegisterBox key={i} label={`HR${i}`} value={val} />
                ))}
              </div>
            </div>

            <div className="led-panel">
              <div className="led-section">
                <h4>Output Coils</h4>
                <div className="led-strip">
                  {parseBools(data.co).map((val, i) => (
                    <LED key={i} label={`CO${i}`} state={val} />
                  ))}
                </div>
              </div>
              <div className="led-section">
                <h4>Discrete Inputs</h4>
                <div className="led-strip">
                  {parseBools(data.di).map((val, i) => (
                    <LED key={i} label={`DI${i}`} state={val} />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

