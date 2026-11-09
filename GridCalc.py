"""GridCalc 3.0 - Power System Engineering Toolkit
Run:  pip install streamlit plotly numpy   ->   streamlit run gridcalc_app.py
"""
import math
import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="GridCalc | Power System Engineering", page_icon="⚡", layout="wide")

# ---------------------------------------------------------------- styling
st.markdown("""
<style>
.block-container{padding-top:1.2rem;max-width:1450px}
.hero{padding:1.6rem 1.8rem;border-radius:20px;color:#fff;margin-bottom:1.1rem;
 background:linear-gradient(120deg,#0b2545 0%,#13518f 55%,#1d8fd1 100%);
 box-shadow:0 8px 24px rgba(19,81,143,.25)}
.hero h1{font-size:2rem;margin:0;color:#fff}.hero p{margin:.4rem 0 0;color:#d6e8fa}
.formula{background:rgba(23,105,170,.08);border-left:4px solid #1769aa;padding:.7rem 1rem;
 border-radius:8px;margin:.4rem 0 1rem}
div[data-testid="stMetric"]{border:1px solid rgba(120,140,170,.35);padding:.8rem;border-radius:14px;
 background:linear-gradient(180deg,rgba(23,105,170,.07),rgba(23,105,170,0))}
.small{font-size:.8rem;opacity:.65}
</style>""", unsafe_allow_html=True)

# ---------------------------------------------------------------- units & helpers
UNITS = {
    "Power": {"W": 1, "kW": 1e3, "MW": 1e6, "GW": 1e9},
    "Apparent power": {"VA": 1, "kVA": 1e3, "MVA": 1e6},
    "Reactive power": {"var": 1, "kVAr": 1e3, "MVAr": 1e6},
    "Energy": {"Wh": 1, "kWh": 1e3, "MWh": 1e6, "GWh": 1e9},
    "Voltage": {"V": 1, "kV": 1e3},
    "Current": {"A": 1, "kA": 1e3},
    "Resistance": {"Ω": 1, "mΩ": 1e-3, "kΩ": 1e3},
    "Frequency": {"Hz": 1, "kHz": 1e3},
    "Time": {"s": 1, "min": 60, "h": 3600},
    "Length": {"m": 1, "km": 1e3},
    "Capacitance": {"F": 1, "µF": 1e-6, "mF": 1e-3},
}
SQ3 = math.sqrt(3)
PAL = ["#1769aa", "#e4572e", "#2a9d8f", "#f4a261", "#6a4c93"]


def convert(v, g, a, b):
    return v * UNITS[g][a] / UNITS[g][b]


def qty(label, value, group, units, base, key, minv=0.0):
    """Number input + unit selector (default = first unit); returns value in `base` unit."""
    c1, c2 = st.columns([2, 1])
    v = c1.number_input(label, min_value=minv, value=float(value), key=key + "v", format="%g")
    u = c2.selectbox("Unit", units, key=key + "u")
    return convert(v, group, u, base)


def out_unit(label, group, opts, default, key):
    return st.selectbox(label, opts, index=opts.index(default), key=key)


def kpi(col, label, val, unit, fmt=".3f"):
    col.metric(label, f"{format(val, fmt)} {unit}".strip())


def formula(txt):
    st.markdown(f'<div class="formula"><b>Formula</b><br>{txt}</div>', unsafe_allow_html=True)


def style(fig, title, xt="", yt="", h=380):
    fig.update_layout(title=title, template="plotly_white", height=h, xaxis_title=xt, yaxis_title=yt,
                      margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", y=-0.2),
                      font=dict(family="Inter, sans-serif"))
    return fig


def glossary(items):
    with st.expander("Symbols and abbreviations"):
        st.table([{"Symbol": a, "Meaning": b} for a, b in items])


def power_triangle(p, q, pu, qu):
    s = math.hypot(p, q)
    f = go.Figure()
    f.add_trace(go.Scatter(x=[0, p, p, 0], y=[0, 0, q, 0], fill="toself", mode="lines+markers",
                           line=dict(color=PAL[0], width=3), fillcolor="rgba(23,105,170,.12)", name="Triangle"))
    f.add_annotation(x=p / 2, y=0, text=f"P = {p:.3g} {pu}", yshift=-18, showarrow=False)
    f.add_annotation(x=p, y=q / 2, text=f"Q = {q:.3g} {qu}", xshift=55, showarrow=False)
    f.add_annotation(x=p / 2, y=q / 2, text=f"S = {s:.3g}", yshift=14, showarrow=False, font=dict(color=PAL[1]))
    return style(f, "Power triangle", f"Active power ({pu})", f"Reactive power ({qu})")


def gauge(value, title, warn=80, crit=100):
    f = go.Figure(go.Indicator(mode="gauge+number", value=value, number={"suffix": " %"},
        title={"text": title}, gauge={"axis": {"range": [0, max(120, value * 1.1)]},
        "bar": {"color": PAL[0]}, "steps": [{"range": [0, warn], "color": "#d8f3dc"},
        {"range": [warn, crit], "color": "#ffe8b0"}, {"range": [crit, max(120, value * 1.1)], "color": "#ffc9c4"}],
        "threshold": {"line": {"color": "red", "width": 4}, "value": crit}}))
    f.update_layout(height=320, margin=dict(l=20, r=20, t=60, b=10))
    return f


