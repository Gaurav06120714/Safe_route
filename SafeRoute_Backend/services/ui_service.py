def get_test_page(seg_count: int) -> str:
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Women Safety Route API — Test Console</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body {{ font-family: 'Inter', system-ui, sans-serif; max-width: 1000px; margin: 0 auto; padding: 40px 20px; background: linear-gradient(135deg, #020617 0%, #0f172a 100%); color: #f8fafc; min-height: 100vh; }}
    h1 {{ color: #38bdf8; font-weight: 700; font-size: 2.2rem; margin-bottom: 0.5rem; text-align: center; background: -webkit-linear-gradient(#38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .subtitle {{ text-align: center; color: #94a3b8; margin-bottom: 40px; font-size: 1.1rem; }}
    .grid-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
    section {{ padding: 24px; background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px; box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5); transition: transform 0.2s; }}
    section:hover {{ transform: translateY(-2px); border-color: rgba(56, 189, 248, 0.2); }}
    h3 {{ color: #e2e8f0; font-size: 1.25rem; font-weight: 600; margin-top: 0; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }}
    button {{ padding: 10px 18px; margin-top: 12px; cursor: pointer; background: linear-gradient(135deg, #2563eb, #4f46e5); color: white; border: none; border-radius: 8px; font-weight: 500; font-family: 'Inter'; transition: all 0.2s; box-shadow: 0 4px 12px -4px rgba(37, 99, 235, 0.5); width: 100%; }}
    button:hover {{ transform: translateY(-1px); box-shadow: 0 6px 16px -4px rgba(37, 99, 235, 0.6); opacity: 0.95; }}
    button:active {{ transform: translateY(1px); box-shadow: none; }}
    button.danger {{ background: linear-gradient(135deg, #dc2626, #991b1b); box-shadow: 0 4px 12px -4px rgba(220, 38, 38, 0.5); }}
    
    .result-section {{ grid-column: 1 / -1; }}
    #out-container {{ background: #0f172a; border-radius: 12px; border: 1px solid #334155; overflow: hidden; }}
    pre {{ margin: 0; padding: 20px; color: #cbd5e1; font-size: 13px; max-height: 500px; overflow-y: auto; line-height: 1.5; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    pre::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    pre::-webkit-scrollbar-track {{ background: #0f172a; }}
    pre::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 4px; }}
    
    label {{ display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; font-size: 0.9rem; color: #cbd5e1; font-weight: 500; }}
    input {{ padding: 10px 12px; background: rgba(15, 23, 42, 0.6); color: #f8fafc; border: 1px solid #475569; border-radius: 8px; font-family: 'Inter'; outline: none; transition: border-color 0.2s; }}
    input:focus {{ border-color: #38bdf8; box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.1); }}
    .row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .full-row {{ grid-column: 1 / -1; }}
    
    .loading {{ display: inline-block; width: 16px; height: 16px; border: 3px solid rgba(255,255,255,.3); border-radius: 50%; border-top-color: #fff; animation: spin 1s ease-in-out infinite; margin-right: 8px; vertical-align: middle; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    
    .safest-route-ui {{ margin-top: 20px; }}
    .segment-card {{ background: rgba(30, 41, 59, 0.9); border: 1px solid #334155; border-radius: 8px; padding: 12px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }}
    .segment-details-btn {{ background: transparent; border: 1px solid #475569; padding: 6px 12px; margin: 0; width: auto; font-size: 12px; color: #94a3b8; box-shadow: none; }}
    .segment-details-btn:hover {{ background: #334155; color: white; transform: none; box-shadow: none; }}
    .badge {{ padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; text-transform: uppercase; }}
  </style>
</head>
<body>
  <h1>Women Safety Route API</h1>
  <div class="subtitle">Test Console • <code id="base" style="color:#818cf8;"></code> • <b>{seg_count}</b> segments loaded</div>

  <div class="grid-container">
    <section>
      <h3>✨ 1. Health Status</h3>
      <button onclick="call('/health', this)">Run System Diagnostic</button>
    </section>

    <section>
      <h3>🗺️ 2. Safest Route Finder</h3>
      <div class="row">
        <label>Start Lat <input type="text" id="startLat" value="17.4267"></label>
        <label>Start Lng <input type="text" id="startLng" value="78.3368"></label>
        <label>End Lat <input type="text" id="endLat" value="17.4455"></label>
        <label>End Lng <input type="text" id="endLng" value="78.3317"></label>
      </div>
      <button onclick="safestRoute(this)">Calculate Safest Route</button>
    </section>

    <section>
      <h3>🔥 3. Live Heatmap</h3>
      <button onclick="heatmap(this)">Generate Heatmap</button>
    </section>

    <section>
      <h3>🚨 4. Report Crime Incident</h3>
      <div class="row">
        <label>Lat <input type="text" id="crimeLat" value="17.4345"></label>
        <label>Lng <input type="text" id="crimeLng" value="78.3550"></label>
        <label class="full-row">Description <input type="text" id="crimeDesc" value="Suspicious activity"></label>
        <label>Severity (1-10) <input type="number" id="crimeSev" value="5"></label>
      </div>
      <button onclick="reportCrime(this)" class="danger">Submit Incident Report</button>
    </section>

    <section class="result-section">
      <h3>Console Output</h3>
      <div id="out-container">
        <pre id="out">Connect to the API by running a command...</pre>
      </div>
    </section>
  </div>

  <script>
    const base = window.location.origin;
    document.getElementById('base').textContent = base;
    const pre = document.getElementById('out');
    
    function setBtnLoading(btn, isLoading, originalText) {{
      if (isLoading) {{
        btn.innerHTML = `<span class="loading"></span> Processing...`;
        btn.disabled = true;
      }} else {{
        btn.innerHTML = originalText;
        btn.disabled = false;
      }}
    }}

    function out(obj) {{ 
      pre.textContent = typeof obj === 'string' ? obj : JSON.stringify(obj, null, 2); 
    }}
    
    async function call(path, btn) {{
      const originalText = btn.innerHTML;
      setBtnLoading(btn, true, originalText);
      try {{ 
        const res = await fetch(base + path);
        out(await res.json());
      }} catch (e) {{ 
        out('Error: ' + e.message); 
      }} finally {{
        setBtnLoading(btn, false, originalText);
      }}
    }}

    async function safestRoute(btn) {{
      const originalText = btn.innerHTML;
      setBtnLoading(btn, true, originalText);
      const body = {{
        start: {{ lat: parseFloat(document.getElementById('startLat').value), lng: parseFloat(document.getElementById('startLng').value) }},
        end:   {{ lat: parseFloat(document.getElementById('endLat').value),   lng: parseFloat(document.getElementById('endLng').value) }},
      }};
      try {{ 
        const res = await fetch(base + '/safest_route', {{ 
          method: 'POST', 
          headers: {{'Content-Type': 'application/json'}}, 
          body: JSON.stringify(body) 
        }});
        out(await res.json());
      }} catch(e) {{ out('Error: '+e.message); }}
      finally {{ setBtnLoading(btn, false, originalText); }}
    }}

    async function heatmap(btn) {{
      const originalText = btn.innerHTML;
      setBtnLoading(btn, true, originalText);
      try {{
        const res = await fetch(base + '/heatmap/spatial');
        out(await res.json());
      }} catch(e) {{ out('Error: '+e.message); }}
      finally {{ setBtnLoading(btn, false, originalText); }}
    }}

    async function reportCrime(btn) {{
      const originalText = btn.innerHTML;
      setBtnLoading(btn, true, originalText);
      const body = {{
        lat: parseFloat(document.getElementById('crimeLat').value),
        lng: parseFloat(document.getElementById('crimeLng').value),
        description: document.getElementById('crimeDesc').value,
        severity: parseInt(document.getElementById('crimeSev').value, 10),
        incident_type: document.getElementById('crimeDesc').value,
        user_id: 'test-user',
        timestamp: new Date().toISOString()
      }};
      try {{
        const res = await fetch(base + '/crime/report', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify(body)
        }});
        out(await res.json());
      }} catch(e) {{ out('Error: '+e.message); }}
      finally {{ setBtnLoading(btn, false, originalText); }}
    }}
  </script>
</body>
</html>
"""
