#!/usr/bin/env python3
"""
gen-skill-graph.py  —  Generate an interactive skill-graph HTML visualisation.

Usage:
  python3 scripts/gen-skill-graph.py [vault_root] [edges_json] [output_html]

Defaults:
  vault_root  = . (current directory)
  edges_json  = ops/metrics/graph/skill-edges.json   (auto-extracted by feedback-loop.sh)
  output_html = ~/.agent/diagrams/skill-graph.html

The edges_json is produced by:
  product/domain/arscontexta/reference/scripts/graph/extract-skill-edges.py

Run via feedback-loop.sh (recommended) or standalone after an edge extraction:
  python3 product/domain/arscontexta/reference/scripts/graph/extract-skill-edges.py .
  python3 scripts/gen-skill-graph.py
"""
import json, pathlib, sys

ROOT      = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(".")
EDGES_IN  = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "ops/metrics/graph/skill-edges.json"
HTML_OUT  = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else pathlib.Path.home() / ".agent/diagrams/skill-graph.html"

if not EDGES_IN.exists():
    # Fallback: re-extract on the fly
    import subprocess, sys as _sys
    extractor = ROOT / "product/domain/arscontexta/reference/scripts/graph/extract-skill-edges.py"
    if extractor.exists():
        subprocess.run([_sys.executable, str(extractor), str(ROOT), str(EDGES_IN)], check=True)
    else:
        print(f"ERROR: edges file not found: {EDGES_IN}", file=sys.stderr)
        sys.exit(1)

data = json.loads(EDGES_IN.read_text())
graph_json = json.dumps(data)