def go_to(p):
    st.session_state.page = p


# ---------------------------------------------------------------- navigation
PAGES = ["Dashboard", "Three-phase power", "Power factor correction", "Transformer", "Transmission line",
         "Per-unit system", "Short-circuit basics", "BESS sizing", "Renewable integration",
         "Unit converter", "Formula & abbreviation guide"]
ICON = dict(zip(PAGES, ["🏠", "🔌", "📈", "🧲", "🗼", "📐", "💥", "🔋", "☀️", "🔁", "📘"]))

with st.sidebar:
    st.markdown("## ⚡ GridCalc")
    st.caption("POWER SYSTEM TOOLKIT • v3.0")
    page = st.radio("Workspace", PAGES, key="page", format_func=lambda x: f"{ICON[x]}  {x}")
    st.divider()
    st.caption("Enter values in the unit shown next to each field; results update live.")

st.markdown(f"""<div class="hero"><h1>{ICON[page]} {'GridCalc — Power System Engineering' if page == 'Dashboard' else page}</h1>
<p>Interactive calculations • Live charts • Editable engineering units • Formula reference</p></div>""",
            unsafe_allow_html=True)

# ================================================================ DASHBOARD
if page == "Dashboard":
    cards = [("Three-phase power", "P, Q, S, current, phasors"), ("Power factor correction", "Capacitor bank sizing"),
             ("Transformer", "Current, loading gauge, losses"), ("Transmission line", "Voltage drop profile & losses"),
             ("Per-unit system", "Base impedance & conversion"), ("Short-circuit basics", "Fault current & level"),
             ("BESS sizing", "Peak shaving & energy"), ("Renewable integration", "DC/AC ratio, clipping, CF")]
    cols = st.columns(4)
    for i, (t, d) in enumerate(cards):
        with cols[i % 4].container(border=True):
            st.markdown(f"### {ICON[t]}")
            st.markdown(f"**{t}**")
            st.caption(d)
            st.button("Open →", key=f"o{i}", on_click=go_to, args=(t,), use_container_width=True)

    st.markdown("### Sample feeder snapshot")
    st.caption("Illustrative 24 h feeder with a PV plant and a BESS peak-shaving target.")
    h = np.arange(0, 24, .25)
    load = 6 + 2.2 * np.exp(-((h - 8) / 2) ** 2) + 4.2 * np.exp(-((h - 19.5) / 2.2) ** 2)
    pv = 5 * np.clip(np.sin(np.pi * (h - 6) / 12), 0, None) ** 1.3
    net = load - pv
    tgt = 8.0
    f = go.Figure()
    f.add_trace(go.Scatter(x=h, y=load, name="Load", line=dict(color=PAL[1], width=3)))
    f.add_trace(go.Scatter(x=h, y=pv, name="PV", fill="tozeroy", line=dict(color=PAL[3]), fillcolor="rgba(244,162,97,.3)"))
    f.add_trace(go.Scatter(x=h, y=net, name="Net grid import", line=dict(color=PAL[0], width=3)))
    f.add_hline(y=tgt, line_dash="dash", line_color="green", annotation_text="BESS target")
    st.plotly_chart(style(f, "Daily profile (MW)", "Hour of day", "MW", 400), use_container_width=True)
    a, b, c, d = st.columns(4)
    kpi(a, "Peak load", load.max(), "MW", ".2f"); kpi(b, "Peak PV", pv.max(), "MW", ".2f")
    kpi(c, "Peak net import", net.max(), "MW", ".2f")
    kpi(d, "Energy above target", np.clip(net - tgt, 0, None).sum() * .25, "MWh", ".2f")
    st.info("**Conventions:** 3-phase equations use line-to-line voltage and line current. Positive Q = inductive/lagging. "
            "BESS and short-circuit tools are preliminary estimates, not full studies.")

