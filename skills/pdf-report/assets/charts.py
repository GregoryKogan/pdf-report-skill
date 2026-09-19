# -*- coding: utf-8 -*-
"""Chart geometry. The HTML around it is assembled by the report generator.

The viewBox is 420 by default, not 520: one HTML builds BOTH A4 and A5, and on A5
at 520 the small labels drop to 5.9 pt — below the readability threshold.
Label sizes are scaled up 1.26x to match the larger body text (13.5 pt)."""
import math

# ---- palette (verified with validate_palette.js) ----
N0="#2E3440"; N1="#3B4252"; N2="#434C5E"; N3="#4C566A"
N4="#D8DEE9"; N6="#ECEFF4"; MUTED="#A2ADC0"
C1="#60c4de"; C2="#d4af62"; C3="#b77bad"; C4="#9ec27e"; C5="#c9785f"
GOOD="#92b96e"; WARN="#cba553"; CRIT="#e88d94"
GRID=N2; AXIS=N3
SEQ=["#21697c","#3a8ea5","#59b2cb","#7cd3eb"]   # sequential, one hue, monotone lightness
EMPTY="#454F62"                                   # an empty cell, not a zero value
NBSP="\u00a0"

# ---- numbers ---------------------------------------------------------------
# Numbers are written the same way in every language, deliberately: a period for
# the decimal separator and no space before %, even in the languages that would
# write a comma and a space in running text. A report is read next to code,
# tables and other languages, and one notation is one ambiguity less.
def num(x, nd=None):
    """a number for a chart: integers keep no tail unless nd is given"""
    return f"{x:g}" if nd is None else f"{x:.{nd}f}"

ru = num   # former name, kept so existing generators keep working

GAP=2.0       # 2px surface gap in viewBox units (at W=420)
REND=4.5      # 4px rounding on the data end
MAXBAR=23.0   # 24px limit on mark thickness (at W=420)

def esc(s): return s.replace("&","&amp;").replace("<","&lt;")

def top_round(x,y,w,h,r=REND):
    """a rectangle with a rounded top and a flat base"""
    r=min(r,w/2,h)
    if h<=0.4: return ""
    return (f'<path d="M{x:.1f},{y+h:.1f} L{x:.1f},{y+r:.1f} Q{x:.1f},{y:.1f} {x+r:.1f},{y:.1f} '
            f'L{x+w-r:.1f},{y:.1f} Q{x+w:.1f},{y:.1f} {x+w:.1f},{y+r:.1f} L{x+w:.1f},{y+h:.1f} Z"/>')

def right_round(x,y,w,h,r=REND):
    r=min(r,w,h/2)
    if w<=0.4: return ""
    return (f'<path d="M{x:.1f},{y:.1f} L{x+w-r:.1f},{y:.1f} Q{x+w:.1f},{y:.1f} {x+w:.1f},{y+r:.1f} '
            f'L{x+w:.1f},{y+h-r:.1f} Q{x+w:.1f},{y+h:.1f} {x+w-r:.1f},{y+h:.1f} L{x:.1f},{y+h:.1f} Z"/>')

def svg(w,h,body,cls="chart"):
    return (f'<svg class="{cls}" viewBox="0 0 {w} {h}" role="img" '
            f'font-family="PT Sans, sans-serif">{body}</svg>')

# ---------------------------------------------------------------- area + line
def area_line(labels, vals, ymax, W=420, H=210, unit="", label_idx=None):
    L,R,T,B = 30,10,16,26
    pw,ph = W-L-R, H-T-B
    xs=[L+pw*(i+0.5)/len(vals) for i in range(len(vals))]
    ys=[T+ph*(1-v/ymax) for v in vals]
    o=[]
    ticks=[0,ymax/4,ymax/2,ymax*3/4,ymax]
    for t in ticks:
        y=T+ph*(1-t/ymax)
        o.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{L-6}" y="{y+3.5:.1f}" fill="{MUTED}" font-size="13.2" text-anchor="end">{num(t)}</text>')
    pts=" ".join(f"{x:.1f},{y:.1f}" for x,y in zip(xs,ys))
    o.append(f'<polygon points="{xs[0]:.1f},{T+ph} {pts} {xs[-1]:.1f},{T+ph}" fill="{C1}" fill-opacity="0.10"/>')
    o.append(f'<polyline points="{pts}" fill="none" stroke="{C1}" stroke-width="2" '
             f'stroke-linejoin="round" stroke-linecap="round"/>')
    for i,(x,y) in enumerate(zip(xs,ys)):
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{C1}" stroke="{N1}" stroke-width="2"/>')
    for i in (label_idx or []):
        o.append(f'<text x="{xs[i]:.1f}" y="{ys[i]-11:.1f}" fill="{N6}" font-size="13.9" '
                 f'font-weight="700" text-anchor="middle">{num(vals[i])}{unit}</text>')
    for i,lb in enumerate(labels):
        o.append(f'<text x="{xs[i]:.1f}" y="{H-8}" fill="{MUTED}" font-size="13.2" text-anchor="middle">{lb}</text>')
    o.append(f'<line x1="{L}" y1="{T+ph}" x2="{W-R}" y2="{T+ph}" stroke="{AXIS}" stroke-width="1"/>')
    return svg(W,H,"".join(o))