node_count = data.get("node_count", len(data.get("nodes", [])))
edge_count = data.get("edge_count", len(data.get("edges", [])))

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agent-Skills Graph</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:#0a0d14;--surface:#111520;--surface2:#161b2e;
  --border:rgba(120,140,255,0.12);
  --text:#e8ecf4;--text-dim:#6b7799;--text-muted:#3d4566;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{
  font-family:'Space Grotesk',sans-serif;background:var(--bg);color:var(--text);
  height:100vh;overflow:hidden;
  display:grid;
  grid-template-rows:56px 1fr;
  grid-template-columns:240px 1fr 260px;
  grid-template-areas:"header header header" "sidebar canvas detail";
  background-image:
    radial-gradient(ellipse 80% 60% at 60% 40%,rgba(124,106,245,0.06) 0%,transparent 70%),
    radial-gradient(ellipse 50% 40% at 20% 80%,rgba(34,211,176,0.05) 0%,transparent 60%);
}}
header{{
  grid-area:header;display:flex;align-items:center;gap:16px;padding:0 20px;
  background:rgba(17,21,32,0.92);backdrop-filter:blur(12px);
  border-bottom:1px solid var(--border);z-index:10;
}}
header h1{{font-size:15px;font-weight:600;letter-spacing:.02em;flex-shrink:0}}
header h1 span{{color:#7c6af5}}
.sw{{flex:1;max-width:300px;position:relative}}
.sw input{{
  width:100%;background:var(--surface2);border:1px solid var(--border);
  border-radius:8px;padding:7px 12px 7px 32px;
  font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--text);
  outline:none;transition:border-color .2s
}}
.sw input:focus{{border-color:rgba(124,106,245,0.5)}}
.sw input::placeholder{{color:var(--text-muted)}}
.si{{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:var(--text-dim);font-size:13px;pointer-events:none}}
.stats{{margin-left:auto;display:flex;gap:14px;font-size:12px;color:var(--text-dim)}}
.stats b{{color:var(--text);font-weight:600}}
aside{{
  grid-area:sidebar;background:var(--surface);border-right:1px solid var(--border);
  overflow-y:auto;padding:14px 10px
}}
aside::-webkit-scrollbar{{width:3px}}
aside::-webkit-scrollbar-thumb{{background:var(--border);border-radius:2px}}
.stitle{{font-size:10px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--text-muted);margin-bottom:10px;padding-left:6px}}
.ti{{display:flex;align-items:center;gap:8px;padding:7px 10px;border-radius:8px;cursor:pointer;transition:background .15s;margin-bottom:2px}}
.ti:hover,.ti.active{{background:var(--surface2)}}
.td{{width:10px;height:10px;border-radius:50%;flex-shrink:0}}
.tn{{font-size:12px;font-weight:500;flex:1}}
.tc{{font-size:11px;color:var(--text-dim);font-family:'JetBrains Mono',monospace}}
.sep{{height:1px;background:var(--border);margin:12px 0}}
.slb{{font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--text-muted);padding-left:6px;margin-bottom:8px}}
#sl{{list-style:none}}
#sl li{{
  padding:4px 10px;border-radius:6px;font-size:11.5px;
  font-family:'JetBrains Mono',monospace;color:var(--text-dim);
  cursor:pointer;transition:color .15s,background .15s;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis
}}
#sl li:hover{{color:var(--text);background:var(--surface2)}}
#sl li.hl{{color:var(--text);font-weight:500}}
#cw{{grid-area:canvas;position:relative;overflow:hidden;cursor:grab}}
#cw:active{{cursor:grabbing}}
svg{{width:100%;height:100%}}
#det{{
  grid-area:detail;background:var(--surface);border-left:1px solid var(--border);
  padding:18px 14px;overflow-y:auto;display:flex;flex-direction:column
}}
#det::-webkit-scrollbar{{width:3px}}
#det::-webkit-scrollbar-thumb{{background:var(--border);border-radius:2px}}
#de{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;color:var(--text-muted);gap:8px}}
#de .di{{font-size:30px;opacity:.35}}
#de p{{font-size:12px;line-height:1.6}}
#dc{{display:none}}
#dc.vis{{display:block}}
.db{{
  display:inline-flex;align-items:center;gap:6px;padding:3px 10px;
  border-radius:20px;font-size:11px;font-weight:600;
  text-transform:uppercase;letter-spacing:.06em;margin-bottom:12px;border:1px solid
}}
.dnm{{font-size:18px;font-weight:700;line-height:1.2;margin-bottom:5px;font-family:'JetBrains Mono',monospace}}
.dmt{{font-size:11px;color:var(--text-dim);margin-bottom:14px}}
.ds{{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--text-muted);margin-bottom:8px;font-weight:600}}
.dcc{{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:14px}}
.cb{{
  padding:3px 9px;border-radius:6px;font-size:11px;font-family:'JetBrains Mono',monospace;
  cursor:pointer;border:1px solid var(--border);color:var(--text-dim);
  background:var(--surface2);transition:color .15s,border-color .15s
}}
.cb:hover{{color:var(--text);border-color:rgba(120,140,255,0.4)}}
.zc{{position:absolute;bottom:18px;right:18px;display:flex;flex-direction:column;gap:4px}}
.zb{{
  width:30px;height:30px;background:var(--surface);border:1px solid var(--border);
  border-radius:7px;color:var(--text-dim);font-size:15px;
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;transition:color .15s,background .15s;user-select:none
}}
.zb:hover{{color:var(--text);background:var(--surface2)}}
.ins{{
  position:absolute;bottom:14px;left:50%;transform:translateX(-50%);
  font-size:11px;color:var(--text-muted);background:rgba(10,13,20,.85);
  padding:4px 12px;border-radius:20px;border:1px solid var(--border);
  pointer-events:none;white-space:nowrap
}}
.link{{stroke:rgba(120,140,255,0.18);stroke-width:1;fill:none;transition:stroke .2s}}
.link.hl{{stroke:rgba(255,255,255,0.55);stroke-width:1.5}}
.node circle{{stroke-width:1.5;transition:r .2s,opacity .2s;cursor:pointer}}
.node text{{font-family:'JetBrains Mono',monospace;font-size:9px;fill:var(--text-dim);text-anchor:middle;pointer-events:none}}
.node.hl circle{{filter:drop-shadow(0 0 5px currentColor)}}
.node.hl text{{fill:var(--text)}}
.node.dim circle{{opacity:.12}}
.node.dim text{{opacity:.12}}
</style>
</head>
<body>
<header>
  <h1>Agent<span>-Skills</span> Graph</h1>
  <div class="sw"><span class="si">⌕</span><input id="search" type="text" placeholder="search skills…" autocomplete="off" spellcheck="false"></div>
  <div class="stats">
    <span><b>{node_count}</b> skills</span>
    <span><b>{edge_count}</b> links</span>
    <span><b>7</b> clusters</span>
  </div>