# ================================================================ THREE-PHASE
elif page == "Three-phase power":
    t1, t2, t3 = st.tabs(["P, Q, S from V, I, PF", "S & PF from P and Q", "Current from S"])
    with t1:
        L, R = st.columns([1, 1.6])
        with L:
            V = qty("Line voltage VLL", 11.0, "Voltage", ["kV", "V"], "V", "tp1v", 1e-6)
            I = qty("Line current I", 250.0, "Current", ["A", "kA"], "A", "tp1i")
            pf = st.slider("Power factor", 0.05, 1.0, 0.90, .01)
            lag = st.radio("Nature", ["Lagging (inductive)", "Leading (capacitive)"], horizontal=True)
            o1, o2, o3 = st.columns(3)
            with o1: pu = out_unit("P unit", "Power", ["MW", "kW", "W", "GW"], "MW", "tp_pu")
            with o2: qu = out_unit("Q unit", "Reactive power", ["MVAr", "kVAr", "var"], "MVAr", "tp_qu")
            with o3: su = out_unit("S unit", "Apparent power", ["MVA", "kVA", "VA"], "MVA", "tp_su")
        S = SQ3 * V * I
        P = S * pf
        Q = S * math.sqrt(max(0, 1 - pf ** 2)) * (1 if lag.startswith("Lag") else -1)
        with R:
            formula("S = √3·VLL·I &nbsp;|&nbsp; P = S·PF &nbsp;|&nbsp; Q = S·√(1 − PF²)")
            a, b, c = st.columns(3)
            Pc, Qc_, Sc = convert(P, "Power", "W", pu), convert(Q, "Reactive power", "var", qu), convert(S, "Apparent power", "VA", su)
            kpi(a, "Active P", Pc, pu); kpi(b, "Reactive Q", Qc_, qu); kpi(c, "Apparent S", Sc, su)
            g1, g2 = st.columns(2)
            g1.plotly_chart(power_triangle(Pc, Qc_, pu, qu), use_container_width=True)
            phi = math.acos(pf) * (-1 if lag.startswith("Lag") else 1)
            f = go.Figure()
            f.add_trace(go.Scatter(x=[0, 1], y=[0, 0], mode="lines+text", text=["", "V"], textposition="top center",
                                   line=dict(color=PAL[0], width=4), name="V"))
            f.add_trace(go.Scatter(x=[0, .8 * math.cos(phi)], y=[0, .8 * math.sin(phi)], mode="lines+text",
                                   text=["", "I"], textposition="top center", line=dict(color=PAL[1], width=4), name="I"))
            f.update_yaxes(scaleanchor="x")
            g2.plotly_chart(style(f, f"Phasors (φ = {abs(math.degrees(phi)):.1f}°)"), use_container_width=True)
    with t2:
        c1, c2 = st.columns(2)
        with c1:
            p = qty("Active power P", 5.0, "Power", ["MW", "kW", "W"], "W", "tp2p")
            q = qty("Reactive power Q (+ind, − cap)", 3.0, "Reactive power", ["MVAr", "kVAr", "var"], "var", "tp2q", -1e12)
            su = out_unit("S unit", "Apparent power", ["MVA", "kVA", "VA"], "MVA", "tp2s")
        s = math.hypot(p, q)
        formula("S = √(P² + Q²) &nbsp;|&nbsp; PF = P/S &nbsp;|&nbsp; φ = atan2(Q, P)")
        with c2:
            a, b, c = st.columns(3)
            kpi(a, "S", convert(s, "Apparent power", "VA", su), su)
            kpi(b, "PF", p / s if s else 0, "", ".4f"); kpi(c, "φ", math.degrees(math.atan2(q, p)), "°", ".2f")
            st.write("Nature:", "Lagging / inductive" if q > 0 else "Leading / capacitive" if q < 0 else "Unity")
        st.plotly_chart(power_triangle(p / 1e6, q / 1e6, "MW", "MVAr"), use_container_width=True)
    with t3:
        c1, c2 = st.columns(2)
        with c1:
            s = qty("Apparent power S", 5.0, "Apparent power", ["MVA", "kVA", "VA"], "VA", "tp3s", 1e-6)
            v = qty("Line voltage VLL", 11.0, "Voltage", ["kV", "V"], "V", "tp3v", 1e-6)
            iu = out_unit("Current unit", "Current", ["A", "kA"], "A", "tp3i")
        formula("I = S / (√3·VLL)")
        with c2:
            kpi(st, "Line current", convert(s / (SQ3 * v), "Current", "A", iu), iu, ".3f")
        vs = np.linspace(v * .5, v * 1.5, 60)
        f = go.Figure(go.Scatter(x=vs / 1e3, y=s / (SQ3 * vs), line=dict(color=PAL[0], width=3)))
        st.plotly_chart(style(f, "Current vs line voltage", "VLL (kV)", "I (A)"), use_container_width=True)
    glossary([("P", "Active power"), ("Q", "Reactive power"), ("S", "Apparent power"), ("PF", "Power factor"),
              ("VLL", "Line-to-line RMS voltage"), ("I", "Line current"), ("φ", "PF angle")])

