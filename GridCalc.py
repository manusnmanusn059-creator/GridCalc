import math
import streamlit as st

st.set_page_config(page_title="GridCalc | Power System Engineering", page_icon="⚡", layout="wide")

# ---------- Styling ----------
st.markdown("""
<style>
:root { --ink:#14243a; --muted:#66758a; --line:#e5eaf1; --blue:#1769aa; }
.block-container {padding-top: 1.3rem; padding-bottom: 2rem; max-width: 1450px;}
[data-testid="stSidebar"] {border-right:1px solid #e5eaf1;}
.hero {padding:1.25rem 1.45rem; border:1px solid #dfe8f2; border-radius:18px;
       background:linear-gradient(115deg,#f4f8fd 0%,#ffffff 72%); margin-bottom:1rem;}
.hero h1 {font-size:1.8rem; margin:0; color:#14243a;}
.hero p {color:#5e7087; margin:.35rem 0 0 0;}
.section-note {color:#63748a; font-size:.91rem;}
.formula {background:#f5f8fc; border-left:4px solid #1769aa; padding:.75rem 1rem;
          border-radius:8px; margin:.45rem 0 1rem 0;}
.small-muted {font-size:.82rem; color:#718096;}
div[data-testid="stMetric"] {background:#fff; border:1px solid #e5eaf1; padding:.75rem;
                              border-radius:12px;}
</style>
""", unsafe_allow_html=True)

# ---------- Units ----------
UNITS = {
    "Power": {"W":1, "kW":1e3, "MW":1e6, "GW":1e9},
    "Apparent power": {"VA":1, "kVA":1e3, "MVA":1e6},
    "Reactive power": {"var":1, "kVAr":1e3, "MVAr":1e6},
    "Energy": {"Wh":1, "kWh":1e3, "MWh":1e6, "GWh":1e9},
    "Voltage": {"V":1, "kV":1e3},
    "Current": {"A":1, "kA":1e3},
    "Resistance": {"Ω":1, "mΩ":1e-3, "kΩ":1e3},
    "Impedance": {"Ω":1, "mΩ":1e-3, "kΩ":1e3},
    "Frequency": {"Hz":1, "kHz":1e3},
    "Time": {"s":1, "min":60, "h":3600},
    "Length": {"m":1, "km":1e3},
    "Capacitance": {"F":1, "µF":1e-6, "mF":1e-3},
}

def convert(value, group, from_u, to_u):
    return value * UNITS[group][from_u] / UNITS[group][to_u]

def formula(txt):
    st.markdown(f'<div class="formula"><b>Formula / method</b><br>{txt}</div>', unsafe_allow_html=True)

def glossary(items):
    with st.expander("Symbols and abbreviations", expanded=False):
        st.table([{"Symbol":a, "Meaning":b} for a,b in items])

def output_metric(label, value, unit, fmt=".4f"):
    st.metric(label, f"{format(value, fmt)} {unit}")

def output_unit(label, units, default):
    return st.selectbox(label, units, index=units.index(default), key=label)

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <h1>⚡ GridCalc — Power System Engineering</h1>
  <p>Focused electrical power-system calculations • Formula reference • Editable engineering units • Daily-use workspace</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚡ GridCalc")
    st.caption("POWER SYSTEM TOOLKIT")
    page = st.radio("WORKSPACE", [
        "Dashboard",
        "Three-phase power",
        "Power factor correction",
        "Transformer",
        "Transmission line",
        "Per-unit system",
        "Short-circuit basics",
        "BESS sizing",
        "Renewable integration",
        "Unit converter",
        "Formula & abbreviation guide"
    ], label_visibility="collapsed")
    st.divider()
    st.caption("Engineering reference • Version 2.0")

st.caption("Enter values in the stated input units. Select the output unit wherever an output-unit selector is provided.")