</header>
<aside>
  <div class="stitle">Clusters</div>
  <div id="tl"></div>
  <div class="sep"></div>
  <div class="slb" id="slb">All Skills</div>
  <ul id="sl"></ul>
</aside>
<div id="cw">
  <svg id="svg"></svg>
  <div class="zc">
    <div class="zb" id="zi">+</div>
    <div class="zb" id="zr">⊙</div>
    <div class="zb" id="zo">−</div>
  </div>
  <div class="ins">click node · scroll to zoom · drag to pan</div>
</div>
<div id="det">
  <div id="de"><div class="di">◎</div><p>Click any skill node<br>to inspect its connections</p></div>
  <div id="dc">
    <div id="db" class="db"></div>
    <div id="dnm" class="dnm"></div>
    <div id="dmt" class="dmt"></div>
    <div class="ds">Connected Skills</div>
    <div id="dcc" class="dcc"></div>
  </div>
</div>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const GRAPH={graph_json};
const CLR={{
  "agent-ops":"#7c6af5","backend-platform":"#22d3b0",
  "content-publishing":"#f97316","frontend-ui":"#38bdf8",
  "mobile-native":"#a78bfa","product-strategy":"#f472b6",
  "security-ops":"#4ade80","unknown":"#6b7799"
}};
const TLB={{
  "agent-ops":"Agent Ops","backend-platform":"Backend & Platform",
  "content-publishing":"Content & Publishing","frontend-ui":"Frontend & UI",
  "mobile-native":"Mobile & Native","product-strategy":"Product Strategy",
  "security-ops":"Security Ops"
}};
const tc={{}};GRAPH.nodes.forEach(n=>{{tc[n.topic]=(tc[n.topic]||0)+1;}});
const tl=document.getElementById("tl");let at=null;
Object.entries(TLB).forEach(([k,l])=>{{
  const el=document.createElement("div");el.className="ti";el.dataset.t=k;
  el.innerHTML=`<div class="td" style="background:${{CLR[k]}}"></div><span class="tn">${{l}}</span><span class="tc">${{tc[k]||0}}</span>`;
  el.addEventListener("click",()=>{{
    if(at===k){{at=null;el.classList.remove("active");hlT(null);}}
    else{{document.querySelectorAll(".ti").forEach(e=>e.classList.remove("active"));at=k;el.classList.add("active");hlT(k);}}
    updL(at);
  }});
  tl.appendChild(el);
}});
const sl=document.getElementById("sl"),slb=document.getElementById("slb");
function updL(tf){{
  const ns=tf?GRAPH.nodes.filter(n=>n.topic===tf):GRAPH.nodes;
  slb.textContent=tf?(TLB[tf]||tf):"All Skills";sl.innerHTML="";
  [...ns].sort((a,b)=>a.id.localeCompare(b.id)).forEach(n=>{{
    const li=document.createElement("li");li.textContent=n.id;li.dataset.id=n.id;
    li.addEventListener("click",()=>sel(n.id));sl.appendChild(li);
  }});
}}
updL(null);
const svg=d3.select("#svg"),cw=document.getElementById("cw");
const links=GRAPH.edges.map(function(e){{return {{source:e.from,target:e.to,weight:e.weight||1,desc:e.desc||""}};}}); 
const nodes=GRAPH.nodes.map(function(n){{return Object.assign({{}},n);}});
const co=Object.keys(TLB);
function cp(t){{
  const i=co.indexOf(t),a=(i/co.length)*Math.PI*2-Math.PI/2;
  const r=Math.min(cw.clientWidth,cw.clientHeight)*0.3;
  return{{x:cw.clientWidth/2+Math.cos(a)*r,y:cw.clientHeight/2+Math.sin(a)*r}};
}}
nodes.forEach(n=>{{const p=cp(n.topic);n.x=p.x+(Math.random()-.5)*70;n.y=p.y+(Math.random()-.5)*70;}});
const zoom=d3.zoom().scaleExtent([0.08,5]).on("zoom",e=>g.attr("transform",e.transform));
svg.call(zoom);
const g=svg.append("g");
const lk=g.append("g").selectAll("line").data(links).join("line").attr("class","link")
  .attr("stroke-width",function(l){{return Math.min(3.5,0.6+l.weight*0.35);}})
  .attr("stroke-opacity",function(l){{return Math.min(0.65,0.12+l.weight*0.1);}});