# ================================================================ PF CORRECTION
elif page == "Power factor correction":
    L, R = st.columns([1, 1.6])
    with L:
        P = qty("Active load power", 1000.0, "Power", ["kW", "MW", "W"], "W", "pcp")
        pf1 = st.slider("Initial PF", .3, .99, .80, .01)
        pf2 = st.slider("Target PF", .31, 1.0, .95, .01)
        qu = out_unit("Capacitor unit", "Reactive power", ["kVAr", "MVAr", "var"], "kVAr", "pcu")
    formula("Qc = P × [tan(cos⁻¹ PF₁) − tan(cos⁻¹ PF₂)]")
    with R:
        if pf2 <= pf1:
            st.error("Target PF must be greater than initial PF.")
        else:
            q1, q2 = P * math.tan(math.acos(pf1)), P * math.tan(math.acos(pf2))
            qc = q1 - q2
            a, b, c = st.columns(3)
            kpi(a, "Required capacitor", convert(qc, "Reactive power", "var", qu), qu, ".2f")
            s1, s2 = P / pf1, P / pf2
            kpi(b, "kVA reduction", (s1 - s2) / 1e3, "kVA", ".1f")
            kpi(c, "Current reduction", (1 - s2 / s1) * 100, "%", ".1f")
            f = go.Figure()
            f.add_trace(go.Scatter(x=[0, P / 1e3, P / 1e3, 0], y=[0, 0, q1 / 1e3, 0], mode="lines", name=f"Before (PF {pf1})",
                                   line=dict(color=PAL[1], width=3)))
            f.add_trace(go.Scatter(x=[0, P / 1e3, P / 1e3, 0], y=[0, 0, q2 / 1e3, 0], mode="lines", name=f"After (PF {pf2})",
                                   line=dict(color=PAL[2], width=3), fill="toself", fillcolor="rgba(42,157,143,.12)"))
            st.plotly_chart(style(f, "Power triangle before / after correction", "P (kW)", "Q (kVAr)"), use_container_width=True)
    pfs = np.linspace(pf1 + .005, 1.0, 60) if pf1 < .995 else np.array([1.0])
    f = go.Figure(go.Scatter(x=pfs, y=convert(P, "Power", "W", "kW") * (math.tan(math.acos(pf1)) - np.tan(np.arccos(pfs))),
                             line=dict(color=PAL[0], width=3)))
    st.plotly_chart(style(f, "Capacitor requirement vs target PF", "Target PF", "Qc (kVAr)"), use_container_width=True)
    st.caption("Ideal steady-state kvar. Check voltage rise, harmonics, resonance, switching transients and step sizes.")
    glossary([("Qc", "Required capacitive kvar"), ("P", "Active load"), ("PF₁/PF₂", "Initial / target PF")])

# ================================================================ TRANSFORMER
elif page == "Transformer":
    t1, t2, t3 = st.tabs(["Rated current", "Loading", "Copper loss"])
    with t1:
        c1, c2 = st.columns([1, 1.4])
        with c1:
            s = qty("Rating", 5.0, "Apparent power", ["MVA", "kVA"], "VA", "tr1s", 1e-6)
            v = qty("Side voltage", 11.0, "Voltage", ["kV", "V"], "V", "tr1v", 1e-6)
            ph = st.radio("System", ["Three-phase", "Single-phase"], horizontal=True)
            iu = out_unit("Current unit", "Current", ["A", "kA"], "A", "tr1i")
        formula("3φ: I = S/(√3·VLL) &nbsp;|&nbsp; 1φ: I = S/V")
        i = s / (SQ3 * v) if ph == "Three-phase" else s / v
        with c2:
            kpi(st, "Rated current", convert(i, "Current", "A", iu), iu)
            f = go.Figure(go.Bar(x=["HV side", "LV side (0.4 kV)"], y=[i, s / (SQ3 * 400)], marker_color=[PAL[0], PAL[3]]))
            st.plotly_chart(style(f, "Rated current comparison (A) — assuming 0.4 kV LV", h=300), use_container_width=True)
    with t2:
        c1, c2 = st.columns([1, 1.4])
        with c1:
            rt = qty("Rated capacity", 5.0, "Apparent power", ["MVA", "kVA"], "VA", "tr2r", 1e-6)
            ld = qty("Measured load", 4.2, "Apparent power", ["MVA", "kVA"], "VA", "tr2l")
            warn = st.slider("Planning threshold (%)", 50, 100, 80)
        pct = ld / rt * 100
        formula("Loading (%) = Measured load / Rated capacity × 100")
        c2.plotly_chart(gauge(pct, "Transformer loading", warn), use_container_width=True)
        if pct > 100: c2.error("Above nameplate rating.")
        elif pct > warn: c2.warning("Above planning threshold.")
        else: c2.success("Within planning threshold.")
    with t3:
        c1, c2 = st.columns([1, 1.4])
        with c1:
            i = qty("Phase current", 200.0, "Current", ["A", "kA"], "A", "tr3i")
            r = qty("Winding resistance / phase", .02, "Resistance", ["Ω", "mΩ"], "Ω", "tr3r")
            pu = out_unit("Loss unit", "Power", ["kW", "W", "MW"], "kW", "tr3p")
        formula("Pcu = 3 × I² × Rphase")
        with c2:
            kpi(st, "Copper loss", convert(3 * i * i * r, "Power", "W", pu), pu)
            x = np.linspace(0, 1.3, 60)
            f = go.Figure(go.Scatter(x=x * 100, y=convert(3 * (i * x) ** 2 * r, "Power", "W", pu), line=dict(color=PAL[1], width=3)))
            st.plotly_chart(style(f, "Copper loss vs % of entered current", "% of current", f"Loss ({pu})", 300), use_container_width=True)
    glossary([("S", "Rating"), ("VLL", "Line voltage"), ("Pcu", "Copper loss"), ("R", "Winding resistance")])