# ---------- Dashboard ----------
if page == "Dashboard":
    st.subheader("Calculation workspace")
    st.write("Select a power-system calculation from the navigation panel.")
    cards = [
        ("Three-phase power","P, Q, S, current and power factor","Three-phase power"),
        ("Power factor correction","Capacitor bank MVAr / kVAr sizing","Power factor correction"),
        ("Transformer","Rated current, loading and losses","Transformer"),
        ("Transmission line","Voltage drop and I²R losses","Transmission line"),
        ("Per-unit system","Base impedance and impedance conversion","Per-unit system"),
        ("Short circuit","Basic three-phase fault level","Short-circuit basics"),
        ("BESS sizing","Power, energy, duration and usable energy","BESS sizing"),
        ("Unit converter","Editable input and output engineering units","Unit converter"),
    ]
    cols = st.columns(4)
    for idx,(title,desc,target) in enumerate(cards):
        with cols[idx%4]:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.caption(desc)
                if st.button("Open calculator →", key=f"open_{idx}", use_container_width=True):
                    st.session_state["jump_page"] = target
                    st.rerun()
    if "jump_page" in st.session_state:
        st.session_state["page_override"] = st.session_state.pop("jump_page")
    st.info("Tip: Use **Unit converter** whenever you need to change kW ↔ MW, kVAr ↔ MVAr, kWh ↔ MWh, kV ↔ V, or other supported engineering units.")
    st.markdown("### Engineering conventions")
    st.markdown("- Three-phase power equations use line-to-line voltage and line current.\n- Positive reactive power is treated as inductive/lagging in the P–Q calculator.\n- Enter line impedance per phase where requested.\n- BESS calculations are preliminary energy estimates, not dispatch or SOC simulations.")

# Navigation reroute from dashboard buttons
if "page_override" in st.session_state and page == "Dashboard":
    page = st.session_state.pop("page_override")

# ---------- Three phase ----------
if page == "Three-phase power":
    st.subheader("Three-phase power calculator")
    st.caption("Calculate active, reactive and apparent power, power factor or line current.")
    mode = st.selectbox("Calculation mode", ["Calculate P, Q and S from voltage, current and PF",
        "Calculate S and PF from active and reactive power", "Calculate line current from apparent power"])
    c1,c2,c3 = st.columns(3)
    if mode == "Calculate P, Q and S from voltage, current and PF":
        with c1: v = st.number_input("Line voltage VLL", min_value=0.000001, value=11.0); vu=st.selectbox("Voltage unit",["kV","V"])
        with c2: i = st.number_input("Line current I", min_value=0.0, value=250.0); iu=st.selectbox("Current unit",["A","kA"])
        with c3: pf=st.number_input("Power factor", min_value=0.0, max_value=1.0, value=.90, step=.01)
        pu=output_unit("Active power output unit",["W","kW","MW","GW"],"MW")
        qu=output_unit("Reactive power output unit",["var","kVAr","MVAr"],"MVAr")
        su=output_unit("Apparent power output unit",["VA","kVA","MVA"],"MVA")
        formula("S = √3 × VLL × I &nbsp; | &nbsp; P = S × PF &nbsp; | &nbsp; Q = S × √(1 − PF²)")
        if st.button("Calculate", type="primary"):
            vk=v*(1000 if vu=="kV" else 1); ia=i*(1000 if iu=="kA" else 1)
            s=math.sqrt(3)*vk*ia; p=s*pf; q=s*math.sqrt(max(0,1-pf**2))
            a,b,c=st.columns(3)
            with a: output_metric("Active power P",convert(p,"Power","W",pu),pu)
            with b: output_metric("Reactive power |Q|",convert(q,"Reactive power","var",qu),qu)
            with c: output_metric("Apparent power S",convert(s,"Apparent power","VA",su),su)
    elif mode == "Calculate S and PF from active and reactive power":
        a,b=st.columns(2)
        with a: p=st.number_input("Active power P",min_value=0.0,value=5.0); punit=st.selectbox("P unit",["MW","kW","W"])
        with b: q=st.number_input("Reactive power Q (positive inductive, negative capacitive)",value=3.0); qunit=st.selectbox("Q unit",["MVAr","kVAr","var"])
        su=output_unit("Apparent power output unit",["VA","kVA","MVA"],"MVA")
        formula("S = √(P² + Q²) &nbsp; | &nbsp; PF = P / S &nbsp; | &nbsp; φ = atan2(Q, P)")
        if st.button("Calculate",type="primary"):
            pw=convert(p,"Power",punit,"W"); qw=convert(q,"Reactive power",qunit,"var"); s=math.hypot(pw,qw)
            a,b,c=st.columns(3)
            with a: output_metric("Apparent power S",convert(s,"Apparent power","VA",su),su)
            with b: output_metric("Power factor",pw/s if s else 0,"pu")
            with c: output_metric("Power-factor angle",math.degrees(math.atan2(qw,pw)),"degrees")
            st.write("Nature:", "Lagging / inductive" if qw>0 else ("Leading / capacitive" if qw<0 else "Unity"))
    else:
        a,b=st.columns(2)
        with a: s=st.number_input("Apparent power S",min_value=0.0,value=5.0); su=st.selectbox("S unit",["MVA","kVA","VA"])
        with b: v=st.number_input("Line voltage VLL",min_value=.000001,value=11.0); vu=st.selectbox("Voltage unit",["kV","V"])
        iu=output_unit("Current output unit",["A","kA"],"A")
        formula("I = S / (√3 × VLL)")
        if st.button("Calculate",type="primary"):
            sv=convert(s,"Apparent power",su,"VA"); vv=convert(v,"Voltage",vu,"V")
            output_metric("Line current",convert(sv/(math.sqrt(3)*vv),"Current","A",iu),iu)
    glossary([("P","Active / real power"),("Q","Reactive power"),("S","Apparent power"),("PF","Power factor"),("VLL","Line-to-line RMS voltage"),("I","Line current"),("φ","Power-factor angle")])