const deg={{}};links.forEach(l=>{{deg[l.source]=(deg[l.source]||0)+1;deg[l.target]=(deg[l.target]||0)+1;}});
const nd=g.append("g").selectAll("g").data(nodes).join("g").attr("class","node")
  .call(d3.drag()
    .on("start",(e,d)=>{{if(!e.active)sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y;}})
    .on("drag", (e,d)=>{{d.fx=e.x;d.fy=e.y;}})
    .on("end",  (e,d)=>{{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}}))
  .on("click",(e,d)=>{{e.stopPropagation();sel(d.id);}});
nd.append("circle")
  .attr("r",d=>Math.max(5,Math.min(14,5+(deg[d.id]||0)*0.7)))
  .attr("fill",d=>CLR[d.topic]||CLR.unknown)
  .attr("fill-opacity",0.82)
  .attr("stroke",d=>CLR[d.topic]||CLR.unknown)
  .attr("stroke-opacity",d=>d.stability==="stable"?0.9:0.45)
  .attr("stroke-width",d=>d.stability==="stable"?3:1.5);
nd.append("text").attr("dy",13).text(d=>d.id);
function cf(alpha){{nodes.forEach(n=>{{const p=cp(n.topic);n.vx+=(p.x-n.x)*alpha*0.05;n.vy+=(p.y-n.y)*alpha*0.05;}});}}
const sim=d3.forceSimulation(nodes)
  .force("link",d3.forceLink(links).id(d=>d.id).distance(60).strength(0.28))
  .force("charge",d3.forceManyBody().strength(-55))
  .force("cluster",cf)
  .force("collide",d3.forceCollide(15))
  .on("tick",()=>{{
    lk.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
    nd.attr("transform",d=>`translate(${{d.x}},${{d.y}})`);
  }});