# ================================================================ LINE
elif page == "Transmission line":
    t1, t2 = st.tabs(["Voltage drop", "Line losses"])
    with t1:
        L, R = st.columns([1, 1.6])
        with L:
            ln = qty("Line length", 5.0, "Length", ["km", "m"], "km", "tlL")
            i = qty("Line current", 150.0, "Current", ["A", "kA"], "A", "tlI")
            pf = st.slider("Power factor", .3, 1.0, .9, .01)
            r = st.number_input("R (Ω/km)", 0.0, value=.20, format="%g")
            x = st.number_input("X (Ω/km)", 0.0, value=.30, format="%g")
            v = qty("Nominal VLL", 11.0, "Voltage", ["kV", "V"], "V", "tlV", 1e-6)
        formula("ΔVLL ≈ √3·I·L·(R cosφ + X sinφ) &nbsp;|&nbsp; ΔV% = ΔV / VLL × 100")
        sn = math.sqrt(1 - pf ** 2)
        d = SQ3 * i * ln * (r * pf + x * sn)
        with R:
            a, b, c = st.columns(3)
            kpi(a, "Voltage drop", d / 1e3, "kV", ".4f"); kpi(b, "Drop", d / v * 100, "%", ".3f")
            kpi(c, "Receiving-end VLL", (v - d) / 1e3, "kV", ".3f")
            dist = np.linspace(0, ln, 50)
            pct = SQ3 * i * dist * (r * pf + x * sn) / v * 100
            f = go.Figure(go.Scatter(x=dist, y=pct, fill="tozeroy", line=dict(color=PAL[0], width=3), fillcolor="rgba(23,105,170,.12)"))
            f.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="5 % reference")
            st.plotly_chart(style(f, "Voltage-drop profile along the line", "Distance (km)", "Drop (%)"), use_container_width=True)
        pfv = np.linspace(.5, 1, 40)
        f = go.Figure(go.Scatter(x=pfv, y=SQ3 * i * ln * (r * pfv + x * np.sqrt(1 - pfv ** 2)) / v * 100, line=dict(color=PAL[1], width=3)))
        st.plotly_chart(style(f, "Voltage drop vs power factor", "PF", "Drop (%)", 300), use_container_width=True)
        st.caption("Balanced steady-state approximation. Confirm conductor temperature and geometry.")
    with t2:
        c1, c2 = st.columns([1, 1.4])
        with c1:
            i = qty("Line current", 100.0, "Current", ["A", "kA"], "A", "tl2i")
            r = qty("End-to-end R / phase", .5, "Resistance", ["Ω", "mΩ"], "Ω", "tl2r")
            pu = out_unit("Loss unit", "Power", ["kW", "W", "MW"], "kW", "tl2p")
        formula("P_loss = 3 × I² × Rphase")
        with c2:
            kpi(st, "Line loss", convert(3 * i * i * r, "Power", "W", pu), pu)
            xs = np.linspace(0, max(i, 1) * 1.5, 60)
            f = go.Figure(go.Scatter(x=xs, y=convert(3 * xs ** 2 * r, "Power", "W", pu), line=dict(color=PAL[1], width=3)))
            st.plotly_chart(style(f, "Loss vs current (quadratic)", "I (A)", f"Loss ({pu})", 320), use_container_width=True)
    glossary([("R", "Resistance"), ("X", "Reactance"), ("L", "Length"), ("φ", "PF angle"), ("ΔV", "Voltage drop")])

# ================================================================ PER-UNIT
elif page == "Per-unit system":
    mode = st.selectbox("Calculation", ["Impedance pu → ohms", "Impedance ohms → pu", "Change impedance base"])
    if mode == "Change impedance base":
        c1, c2 = st.columns(2)
        zpu = c1.number_input("Old impedance (pu)", value=.10, format="%g")
        so = c1.number_input("Old MVA base", 1e-4, value=50.0); vo = c1.number_input("Old kV base", 1e-4, value=132.0)
        sn_ = c2.number_input("New MVA base", 1e-4, value=100.0); vn = c2.number_input("New kV base", 1e-4, value=132.0)
        formula("Zpu,new = Zpu,old × (Sbase,new / Sbase,old) × (Vbase,old / Vbase,new)²")
        res = zpu * (sn_ / so) * (vo / vn) ** 2
        kpi(c2, "New impedance", res, "pu", ".5f")
        f = go.Figure(go.Bar(x=["Old base", "New base"], y=[zpu, res], marker_color=[PAL[3], PAL[0]]))
        st.plotly_chart(style(f, "Per-unit impedance on both bases", yt="pu", h=300), use_container_width=True)
    else:
        c1, c2 = st.columns(2)
        to_ohm = mode.startswith("Impedance pu")
        z = c1.number_input("Impedance value", 0.0, value=.1 if to_ohm else 5.0, format="%g")
        kv = c1.number_input("Base VLL (kV)", 1e-4, value=132.0); mva = c1.number_input("Base power (MVA)", 1e-4, value=100.0)
        zb = kv ** 2 / mva
        formula("Zbase (Ω) = Vbase(kV)² / Sbase(MVA)")
        with c2:
            kpi(st, "Base impedance", zb, "Ω", ".4f")
            kpi(st, "Result", z * zb if to_ohm else z / zb, "Ω" if to_ohm else "pu", ".5f")
        kvs = np.linspace(kv * .3, kv * 1.5, 60)
        f = go.Figure(go.Scatter(x=kvs, y=kvs ** 2 / mva, line=dict(color=PAL[0], width=3)))
        st.plotly_chart(style(f, "Base impedance vs base voltage", "Vbase (kV)", "Zbase (Ω)", 320), use_container_width=True)
    glossary([("pu", "Per-unit"), ("Zbase", "Base impedance"), ("Sbase", "3φ MVA base"), ("Vbase", "Line-line kV base")])