# ---------- PF correction ----------
elif page == "Power factor correction":
    st.subheader("Power factor correction / capacitor bank sizing")
    a,b,c=st.columns(3)
    with a: p=st.number_input("Active load power",min_value=0.0,value=1000.0); pu=st.selectbox("Active power unit",["kW","MW","W"])
    with b: pf1=st.number_input("Initial PF",min_value=.01,max_value=1.0,value=.80,step=.01)
    with c: pf2=st.number_input("Target PF",min_value=.01,max_value=1.0,value=.95,step=.01)
    qu=output_unit("Capacitor output unit",["var","kVAr","MVAr"],"kVAr")
    formula("Qc = P × [tan(cos⁻¹(PF₁)) − tan(cos⁻¹(PF₂))]")
    if st.button("Calculate capacitor requirement",type="primary"):
        if pf2<=pf1: st.error("Target PF must be greater than initial PF for capacitive correction.")
        else:
            pw=convert(p,"Power",pu,"W"); qc=pw*(math.tan(math.acos(pf1))-math.tan(math.acos(pf2)))
            output_metric("Required capacitor rating",convert(qc,"Reactive power","var",qu),qu)
            st.caption("Ideal steady-state kvar requirement. Check voltage rise, harmonics, resonance, switching transients, step sizes and utility requirements.")
    glossary([("Qc","Required capacitive reactive power"),("P","Active load power"),("PF₁","Initial power factor"),("PF₂","Target power factor")])

