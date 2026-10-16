"""Regenerate paper-aligned vector diagrams from the exact seed arc lists."""
from pathlib import Path
import html,json
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'figures/seed_arc_lists.json').read_text())
OUT=ROOT/'docs/assets/witness-pairs.svg'
# Same vertex layout across every witness; alpha=solid, beta=dashed.
pos={0:(70,45),1:(70,145),2:(200,45),3:(200,145),4:(330,35),5:(330,100),6:(330,165)}
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="460" viewBox="0 0 1000 460" role="img" aria-labelledby="title desc">','<title id="title">Two exact seven-vertex operation-labelled DAG witness pairs</title>','<desc id="desc">Four DAGs in two pairs. Solid arcs denote alpha and dashed arcs beta. Each panel is generated from the archive seed arc lists.</desc>','<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 Z" fill="#1f2937"/></marker></defs>','<rect width="1000" height="460" fill="white"/>']
for row,pair in enumerate(('first_pair','second_pair')):
 for col,side in enumerate(('A','B')):
  tx=col*500+38; ty=row*210+20
  parts.append(f'<g transform="translate({tx},{ty})">')
  parts.append(f'<text x="0" y="0" font-size="16" font-weight="bold" font-family="sans-serif" fill="#171717">Family {row+1} · {side}</text>')
  d=DATA[pair][side];alpha={tuple(e) for e in d['alpha']}
  for u,v in d['arcs']:
   x1,y1=pos[u];x2,y2=pos[v];x1+=12;x2-=12;dy=y2-y1;dx=x2-x1; l=(dx*dx+dy*dy)**0.5;x1+=dx/l*2;y1+=dy/l*2;x2-=dx/l*2;y2-=dy/l*2
   style='' if (u,v) in alpha else ' stroke-dasharray="6 5"'
   parts.append(f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" fill="none" stroke="#1f2937" stroke-width="1.8"{style} marker-end="url(#arrow)"/>')
  for v,(x,y) in pos.items():
   parts.append(f'<circle cx="{x}" cy="{y}" r="12" stroke="#111827" stroke-width="1.5" fill="white"/>')
   parts.append(f'<text x="{x}" y="{y+4}" text-anchor="middle" font-size="12" fill="#111827" font-family="sans-serif">{v}</text>')
  parts.append('</g>')
parts.append('<g transform="translate(400,447)" font-family="sans-serif" font-size="13" fill="#1f2937"><path d="M0 0 h40" stroke="#1f2937" stroke-width="2"/><text x="46" y="4">α</text><path d="M90 0 h40" stroke="#1f2937" stroke-width="2" stroke-dasharray="6 5"/><text x="136" y="4">β</text></g></svg>')
OUT.write_text('\n'.join(parts),encoding='utf8')
print('saved',OUT)