# ================================================================ SHORT-CIRCUIT
elif page == "Short-circuit basics":
    t1, t2 = st.tabs(["Fault current from Zth", "Fault level from current"])
    with t1:
        c1, c2 = st.columns([1, 1.4])
        with c1:
            v = qty("Prefault VLL", 11.0, "Voltage", ["kV", "V"], "V", "sc1v", 1e-6)
            z = qty("|Zth| (positive-seq.)", .5, "Resistance", ["Ω", "mΩ"], "Ω", "sc1z", 1e-6)
            iu = out_unit("Fault current unit", "Current", ["kA", "A"], "kA", "sc1u")
        formula("Isc = VLL / (√3·|Zth|)")
        isc = v / (SQ3 * z)
        with c2:
            a, b = st.columns(2)
            kpi(a, "Isc", convert(isc, "Current", "A", iu), iu); kpi(b, "Fault level", SQ3 * v * isc / 1e6, "MVA", ".2f")
            zs = np.linspace(z * .3, z * 3, 60)
            f = go.Figure(go.Scatter(x=zs, y=v / (SQ3 * zs) / 1e3, line=dict(color=PAL[1], width=3)))
            f.add_trace(go.Scatter(x=[z], y=[isc / 1e3], mode="markers", marker=dict(size=12, color=PAL[0]), name="Operating point"))
            st.plotly_chart(style(f, "Fault current vs source impedance", "|Zth| (Ω)", "Isc (kA)", 320), use_container_width=True)
    with t2:
        c1, c2 = st.columns(2)
        with c1:
            v = qty("Nominal VLL", 11.0, "Voltage", ["kV", "V"], "V", "sc2v", 1e-6)
            i = qty("3φ fault current", 20.0, "Current", ["kA", "A"], "A", "sc2i")
            su = out_unit("Fault level unit", "Apparent power", ["MVA", "kVA", "VA"], "MVA", "sc2s")
        formula("Ssc = √3 × VLL × Isc")
        kpi(c2, "Short-circuit level", convert(SQ3 * v * i, "Apparent power", "VA", su), su, ".3f")
    st.warning("Simplified Thevenin calculation — not IEC 60909. Detailed studies need sequence networks, c-factor, X/R, peak current and equipment duties.")
    glossary([("Isc", "Short-circuit current"), ("Zth", "Thevenin impedance"), ("Ssc", "Fault level")])