# ---------- Transformer ----------
elif page == "Transformer":
    st.subheader("Transformer calculations")
    mode=st.selectbox("Calculation",["Rated current","Transformer loading","Three-phase copper loss"])
    if mode=="Rated current":
        a,b,c=st.columns(3)
        with a: s=st.number_input("Transformer rating",min_value=.0001,value=5.0); su=st.selectbox("Rating unit",["MVA","kVA"])
        with b: v=st.number_input("Side voltage",min_value=.0001,value=11.0); vu=st.selectbox("Voltage unit",["kV","V"])
        with c: phase=st.radio("System",["Three-phase","Single-phase"])
        iu=output_unit("Current output unit",["A","kA"],"A")
        formula("3-phase: I = S / (√3 × VLL) &nbsp; | &nbsp; 1-phase: I = S / V")
        if st.button("Calculate rated current",type="primary"):
            sv=convert(s,"Apparent power",su,"VA"); vv=convert(v,"Voltage",vu,"V")
            amps=sv/(math.sqrt(3)*vv) if phase=="Three-phase" else sv/vv
            output_metric("Rated current",convert(amps,"Current","A",iu),iu)
    elif mode=="Transformer loading":
        a,b=st.columns(2)
        with a: rating=st.number_input("Transformer rated capacity",min_value=.0001,value=5.0); ru=st.selectbox("Rating unit",["MVA","kVA"])
        with b: load=st.number_input("Measured apparent load",min_value=0.0,value=4.2); lu=st.selectbox("Load unit",["MVA","kVA"])
        formula("Loading (%) = Measured load / Rated capacity × 100")
        if st.button("Calculate loading",type="primary"):
            pct=convert(load,"Apparent power",lu,"VA")/convert(rating,"Apparent power",ru,"VA")*100
            output_metric("Transformer loading",pct,"%","0.2f")
            if pct>100: st.error("Above nameplate MVA rating.")
            elif pct>80: st.warning("Above the illustrative 80% planning threshold. Apply project-specific criteria.")
            else: st.success("At or below the illustrative 80% planning threshold.")
    else:
        a,b=st.columns(2)
        with a: current=st.number_input("Phase current",min_value=0.0,value=200.0); iu=st.selectbox("Current unit",["A","kA"])
        with b: r=st.number_input("Winding resistance per phase",min_value=0.0,value=.02); ru=st.selectbox("Resistance unit",["Ω","mΩ"])
        pu=output_unit("Loss output unit",["W","kW","MW"],"kW")
        formula("Pcu = 3 × I² × Rphase")
        if st.button("Calculate copper loss",type="primary"):
            amps=convert(current,"Current",iu,"A"); ohms=convert(r,"Resistance",ru,"Ω")
            output_metric("Three-phase copper loss",convert(3*amps**2*ohms,"Power","W",pu),pu)
    glossary([("S","Transformer apparent-power rating"),("VLL","Line-to-line voltage"),("I","Line current"),("Pcu","Copper loss"),("Rphase","Per-phase winding resistance")])

# ---------- Transmission line ----------
elif page == "Transmission line":
    st.subheader("Transmission and distribution line calculations")
    mode=st.selectbox("Calculation",["Approximate three-phase voltage drop","Three-phase line losses"])
    if mode=="Approximate three-phase voltage drop":
        c1,c2,c3=st.columns(3)
        with c1: length=st.number_input("Line length",min_value=0.0,value=5.0); lu=st.selectbox("Length unit",["km","m"])
        with c2: current=st.number_input("Line current",min_value=0.0,value=150.0); iu=st.selectbox("Current unit",["A","kA"])
        with c3: pf=st.number_input("Power factor",min_value=0.0,max_value=1.0,value=.90)
        c1,c2,c3=st.columns(3)
        with c1: r=st.number_input("R per phase per km",min_value=0.0,value=.20); ru=st.selectbox("R unit",["Ω/km","mΩ/km"])
        with c2: x=st.number_input("X per phase per km",min_value=0.0,value=.30); xu=st.selectbox("X unit",["Ω/km","mΩ/km"])
        with c3: v=st.number_input("Nominal line voltage",min_value=.0001,value=11.0); vu=st.selectbox("Voltage unit",["kV","V"])
        formula("ΔVLL ≈ √3 × I × L × (R cosφ + X sinφ) &nbsp; | &nbsp; ΔV% = ΔVLL / VLL × 100")
        if st.button("Calculate voltage drop",type="primary"):
            lm=convert(length,"Length",lu,"km"); amps=convert(current,"Current",iu,"A")
            rr=r*(1 if ru=="Ω/km" else .001); xx=x*(1 if xu=="Ω/km" else .001)
            vv=convert(v,"Voltage",vu,"V"); sinp=math.sqrt(max(0,1-pf**2))
            dv=math.sqrt(3)*amps*lm*(rr*pf+xx*sinp)
            c1,c2=st.columns(2)
            with c1: output_metric("Approx. line-to-line voltage drop",convert(dv,"Voltage","V",vu),vu)
            with c2: output_metric("Voltage drop",dv/vv*100,"%","0.3f")
        st.caption("Approximation for balanced steady-state operation. Uses per-phase R and X per unit length. Confirm conductor temperature and configuration.")
    else:
        a,b=st.columns(2)
        with a: current=st.number_input("Line current",min_value=0.0,value=100.0); iu=st.selectbox("Current unit",["A","kA"])
        with b: r=st.number_input("End-to-end resistance per phase",min_value=0.0,value=.5); ru=st.selectbox("Resistance unit",["Ω","mΩ"])
        pu=output_unit("Loss output unit",["W","kW","MW"],"kW")
        formula("P_loss = 3 × I² × Rphase")
        if st.button("Calculate line losses",type="primary"):
            amps=convert(current,"Current",iu,"A"); ohms=convert(r,"Resistance",ru,"Ω")
            output_metric("Three-phase line loss",convert(3*amps**2*ohms,"Power","W",pu),pu)
    glossary([("R","Per-phase resistance"),("X","Per-phase reactance"),("L","Line length"),("φ","Power-factor angle"),("ΔV","Voltage drop")])