# ---------------------------------------------------------------- stacked columns
def stacked_cols(labels, series, colors, ymax, W=420, H=225):
    L,R,T,B = 30,10,14,26
    pw,ph = W-L-R, H-T-B
    n=len(labels); slot=pw/n; bw=min(MAXBAR, slot*0.62)
    o=[]
    for t in range(0,int(ymax)+1,int(ymax//4)):
        y=T+ph*(1-t/ymax)
        o.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{L-6}" y="{y+3.5:.1f}" fill="{MUTED}" font-size="13.2" text-anchor="end">{t}</text>')
    for i in range(n):
        x=L+slot*i+(slot-bw)/2; acc=0.0
        segs=[s[i] for s in series]
        tot=sum(segs)
        for k,v in enumerate(segs):
            if v<=0: continue
            hgt=ph*v/ymax
            ytop=T+ph-(acc+v)/ymax*ph
            hh=hgt-(GAP if acc>0 else 0)
            yy=ytop
            top=(k==len(segs)-1) or all(s==0 for s in segs[k+1:])
            shape = top_round(x,yy,bw,hh) if top else f'<rect x="{x:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="{max(hh,0):.1f}"/>'
            o.append(f'<g fill="{colors[k]}">{shape}</g>')
            acc+=v
        if tot>0:
            o.append(f'<text x="{x+bw/2:.1f}" y="{T+ph-tot/ymax*ph-8:.1f}" fill="{N4}" '
                     f'font-size="12.6" text-anchor="middle">{int(tot)}</text>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{H-8}" fill="{MUTED}" font-size="13.2" text-anchor="middle">{labels[i]}</text>')
    o.append(f'<line x1="{L}" y1="{T+ph}" x2="{W-R}" y2="{T+ph}" stroke="{AXIS}" stroke-width="1"/>')
    return svg(W,H,"".join(o))

# ---------------------------------------------------------------- calendar heatmap
def heatmap(rows, months, W=420):
    LW=34; cell=(W-LW)/31.0; ch=13.5
    H=len(rows)*ch+20
    o=[]
    for r,(m,days) in enumerate(zip(months,rows)):
        y=r*ch
        o.append(f'<text x="0" y="{y+ch/2+3.5:.1f}" fill="{MUTED}" font-size="12.6">{m}</text>')
        for d,v in enumerate(days):
            if v is None: continue          # no cell at all: outside the month, or no data by design
            x=LW+d*cell
            fill = EMPTY if v==0 else SEQ[min(v,4)-1]
            o.append(f'<rect x="{x+GAP/2:.2f}" y="{y+GAP/2:.2f}" width="{cell-GAP:.2f}" '
                     f'height="{ch-GAP:.2f}" rx="1.5" fill="{fill}"/>')
    for d in (0,9,19,30):
        o.append(f'<text x="{LW+d*cell+cell/2:.1f}" y="{len(rows)*ch+12:.1f}" fill="{MUTED}" '
                 f'font-size="12" text-anchor="middle">{d+1}</text>')
    return svg(W,H,"".join(o))

# ---------------------------------------------------------------- polar rose
def polar(vals, W=420, H=300):
    cx,cy=W/2,H/2-4; rmax=118; rmin=26
    mx=max(vals); o=[]
    for frac in (0.25,0.5,0.75,1.0):
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{rmin+(rmax-rmin)*frac:.1f}" fill="none" '
                 f'stroke="{GRID}" stroke-width="1"/>')
    for i,v in enumerate(vals):
        a0=math.radians(i*15-90-7.0); a1=math.radians(i*15-90+7.0)
        r=rmin+(rmax-rmin)*v/mx
        r=max(r, rmin+4.5)          # a zero hour keeps a visible stub, so the circle still reads as a dial
        x0,y0=cx+rmin*math.cos(a0), cy+rmin*math.sin(a0)
        x1,y1=cx+r*math.cos(a0),    cy+r*math.sin(a0)
        x2,y2=cx+r*math.cos(a1),    cy+r*math.sin(a1)
        x3,y3=cx+rmin*math.cos(a1), cy+rmin*math.sin(a1)
        night = (i>=18 or i<=6)
        col = C1 if night else N3
        op  = '1' if night else '0.75'
        o.append(f'<path d="M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f} A{r:.1f},{r:.1f} 0 0 1 {x2:.1f},{y2:.1f} '
                 f'L{x3:.1f},{y3:.1f} A{rmin},{rmin} 0 0 0 {x0:.1f},{y0:.1f} Z" fill="{col}" fill-opacity="{op}"/>')
    for hh in range(0,24,3):
        a=math.radians(hh*15-90); rr=rmax+16
        o.append(f'<text x="{cx+rr*math.cos(a):.1f}" y="{cy+rr*math.sin(a)+3.5:.1f}" fill="{MUTED}" '
                 f'font-size="13.2" text-anchor="middle">{hh:02d}</text>')
    peak=vals.index(max(vals))
    ap=math.radians(peak*15-90); rr=rmin+(rmax-rmin)*max(vals)/mx+13
    o.append(f'<text x="{cx+rr*math.cos(ap):.1f}" y="{cy+rr*math.sin(ap)+4:.1f}" fill="{N6}" '
             f'font-size="15.1" font-weight="700" text-anchor="middle">{max(vals)}</text>')
    o.append(f'<text x="{cx}" y="{cy+1}" fill="{N4}" font-size="12.6" text-anchor="middle">peak</text>')
    o.append(f'<text x="{cx}" y="{cy+13}" fill="{N6}" font-size="14.5" font-weight="700" text-anchor="middle">{peak:02d}:00</text>')
    return svg(W,H,"".join(o))

# ---------------------------------------------------------------- 100% bar
def share_bar(items, colors, W=420, H=32):
    """100% part-to-whole bar; share labels go inside a segment only if they fit"""
    bh=30; tot=sum(v for _,v in items); x=0.0; o=[]; segs=[]
    for i,((lab,v),c) in enumerate(zip(items,colors)):
        w=W*v/tot - (GAP if i<len(items)-1 else 0)
        rx = 3 if (i==0 or i==len(items)-1) else 1.5
        o.append(f'<rect x="{x:.1f}" y="0" width="{max(w,0):.1f}" height="{bh}" fill="{c}" rx="{rx}"/>')
        segs.append((x,w,100*v/tot))
        x+=w+GAP
    for (sx,sw,pct) in segs:
        if sw>46:   # label inside only when it fits with margins
            o.append(f'<text x="{sx+sw/2:.1f}" y="{bh/2+4:.1f}" fill="{N0}" font-size="14.5" '
                     f'font-weight="700" text-anchor="middle">{num(pct, 0)}%</text>')
    return svg(W,H,"".join(o))

# ---------------------------------------------------------------- sparkline
def spark(vals, W=86, H=22, col=C1, dim="#6B7688"):
    mn,mx=min(vals),max(vals); rng=(mx-mn) or 1
    xs=[W*i/(len(vals)-1) for i in range(len(vals))]
    ys=[H-2-(H-6)*(v-mn)/rng for v in vals]
    pts=" ".join(f"{x:.1f},{y:.1f}" for x,y in zip(xs,ys))
    return (f'<svg class="spark" viewBox="0 0 {W} {H}">'
            f'<polyline points="{pts}" fill="none" stroke="{dim}" stroke-width="1.6" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
            f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="2.8" fill="{col}"/></svg>')

# ---------------------------------------------------------------- scatter
def scatter(groups, colors, W=420, H=250, xlab="", ylab=""):
    L,R,T,B=34,10,14,30
    pw,ph=W-L-R,H-T-B
    allx=[p[0] for g in groups for p in g[1]]; ally=[p[1] for g in groups for p in g[1]]
    x0,x1=min(allx)-2,max(allx)+2; y0,y1=0,10
    o=[]
    for t in range(0,11,2):
        y=T+ph*(1-(t-y0)/(y1-y0))
        o.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{L-6}" y="{y+3.5:.1f}" fill="{MUTED}" font-size="13.2" text-anchor="end">{t}</text>')
    for t in range(int(x0//10*10), int(x1)+1, 10):
        if t<x0: continue
        x=L+pw*(t-x0)/(x1-x0)
        o.append(f'<text x="{x:.1f}" y="{H-14}" fill="{MUTED}" font-size="13.2" text-anchor="middle">{t}</text>')
    for (name,pts),c in zip(groups,colors):
        for px,py in pts:
            x=L+pw*(px-x0)/(x1-x0); y=T+ph*(1-(py-y0)/(y1-y0))
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="{c}" stroke="{N1}" stroke-width="2"/>')
    o.append(f'<line x1="{L}" y1="{T+ph}" x2="{W-R}" y2="{T+ph}" stroke="{AXIS}" stroke-width="1"/>')
    o.append(f'<text x="{W-R}" y="{H-1}" fill="{MUTED}" font-size="12.6" text-anchor="end">{esc(xlab)}</text>')
    return svg(W,H,"".join(o))

# ---------------------------------------------------------------- multi-line on a continuous axis
def multi_line(xs, series, colors, W=420, H=230, ymax=None, xlabel="", ylabel="",
               end_labels=True, xticks=None):
    """series: [(name, [values]), …] over the shared numeric axis xs (RPS, time, dose…).
    At most 4 series: beyond that the end labels collide — split into small multiples.
    Draw the legend in HTML (.legend); only end labels belong here."""
    assert len(series) <= 4, "more than 4 series: use small multiples, not one axis"
    L,R,T,B = 34,44,16,36   # B has slack: ticks and the axis label sit on separate lines
    pw,ph = W-L-R, H-T-B
    x0,x1 = min(xs), max(xs)
    ymax = ymax or max(v for _,vals in series for v in vals)*1.15
    px = lambda x: L+pw*(x-x0)/(x1-x0 or 1)
    py = lambda v: T+ph*(1-v/ymax)
    o=[]
    for k in range(5):
        t=ymax*k/4; y=py(t)
        o.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{L-6}" y="{y+3.5:.1f}" fill="{MUTED}" font-size="13.2" text-anchor="end">{num(round(t))}</text>')
    for (name,vals),c in zip(series,colors):
        pts=" ".join(f"{px(x):.1f},{py(v):.1f}" for x,v in zip(xs,vals))
        o.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2" '
                 f'stroke-linejoin="round" stroke-linecap="round"/>')
        for x,v in zip(xs,vals):
            o.append(f'<circle cx="{px(x):.1f}" cy="{py(v):.1f}" r="4" fill="{c}" '
                     f'stroke="{N1}" stroke-width="2"/>')
        if end_labels:
            o.append(f'<text x="{px(xs[-1])+9:.1f}" y="{py(vals[-1])+3.5:.1f}" fill="{N4}" '
                     f'font-size="12.6" font-weight="700">{num(vals[-1])}</text>')
    for x in (xticks or xs):
        o.append(f'<text x="{px(x):.1f}" y="{H-20}" fill="{MUTED}" font-size="13.2" '
                 f'text-anchor="middle">{num(x)}</text>')
    o.append(f'<line x1="{L}" y1="{T+ph}" x2="{W-R}" y2="{T+ph}" stroke="{AXIS}" stroke-width="1"/>')
    if xlabel:
        o.append(f'<text x="{W-R}" y="{H-4}" fill="{MUTED}" font-size="12" text-anchor="end">{esc(xlabel)}</text>')
    return svg(W,H,"".join(o))

# ---------------------------------------------------------------- vertical threshold line
def threshold(x_frac, label, W=420, H=230, color=None):
    """A hairline from the axis to the top plus a label. x_frac is a share of the plot
    width (0..1). Insert into the same svg stream AFTER the grid and BEFORE the
    marks, so the marks sit on top."""
    color = color or MUTED
    L,R,T,B = 34,44,16,36
    x = L+(W-L-R)*x_frac
    return (f'<line x1="{x:.1f}" y1="{T}" x2="{x:.1f}" y2="{H-B}" stroke="{color}" stroke-width="1"/>'
            f'<text x="{x-6:.1f}" y="{T+10}" fill="{color}" font-size="12" text-anchor="end">{esc(label)}</text>')

# ---------------------------------------------------------------- treemap
CAT=[C1,C2,C3,C4,C5]          # fixed order, never cycled: a 6th group folds into "other"

def mix(a,b,t):
    """a and b are hex; t=0 -> a, t=1 -> b"""
    f=lambda h:(int(h[1:3],16),int(h[3:5],16),int(h[5:7],16))
    x,y=f(a),f(b)
    return "#%02x%02x%02x"%tuple(round(x[i]+(y[i]-x[i])*t) for i in range(3))

def _squarify(items,x,y,w,h):
    """Classic squarify: [(key, weight)] descending -> [(key, x, y, w, h)]"""
    items=[(k,v) for k,v in items if v>0]
    tot=sum(v for _,v in items)
    if tot<=0 or w<=0 or h<=0: return []
    vals=[[k,v*w*h/tot] for k,v in items]
    def worst(row,ln):
        s=sum(r[1] for r in row)
        if s<=0: return float("inf")
        mx=max(r[1] for r in row); mn=min(r[1] for r in row)
        return max(ln*ln*mx/(s*s), s*s/(ln*ln*mn))
    out=[]
    while vals:
        ln=min(w,h)
        if ln<=0: break
        row=[vals.pop(0)]
        while vals and worst(row,ln)>=worst(row+[vals[0]],ln): row.append(vals.pop(0))
        s=sum(r[1] for r in row)
        if w>=h:
            rw=s/h if h else 0; yy=y
            for k,a in row:
                rh=a/rw if rw else 0; out.append((k,x,yy,rw,rh)); yy+=rh
            x+=rw; w-=rw
        else:
            rh=s/w if w else 0; xx=x
            for k,a in row:
                rw=a/rh if rh else 0; out.append((k,xx,y,rw,rh)); xx+=rw
            y+=rh; h-=rh
    return out

def treemap(groups, W=420, H=300, unit="", head=17, pad=2.0):
    """Nested treemap: groups = [(name, [(label, value), …]), …].
    The top level is cut by totals; inside each cell its own children in lighter
    steps of the same hue. Labels appear only where they fit whole."""
    tops=[(g,sum(v for _,v in kids)) for g,kids in groups]
    cells=_squarify(tops,0,0,W,H)
    kid_of=dict(groups); o=[]
    for i,(name,x,y,w,h) in enumerate(cells):
        col=CAT[i] if i<len(CAT) else MUTED
        x+=pad/2; y+=pad/2; w=max(w-pad,0); h=max(h-pad,0)
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                 f'rx="3" fill="{mix(col,N0,0.62)}"/>')
        kids=sorted(kid_of[name],key=lambda t:-t[1])
        inner=(x,y+head,w,h-head) if (h>head+16 and w>70) else None
        if inner and kids:
            for j,(kn,kx,ky,kw,kh) in enumerate(_squarify(kids,*inner)):
                kx+=0.8; ky+=0.8; kw=max(kw-1.6,0); kh=max(kh-1.6,0)
                o.append(f'<rect x="{kx:.1f}" y="{ky:.1f}" width="{kw:.1f}" height="{kh:.1f}" '
                         f'rx="2" fill="{mix(col,N0,0.10+0.14*min(j,4))}"/>')
                if kw>46 and kh>17:
                    o.append(f'<text x="{kx+5:.1f}" y="{ky+13:.1f}" fill="{N0}" font-size="11.6" '
                             f'font-weight="600">{esc(clip(kn,kw-9,11.6))}</text>')
        ttl=f"{esc(name)}"
        if w>54 and h>15:
            o.append(f'<text x="{x+5:.1f}" y="{y+12.6:.1f}" fill="{N6}" font-size="13.2" '
                     f'font-weight="700">{esc(clip(name,w-9))}</text>')
    return svg(W,H,"".join(o))

# ---------------------------------------------------------------- horizontal bars
def clip(s,px,fs=13.2):
    """clip a label to px width with an ellipsis, never mid-word in silence"""
    n=max(int(px/(fs*0.47)),3)
    return s if len(s)<=n else s[:n-1]+"\u2026"

def hbars(items, W=420, unit="", lw=150, rowh=None, color=None, colors=None, nd=1):
    """items=[(label, value)] descending; the value is printed at the data end.
    lw — width of the label column, nd — decimals in the printed value."""
    n=len(items); rowh=rowh or 26
    fmt=lambda v: num(v, nd)
    res=6+max(len(fmt(v)) for _,v in items)*6.6+(len(unit)+1)*6.6
    H=n*rowh+6; bw=W-lw-res
    mx=max(v for _,v in items) or 1
    bh=min(MAXBAR,rowh-8); o=[]
    for i,(lab,v) in enumerate(items):
        y=6+i*rowh; c=(colors[i] if colors else (color or C1))
        w=bw*v/mx
        o.append(f'<text x="0" y="{y+bh/2+4.6:.1f}" fill="{N4}" font-size="13.2">'
                 f'{esc(clip(lab,lw-6))}</text>')
        o.append(f'<g fill="{c}">{right_round(lw,y,max(w,3),bh)}</g>')
        o.append(f'<text x="{lw+max(w,3)+6:.1f}" y="{y+bh/2+4.6:.1f}" fill="{MUTED}" '
                 f'font-size="13.2">{fmt(v)}{NBSP}{unit}</text>')
    return svg(W,H,"".join(o))