# ================================================================ BESS
elif page == "BESS sizing":
    t1, t2, t3 = st.tabs(["Constant-power discharge", "Usable AC energy", "Peak shaving"])
    with t1:
        c1, c2 = st.columns([1, 1.4])
        with c1:
            p = qty("AC discharge power", 2.0, "Power", ["MW", "kW"], "MW", "b1p")
            t = qty("Duration", 2.0, "Time", ["h", "min"], "h", "b1t")
            eta = st.slider("Discharge efficiency", .5, 1.0, .90, .01)
            eu = out_unit("Energy unit", "Energy", ["MWh", "kWh"], "MWh", "b1e")
        formula("E_AC = P × t &nbsp;|&nbsp; E_DC ≈ E_AC / η")
        with c2:
            a, b = st.columns(2)
            kpi(a, "AC energy", convert(p * t, "Energy", "MWh", eu), eu); kpi(b, "DC energy needed", convert(p * t / eta, "Energy", "MWh", eu), eu)
            ts = np.linspace(0, t, 50)
            f = go.Figure(go.Scatter(x=ts, y=100 * (1 - ts / t) if t else ts, fill="tozeroy", line=dict(color=PAL[2], width=3)))
            st.plotly_chart(style(f, "Ideal SOC during discharge", "Time (h)", "SOC (%)", 300), use_container_width=True)
    with t2:
        c1, c2 = st.columns([1, 1.4])
        with c1:
            en = qty("Nominal energy", 10.0, "Energy", ["MWh", "kWh"], "MWh", "b2e")
            dod = st.slider("Usable DoD", .3, 1.0, .8, .01); eta = st.slider("Discharge η", .5, 1.0, .9, .01, key="b2eta")
            eu = out_unit("Output unit", "Energy", ["MWh", "kWh"], "MWh", "b2u")
        formula("E_usable,AC ≈ E_nominal × DoD × η")
        with c2:
            kpi(st, "Usable AC energy", convert(en * dod * eta, "Energy", "MWh", eu), eu)
            f = go.Figure(go.Waterfall(x=["Nominal", "DoD loss", "Efficiency loss", "Usable AC"], measure=["absolute", "relative", "relative", "total"],
                                       y=[en, -en * (1 - dod), -en * dod * (1 - eta), 0]))
            st.plotly_chart(style(f, f"Energy waterfall ({eu})", h=320), use_container_width=True)
    with t3:
        c1, c2 = st.columns([1, 1.6])
        with c1:
            peak = qty("Existing peak demand", 8.0, "Power", ["MW", "kW"], "MW", "b3p")
            tg = qty("Target grid import", 6.0, "Power", ["MW", "kW"], "MW", "b3t")
            dur = qty("Required duration", 2.0, "Time", ["h", "min"], "h", "b3d")
            eta = st.slider("Discharge η", .5, 1.0, .9, .01, key="b3eta")
        pb = max(0, peak - tg)
        formula("P_BESS = max(0, Peak − Target) &nbsp;|&nbsp; E_nom ≈ P_BESS × duration / η")
        with c2:
            a, b = st.columns(2)
            kpi(a, "BESS power", pb, "MW"); kpi(b, "Nominal energy", pb * dur / eta, "MWh")
            h = np.arange(0, 24, .25)
            ld = .55 + .25 * np.exp(-((h - 8) / 2) ** 2) + .45 * np.exp(-((h - 19) / 2) ** 2)
            ld = ld / ld.max() * peak
            f = go.Figure()
            f.add_trace(go.Scatter(x=h, y=ld, name="Load", line=dict(color=PAL[1], width=3)))
            f.add_trace(go.Scatter(x=h, y=np.minimum(ld, tg), name="After BESS", fill="tozeroy", line=dict(color=PAL[0], width=3), fillcolor="rgba(23,105,170,.15)"))
            f.add_hline(y=tg, line_dash="dash", line_color="green", annotation_text="Target")
            st.plotly_chart(style(f, "Illustrative peak-shaving profile (MW)", "Hour", "MW"), use_container_width=True)
            st.caption(f"Profile is a synthetic shape scaled to your peak; energy above target ≈ {np.clip(ld - tg, 0, None).sum() * .25:.2f} MWh.")
    st.caption("Preliminary sizing. Add SOC limits, degradation, aux loads, temperature, C-rate, inverter P–Q capability and dispatch strategy for design.")
    glossary([("BESS", "Battery energy storage system"), ("SOC", "State of charge"), ("DoD", "Depth of discharge"), ("η", "Efficiency")])

# ================================================================ RENEWABLES
elif page == "Renewable integration":
    t1, t2, t3 = st.tabs(["PV DC/AC ratio & clipping", "Capacity factor", "Inverter apparent power"])
    with t1:
        c1, c2 = st.columns([1, 1.6])
        with c1:
            dc = st.number_input("PV DC capacity (MWp)", 0.0, value=10.16)
            ac = st.number_input("Inverter / evacuation (MW)", 1e-4, value=7.0)
        ratio = dc / ac
        formula("DC/AC ratio = PV DC nameplate / AC inverter capacity")
        h = np.arange(0, 24, .25)
        pdc = dc * .85 * np.clip(np.sin(np.pi * (h - 6) / 12), 0, None) ** 1.3
        pac = np.minimum(pdc, ac)
        clip = (pdc - pac).sum() * .25; tot = pdc.sum() * .25
        with c2:
            a, b, c = st.columns(3)
            kpi(a, "DC/AC ratio", ratio, "", ".3f"); kpi(b, "Clipped energy", clip, "MWh/day", ".2f")
            kpi(c, "Clipping loss", clip / tot * 100 if tot else 0, "%", ".2f")
            f = go.Figure()
            f.add_trace(go.Scatter(x=h, y=pdc, name="DC available", line=dict(color=PAL[3], dash="dot", width=2)))
            f.add_trace(go.Scatter(x=h, y=pac, name="AC output", fill="tozeroy", line=dict(color=PAL[0], width=3), fillcolor="rgba(23,105,170,.18)"))
            f.add_hline(y=ac, line_dash="dash", line_color="red", annotation_text="AC limit")
            st.plotly_chart(style(f, "Illustrative clear-sky day (MW)", "Hour", "MW"), use_container_width=True)
    with t2:
        c1, c2 = st.columns([1, 1.4])
        with c1:
            e = qty("Energy generated", 120.0, "Energy", ["MWh", "kWh"], "MWh", "r2e")
            cap = qty("Installed capacity", 10.0, "Power", ["MW", "kW"], "MW", "r2c", 1e-4)
            hrs = qty("Period", 24.0, "Time", ["h", "min"], "h", "r2t", 1e-4)
        formula("CF (%) = Energy / (Capacity × hours) × 100")
        cf = e / (cap * hrs) * 100
        with c2:
            c2.plotly_chart(gauge(cf, "Capacity factor", 100, 100), use_container_width=True)
    with t3:
        c1, c2 = st.columns([1, 1.4])
        with c1:
            p = qty("Active power P", 7.0, "Power", ["MW", "kW"], "MW", "r3p")
            q = qty("Reactive power Q", 2.0, "Reactive power", ["MVAr", "kVAr"], "MVAr", "r3q", -1e9)
            smax = st.number_input("Inverter S rating (MVA, optional)", 0.0, value=7.5)
        s = math.hypot(p, q)
        formula("S = √(P² + Q²)")
        with c2:
            a, b = st.columns(2)
            kpi(a, "Required S", s, "MVA"); kpi(b, "PF", p / s if s else 1, "", ".4f")
            th = np.linspace(-math.pi / 2, math.pi / 2, 100)
            f = go.Figure()
            if smax:
                f.add_trace(go.Scatter(x=smax * np.cos(th), y=smax * np.sin(th), fill="toself", name="Inverter capability",
                                       line=dict(color=PAL[2]), fillcolor="rgba(42,157,143,.12)"))
            f.add_trace(go.Scatter(x=[p], y=[q], mode="markers", marker=dict(size=14, color=PAL[1]), name="Operating point"))
            f.update_yaxes(scaleanchor="x")
            st.plotly_chart(style(f, "P–Q capability", "P (MW)", "Q (MVAr)"), use_container_width=True)
            if smax and s > smax: st.error("Operating point exceeds inverter rating.")
    glossary([("MWp", "DC peak nameplate"), ("DC/AC", "DC capacity ÷ AC capacity"), ("CF", "Capacity factor")])