# ---------- Per unit ----------
elif page == "Per-unit system":
    st.subheader("Per-unit system calculator")
    mode=st.selectbox("Calculation",["Impedance pu to ohms","Impedance ohms to pu","Change impedance base"])
    if mode=="Change impedance base":
        zpu=st.number_input("Old impedance (pu)",value=.10)
        c1,c2=st.columns(2)
        with c1: sold=st.number_input("Old MVA base",min_value=.0001,value=50.0); vold=st.number_input("Old kV base",min_value=.0001,value=132.0)
        with c2: snew=st.number_input("New MVA base",min_value=.0001,value=100.0); vnew=st.number_input("New kV base",min_value=.0001,value=132.0)
        formula("Zpu,new = Zpu,old × (Sbase,new / Sbase,old) × (Vbase,old / Vbase,new)²")
        if st.button("Convert base",type="primary"): output_metric("New impedance",zpu*(snew/sold)*(vold/vnew)**2,"pu")
    else:
        z=st.number_input("Impedance value",min_value=0.0,value=.1 if mode=="Impedance pu to ohms" else 5.0)
        c1,c2=st.columns(2)
        with c1: kv=st.number_input("Base line voltage (kV)",min_value=.0001,value=132.0)
        with c2: mva=st.number_input("Three-phase base power (MVA)",min_value=.0001,value=100.0)
        formula("Zbase(Ω) = Vbase(kV)² / Sbase(MVA)")
        if st.button("Convert impedance",type="primary"):
            zb=kv**2/mva
            output_metric("Base impedance",zb,"Ω")
            output_metric("Impedance",z*zb if mode=="Impedance pu to ohms" else z/zb,"Ω" if mode=="Impedance pu to ohms" else "pu")
    glossary([("pu","Per-unit value"),("Zbase","Base impedance"),("Sbase","Three-phase apparent-power base"),("Vbase","Line-to-line voltage base")])

# ---------- Short circuit ----------
elif page == "Short-circuit basics":
    st.subheader("Short-circuit basics")
    mode=st.selectbox("Calculation",["Three-phase fault current from Thevenin impedance","Fault level from fault current"])
    if mode=="Three-phase fault current from Thevenin impedance":
        a,b=st.columns(2)
        with a: v=st.number_input("Prefault line voltage",min_value=.0001,value=11.0); vu=st.selectbox("Voltage unit",["kV","V"])
        with b: z=st.number_input("Positive-sequence Thevenin impedance magnitude",min_value=.000001,value=.5); zu=st.selectbox("Impedance unit",["Ω","mΩ"])
        iu=output_unit("Fault current output unit",["A","kA"],"kA")
        formula("Isc = VLL / (√3 × |Zth|)")
        if st.button("Calculate fault current",type="primary"):
            vv=convert(v,"Voltage",vu,"V"); zz=convert(z,"Impedance",zu,"Ω")
            output_metric("Initial symmetrical 3-phase fault current",convert(vv/(math.sqrt(3)*zz),"Current","A",iu),iu)
    else:
        a,b=st.columns(2)
        with a: v=st.number_input("Nominal line voltage",min_value=.0001,value=11.0); vu=st.selectbox("Voltage unit",["kV","V"])
        with b: i=st.number_input("Three-phase fault current",min_value=0.0,value=20.0); iu=st.selectbox("Fault current unit",["kA","A"])
        su=output_unit("Fault level output unit",["MVA","kVA","VA"],"MVA")
        formula("Fault level (VA) = √3 × VLL(V) × Isc(A)")
        if st.button("Calculate fault level",type="primary"):
            vv=convert(v,"Voltage",vu,"V"); ia=convert(i,"Current",iu,"A")
            output_metric("Three-phase short-circuit level",convert(math.sqrt(3)*vv*ia,"Apparent power","VA",su),su)
    st.warning("Simplified Thevenin calculation only. Not an IEC 60909 implementation. Detailed studies must consider source and motor contributions, sequence networks, voltage factor, X/R ratio, peak current and equipment duties.")
    glossary([("Isc","Short-circuit current"),("Zth","Thevenin equivalent positive-sequence impedance"),("Ik''","Initial symmetrical short-circuit current (IEC notation)")])