svg.on("click",()=>clrSel());
let sId=null;
function sel(id){{
  sId=id;const node=nodes.find(n=>n.id===id);if(!node)return;
  const conn=new Set();
  links.forEach(l=>{{
    const s=typeof l.source==="object"?l.source.id:l.source;
    const t=typeof l.target==="object"?l.target.id:l.target;
    if(s===id)conn.add(t);if(t===id)conn.add(s);
  }});
  nd.classed("hl",d=>d.id===id||conn.has(d.id)).classed("dim",d=>d.id!==id&&!conn.has(d.id));
  lk.classed("hl",l=>{{
    const s=typeof l.source==="object"?l.source.id:l.source;
    const t=typeof l.target==="object"?l.target.id:l.target;
    return s===id||t===id;
  }});
  document.querySelectorAll("#sl li").forEach(li=>li.classList.toggle("hl",li.dataset.id===id));
  document.getElementById("de").style.display="none";
  const dc=document.getElementById("dc");dc.classList.add("vis");
  const c=CLR[node.topic]||CLR.unknown;
  const db=document.getElementById("db");
  db.textContent=TLB[node.topic]||node.topic;db.style.cssText=`background:${{c}}20;color:${{c}};border-color:${{c}}44`;
  const stableTag=node.stability==="stable"?` <span style="font-size:10px;opacity:.7">★ stable hub</span>`:"";
  document.getElementById("dnm").innerHTML=node.id+stableTag;
  document.getElementById("dmt").textContent=`${{conn.size}} connection${{conn.size!==1?"s":""}} · ${{node.topic}}`;
  const dcc=document.getElementById("dcc");dcc.innerHTML="";
  if(conn.size===0){{dcc.innerHTML='<span style="color:var(--text-muted);font-size:12px">No cross-skill links yet</span>';}}
  else{{;
    const weightMap={{}};
    links.forEach(function(l){{
      const s=typeof l.source==="object"?l.source.id:l.source;
      const t=typeof l.target==="object"?l.target.id:l.target;
      if(s===id||t===id){{const peer=s===id?t:s;weightMap[peer]={{w:l.weight,desc:l.desc||""}};}}
    }});
    [...conn].sort().forEach(function(cid){{
      const cn=nodes.find(function(n){{return n.id===cid;}});
      const ew=weightMap[cid]||{{w:1,desc:""}};
      const btn=document.createElement("div");btn.className="cb";
      btn.title=ew.desc;
      const wBadge=ew.w>1.5?` <span style="font-size:9px;opacity:.6">${{ew.w.toFixed(1)}}×</span>`:"";
      btn.innerHTML=cid+wBadge;
      if(cn)btn.style.borderColor=CLR[cn.topic]+"44";
      btn.addEventListener("click",function(){{sel(cid);}});dcc.appendChild(btn);
    }});
  }}
}}
function clrSel(){{
  sId=null;nd.classed("hl",false).classed("dim",false);lk.classed("hl",false);
  document.getElementById("de").style.display="flex";document.getElementById("dc").classList.remove("vis");
  document.querySelectorAll("#sl li").forEach(li=>li.classList.remove("hl"));
}}
function hlT(t){{
  if(!t){{nd.classed("dim",false).classed("hl",false);lk.classed("hl",false);return;}}
  nd.classed("dim",d=>d.topic!==t).classed("hl",d=>d.topic===t);
  lk.classed("hl",l=>{{
    const s=typeof l.source==="object"?l.source.id:l.source;
    const t2=typeof l.target==="object"?l.target.id:l.target;
    const sn=nodes.find(n=>n.id===s);const tn=nodes.find(n=>n.id===t2);
    return sn?.topic===t||tn?.topic===t;
  }});
}}
document.getElementById("search").addEventListener("input",e=>{{
  const q=e.target.value.trim().toLowerCase();
  if(!q){{nd.classed("dim",false).classed("hl",false);updL(at);return;}}
  const m=new Set(nodes.filter(n=>n.id.includes(q)).map(n=>n.id));
  nd.classed("hl",d=>m.has(d.id)).classed("dim",d=>!m.has(d.id));
  slb.textContent=`Results (${{m.size}})`;sl.innerHTML="";
  [...m].sort().forEach(id=>{{
    const li=document.createElement("li");li.textContent=id;li.dataset.id=id;li.className="hl";
    li.addEventListener("click",()=>sel(id));sl.appendChild(li);
  }});
}});
document.getElementById("zi").addEventListener("click",()=>svg.transition().call(zoom.scaleBy,1.4));
document.getElementById("zo").addEventListener("click",()=>svg.transition().call(zoom.scaleBy,0.7));
document.getElementById("zr").addEventListener("click",()=>svg.transition().call(zoom.transform,d3.zoomIdentity));
setTimeout(()=>{{
  try{{const b=g.node().getBBox();const w=cw.clientWidth,h=cw.clientHeight;
  const sc=Math.min(0.8,0.8/Math.max(b.width/w,b.height/h));
  svg.transition().duration(900).call(zoom.transform,d3.zoomIdentity.translate(w/2-sc*(b.x+b.width/2),h/2-sc*(b.y+b.height/2)).scale(sc));}}
  catch(e){{}}
}},3200);
</script>
</body>
</html>"""

HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
HTML_OUT.write_text(html, encoding="utf-8")
print(f"gen-skill-graph: nodes={node_count} edges={edge_count}")
print(f"output: {HTML_OUT}")