# ================================================================ UNIT CONVERTER
elif page == "Unit converter":
    g = st.selectbox("Quantity type", list(UNITS))
    u = list(UNITS[g])
    a, b, c = st.columns([1.2, 1, 1])
    val = a.number_input("Value", value=1.0, format="%.8f")
    fu = b.selectbox("From", u, index=0)
    tu = c.selectbox("To", u, index=min(1, len(u) - 1))
    formula("Output = Input × (factor of input unit ÷ factor of output unit)")
    kpi(st, "Converted value", convert(val, g, fu, tu), tu, ".8g")
    st.markdown("### Conversion table")
    st.dataframe([{"Unit": k, "Value": f"{convert(val, g, fu, k):.8g}"} for k in u], hide_index=True, use_container_width=True)

# ================================================================ REFERENCE
else:
    refs = {
        "Three-phase power": [("S = √3 VLL I", "Apparent power"), ("P = √3 VLL I cosφ", "Active power"), ("Q = √3 VLL I sinφ", "Reactive power")],
        "Power factor correction": [("Qc = P[tan(cos⁻¹PF₁) − tan(cos⁻¹PF₂)]", "Capacitor rating")],
        "Transformer": [("I = S/(√3 VLL)", "Rated current"), ("Loading % = Sload/Srated × 100", "Loading"), ("Pcu = 3 I² R", "Copper loss")],
        "Transmission line": [("ΔVLL ≈ √3 I L (R cosφ + X sinφ)", "Voltage drop"), ("Ploss = 3 I² R", "Line loss")],
        "Per-unit": [("Zbase = Vbase²/Sbase", "Base impedance"), ("Zpu,new = Zpu,old (Snew/Sold)(Vold/Vnew)²", "Base change")],
        "Short circuit": [("Isc = VLL/(√3 |Zth|)", "Fault current"), ("Ssc = √3 VLL Isc", "Fault level")],
        "BESS": [("E = P × t", "Energy"), ("Eusable ≈ Enom × DoD × η", "Usable energy"), ("PBESS = max(0, Ppeak − Ptarget)", "Peak shaving")],
        "Renewables": [("DC/AC = MWp / MWac", "Sizing ratio"), ("CF = E/(Prated × t) × 100", "Capacity factor")],
    }
    topic = st.selectbox("Topic", list(refs))
    for f_, d in refs[topic]:
        st.markdown(f"**{d}**"); st.code(f_, language="text")
    st.markdown("### Common abbreviations")
    st.table([{"Abbreviation": a, "Meaning": b} for a, b in [
        ("P / Q / S", "Active / reactive / apparent power"), ("PF", "Power factor"), ("VLL / VLN", "Line-line / line-neutral voltage"),
        ("pu", "Per unit"), ("Isc / Zth", "Short-circuit current / Thevenin impedance"),
        ("BESS / SOC / DoD", "Battery storage / state of charge / depth of discharge"), ("MWp", "PV DC peak capacity")]])

st.divider()
st.markdown('<p class="small">GridCalc • Verify input units, assumptions, equipment data and applicable standards before using results in formal studies.</p>', unsafe_allow_html=True)