# ---------- BESS ----------
elif page == "BESS sizing":
    st.subheader("Battery energy storage system (BESS) sizing")
    mode=st.selectbox("Calculation",["Energy for constant-power discharge","Usable AC energy","Peak-shaving power and energy estimate"])
    if mode=="Energy for constant-power discharge":
        a,b,c=st.columns(3)
        with a: p=st.number_input("AC discharge power",min_value=0.0,value=2.0); pu=st.selectbox("Power unit",["MW","kW"])
        with b: t=st.number_input("Discharge duration",min_value=0.0,value=2.0); tu=st.selectbox("Time unit",["h","min"])
        with c: eta=st.number_input("Discharge efficiency",min_value=.01,max_value=1.0,value=.90)
        eu=output_unit("Energy output unit",["kWh","MWh"],"MWh")
        formula("E_AC = P_AC × t &nbsp; | &nbsp; E_DC,required ≈ E_AC / ηdischarge")
        if st.button("Calculate BESS energy",type="primary"):
            pw=convert(p,"Power",pu,"MW"); hours=convert(t,"Time",tu,"h"); eac=pw*hours
            output_metric("AC energy delivered",convert(eac,"Energy","MWh",eu),eu)
            output_metric("Approx. required DC energy",convert(eac/eta,"Energy","MWh",eu),eu)
    elif mode=="Usable AC energy":
        a,b,c=st.columns(3)
        with a: en=st.number_input("Nominal battery energy",min_value=0.0,value=10.0); eu=st.selectbox("Energy unit",["MWh","kWh"])
        with b: dod=st.number_input("Usable DoD (0–1)",min_value=.01,max_value=1.0,value=.80)
        with c: eta=st.number_input("Discharge efficiency",min_value=.01,max_value=1.0,value=.90)
        out=output_unit("Usable energy output unit",["kWh","MWh"],"MWh")
        formula("Eusable,AC ≈ Enominal × DoD × ηdischarge")
        if st.button("Calculate usable energy",type="primary"):
            e=convert(en,"Energy",eu,"MWh")*dod*eta
            output_metric("Approx. usable AC energy",convert(e,"Energy","MWh",out),out)
    else:
        a,b,c=st.columns(3)
        with a: peak=st.number_input("Existing peak demand",min_value=0.0,value=8.0); pu=st.selectbox("Demand unit",["MW","kW"])
        with b: target=st.number_input("Target grid import",min_value=0.0,value=6.0); tu=st.selectbox("Target unit",["MW","kW"])
        with c: duration=st.number_input("Required duration",min_value=0.0,value=2.0); tim=st.selectbox("Duration unit",["h","min"])
        eta=st.number_input("Discharge efficiency",min_value=.01,max_value=1.0,value=.90)
        powout=output_unit("BESS power output unit",["kW","MW"],"MW")
        enout=output_unit("BESS energy output unit",["kWh","MWh"],"MWh")
        formula("PBESS = max(0, Peak − Target) &nbsp; | &nbsp; Enominal ≈ PBESS × duration / η")
        if st.button("Calculate peak-shaving requirement",type="primary"):
            pb=max(0,convert(peak,"Power",pu,"MW")-convert(target,"Power",tu,"MW"))
            e=pb*convert(duration,"Time",tim,"h")/eta
            output_metric("Required BESS AC power",convert(pb,"Power","MW",powout),powout)
            output_metric("Approx. nominal energy",convert(e,"Energy","MWh",enout),enout)
    st.caption("Preliminary sizing only. A project design should include SOC limits, degradation, auxiliary loads, temperature, C-rate, inverter P-Q capability, charging source/window, network constraints and dispatch strategy.")
    glossary([("BESS","Battery energy storage system"),("SOC","State of charge"),("DoD","Depth of discharge"),("η","Efficiency"),("C-rate","Charge/discharge current relative to rated capacity")])

# ---------- Renewable integration ----------
elif page == "Renewable integration":
    st.subheader("Renewable energy integration")
    mode=st.selectbox("Calculation",["PV DC/AC ratio","Plant capacity factor and energy","Inverter apparent power from P and Q"])
    if mode=="PV DC/AC ratio":
        a,b=st.columns(2)
        with a: dc=st.number_input("PV module capacity",min_value=0.0,value=10.16); du=st.selectbox("DC unit",["MWp","kWp"])
        with b: ac=st.number_input("Inverter / evacuation capacity",min_value=.0001,value=7.0); au=st.selectbox("AC unit",["MW","kW"])
        formula("DC/AC ratio = PV DC nameplate capacity / AC inverter capacity")
        if st.button("Calculate DC/AC ratio",type="primary"):
            ratio=convert(dc,"Power",du.replace("p",""),"MW")/convert(ac,"Power",au,"MW")
            output_metric("PV DC/AC ratio",ratio,"", "3f")
    elif mode=="Plant capacity factor and energy":
        a,b,c=st.columns(3)
        with a: energy=st.number_input("Energy generated",min_value=0.0,value=120.0); eu=st.selectbox("Energy unit",["MWh","kWh"])
        with b: cap=st.number_input("Installed capacity",min_value=.0001,value=10.0); cu=st.selectbox("Capacity unit",["MW","kW"])
        with c: hours=st.number_input("Period duration",min_value=.0001,value=24.0); hu=st.selectbox("Time unit",["h","days"])
        formula("Capacity factor (%) = Energy generated / (Installed capacity × Period hours) × 100")
        if st.button("Calculate capacity factor",type="primary"):
            eh=convert(energy,"Energy",eu,"MWh"); cm=convert(cap,"Power",cu,"MW"); hh=hours*(24 if hu=="days" else 1)
            output_metric("Capacity factor",eh/(cm*hh)*100,"%","0.2f")
    else:
        p=st.number_input("Active power P",min_value=0.0,value=7.0); pu=st.selectbox("P unit",["MW","kW"])
        q=st.number_input("Reactive power Q",value=2.0); qu=st.selectbox("Q unit",["MVAr","kVAr"])
        su=output_unit("Inverter apparent power output unit",["kVA","MVA"],"MVA")
        formula("S = √(P² + Q²)")
        if st.button("Calculate inverter apparent power",type="primary"):
            pw=convert(p,"Power",pu,"MW"); qw=convert(q,"Reactive power",qu,"MVAr")
            output_metric("Required apparent power",convert(math.hypot(pw,qw),"Apparent power","MVA",su),su)
    glossary([("MWp","Megawatt-peak DC module nameplate capacity"),("DC/AC ratio","PV DC capacity divided by AC inverter capacity"),("CF","Capacity factor"),("P","Active power"),("Q","Reactive power")])

# ---------- Unit converter ----------
elif page == "Unit converter":
    st.subheader("Engineering unit converter")
    st.caption("Fully editable: enter any value, select its unit, and choose the required output unit.")
    group=st.selectbox("Quantity type",list(UNITS.keys()))
    units=list(UNITS[group].keys())
    a,b,c=st.columns([1.2,1,1])
    with a: value=st.number_input("Enter value",value=1.0,format="%.8f")
    with b: from_u=st.selectbox("Convert from",units,index=0)
    with c: to_u=st.selectbox("Convert to",units,index=min(1,len(units)-1))
    formula("Output value = Input value × (base factor of input unit / base factor of output unit)")
    output_metric("Converted value",convert(value,group,from_u,to_u),to_u,".8g")
    st.markdown("### Quick conversions")
    quick = {
        "Power": [("1 MW",1000,"kW"),("1 MW",1e6,"W")],
        "Apparent power": [("1 MVA",1000,"kVA"),("1 MVA",1e6,"VA")],
        "Reactive power": [("1 MVAr",1000,"kVAr"),("1 MVAr",1e6,"var")],
        "Energy": [("1 MWh",1000,"kWh"),("1 MWh",1e6,"Wh")],
        "Voltage": [("1 kV",1000,"V")],
        "Current": [("1 kA",1000,"A")],
    }
    if group in quick:
        for label,val,unit in quick[group]:
            st.write(f"**{label} = {val:g} {unit}**")
    glossary([("Input value","The numerical value you want to convert"),("Input unit","Unit of the entered value"),("Output unit","Unit in which the converted result is displayed")])

# ---------- Reference ----------
elif page == "Formula & abbreviation guide":
    st.subheader("Power-system formula and abbreviation reference")
    st.caption("Quick reference for commonly used equations. Select a topic to review formulas and variable definitions.")
    refs={
      "Three-phase power":[("S = √3 VLL I","Apparent power (VA)"),("P = √3 VLL I cosφ","Active power (W)"),("Q = √3 VLL I sinφ","Reactive power (var)"),("PF = P/S = cosφ","Power factor")],
      "Power factor correction":[("Qc = P[tan(cos⁻¹PF₁) − tan(cos⁻¹PF₂)]","Required capacitor rating (var)")],
      "Transformer":[("I = S/(√3 VLL)","Three-phase rated line current"),("Loading (%) = Sload/Srated × 100","Transformer loading"),("Pcu = 3 I² Rphase","Three-phase copper loss")],
      "Transmission line":[("ΔVLL ≈ √3 I L(R cosφ + X sinφ)","Approximate balanced three-phase voltage drop"),("Ploss = 3 I² Rphase","Three-phase resistive line loss")],
      "Per-unit":[("Zbase = Vbase²/Sbase","Three-phase base impedance"),("Zpu = Zactual/Zbase","Per-unit impedance"),("Zpu,new = Zpu,old(Snew/Sold)(Vold/Vnew)²","Impedance base conversion")],
      "Short circuit":[("Isc = VLL/(√3 |Zth|)","Basic three-phase Thevenin fault current"),("Ssc = √3 VLL Isc","Three-phase short-circuit level")],
      "BESS":[("E = P × t","Energy for constant-power operation"),("Eusable ≈ Enominal × DoD × η","Approximate usable AC energy"),("PBESS = max(0, Ppeak − Ptarget)","Peak-shaving power")],
      "Renewable integration":[("DC/AC ratio = PV DC MWp / inverter AC MW","PV sizing ratio"),("CF = Egenerated/(Prated × time) × 100","Capacity factor")]
    }
    topic=st.selectbox("Formula topic",list(refs.keys()))
    for f,desc in refs[topic]:
        st.markdown(f"**{desc}**")
        st.code(f,language="text")
    st.markdown("### Common abbreviations")
    st.table([
      {"Abbreviation":"P / Q / S","Meaning":"Active / reactive / apparent power"},
      {"Abbreviation":"PF","Meaning":"Power factor"},
      {"Abbreviation":"VLL / VLN","Meaning":"Line-to-line / line-to-neutral voltage"},
      {"Abbreviation":"pu","Meaning":"Per unit"},
      {"Abbreviation":"Isc / Zth","Meaning":"Short-circuit current / Thevenin impedance"},
      {"Abbreviation":"BESS / SOC / DoD","Meaning":"Battery energy storage system / state of charge / depth of discharge"},
      {"Abbreviation":"MWp","Meaning":"PV DC peak nameplate capacity"},
      {"Abbreviation":"ICT","Meaning":"Interconnecting transformer"}
    ])

st.divider()
st.markdown('<p class="small-muted">GridCalc • Power-system calculations only • Check input units, assumptions, equipment data and applicable standards before using results in formal studies.</p>',unsafe_allow_html=True)
