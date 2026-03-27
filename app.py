import streamlit as st
import pandas as pd
import numpy as np
import re

st.set_page_config(page_title="Smart Material Balance Calculator", layout="wide")

st.title("⚗️ Smart Material Balance Calculator")

# -------------------------------
# FLOW DIAGRAM (SIMPLE)
# -------------------------------
def flow_diagram(inlets, outlets, unit="UNIT"):
    inlet_text = " + ".join([f"{x:.2f}" for x in inlets])
    outlet_text = " + ".join([f"{x:.2f}" for x in outlets])

    st.markdown(f"""
    <div style="text-align:center">

    <div style="color:#1f77b4;font-weight:bold;font-size:18px;">
    Inlets: {inlet_text}
    </div>

    <div style="font-size:30px;">⬇️</div>

    <div style="
        display:inline-block;
        padding:20px;
        background-color:#f4b400;
        border-radius:12px;
        font-weight:bold;
        font-size:18px;">
        {unit}
    </div>

    <div style="font-size:30px;">⬇️</div>

    <div style="color:#2ca02c;font-weight:bold;font-size:18px;">
    Outlets: {outlet_text}
    </div>

    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# PARSE CHEMICAL FORMULA
# -------------------------------
def parse_formula(formula):
    elements = re.findall(r'([A-Z][a-z]*)(\d*)', formula)
    comp = {}
    for el, num in elements:
        comp[el] = comp.get(el, 0) + int(num if num else 1)
    return comp

# -------------------------------
# AUTO BALANCE REACTION
# -------------------------------
def balance_reaction(reactants, products, formulas):
    elements = set()
    for f in formulas.values():
        elements.update(parse_formula(f).keys())
    elements = list(elements)

    matrix = []

    for el in elements:
        row = []
        for c in reactants:
            row.append(parse_formula(formulas[c]).get(el, 0))
        for c in products:
            row.append(-parse_formula(formulas[c]).get(el, 0))
        matrix.append(row)

    A = np.array(matrix)
    u, s, vh = np.linalg.svd(A)
    coeffs = vh[-1]

    coeffs = coeffs / min([abs(x) for x in coeffs if abs(x) > 1e-6])
    coeffs = np.round(coeffs).astype(int)

    return coeffs[:len(reactants)], coeffs[len(reactants):]

# -------------------------------
# SYSTEM TYPE
# -------------------------------
system = st.selectbox("Select System Type", ["Non-Reactive", "Reactive"])

# =====================================================
# NON-REACTIVE SYSTEM
# =====================================================
if system == "Non-Reactive":

    st.header("🔹 Non-Reactive Multi-Stream System")

    n = st.number_input("Number of Streams", 1, 5, 2)

    inlets = []
    outlets = []

    st.subheader("📥 Inlet Streams")
    for i in range(n):
        val = st.number_input(f"Inlet {i+1}", key=f"in{i}")
        inlets.append(val)

    st.subheader("📤 Outlet Streams")
    for i in range(n):
        val = st.number_input(f"Outlet {i+1}", key=f"out{i}")
        outlets.append(val)

    total_in = sum(inlets)
    total_out = sum(outlets)

    flow_diagram(inlets, outlets, "SEPARATOR")

    st.subheader("📊 Balance Check")
    st.write(f"Total In = {total_in:.2f}")
    st.write(f"Total Out = {total_out:.2f}")

    if abs(total_in - total_out) < 1e-6:
        st.success("✅ System is Balanced")
    else:
        st.error("❌ Not Balanced")

# =====================================================
# REACTIVE SYSTEM
# =====================================================
elif system == "Reactive":

    st.header("🔥 Reactive System Solver (Advanced)")

    # -------------------------------
    # CHEMICAL DATABASE
    # -------------------------------
    st.subheader("🧪 Chemical Selection")

    chem_db = pd.DataFrame({
        "Name": [
            "Methane","Ethane","Propane","Butane","Pentane","Hexane",
            "Oxygen","Nitrogen","Hydrogen","Carbon dioxide","Carbon monoxide",
            "Water","Ethanol","Methanol","Benzene","Toluene","Xylene",
            "Ammonia","Sulfur dioxide","Hydrogen sulfide","Acetone","Ethylene",
            "Propylene","Butadiene","Chlorine","Hydrochloric acid","Nitric acid",
            "Sulfuric acid","Formaldehyde","Acetic acid","Phenol","Urea"
        ],
        "Formula": [
            "CH4","C2H6","C3H8","C4H10","C5H12","C6H14",
            "O2","N2","H2","CO2","CO",
            "H2O","C2H5OH","CH3OH","C6H6","C7H8","C8H10",
            "NH3","SO2","H2S","C3H6O","C2H4",
            "C3H6","C4H6","Cl2","HCl","HNO3",
            "H2SO4","CH2O","CH3COOH","C6H5OH","CH4N2O"
        ],
        "MW": [
            16.04,30.07,44.10,58.12,72.15,86.18,
            32.00,28.01,2.02,44.01,28.01,
            18.02,46.07,32.04,78.11,92.14,106.17,
            17.03,64.07,34.08,58.08,28.05,
            42.08,54.09,70.90,36.46,63.01,
            98.08,30.03,60.05,94.11,60.06
        ]
    })

    n_react = st.number_input("Number of Reactants", 1, 5, 2)
    n_prod = st.number_input("Number of Products", 1, 5, 2)

    R, P, formulas = [], [], {}

    st.subheader("Select Reactants")
    for i in range(n_react):
        chem = st.selectbox(f"Reactant {i+1}", chem_db["Name"], key=f"R{i}")
        tag = f"R{i+1}"
        R.append(tag)
        formulas[tag] = chem_db[chem_db["Name"] == chem]["Formula"].values[0]

    st.subheader("Select Products")
    for i in range(n_prod):
        chem = st.selectbox(f"Product {i+1}", chem_db["Name"], key=f"P{i}")
        tag = f"P{i+1}"
        P.append(tag)
        formulas[tag] = chem_db[chem_db["Name"] == chem]["Formula"].values[0]

    comps = R + P

    st.subheader("📊 Selected Components")
    for comp in comps:
        st.write(f"{comp} → {formulas[comp]}")

    if st.button("Auto Balance Reaction"):
        try:
            vR_auto, vP_auto = balance_reaction(R, P, formulas)
            st.success(f"Balanced → Reactants: {vR_auto}, Products: {vP_auto}")
        except:
            st.error("Balancing failed")

    num_rxn = st.number_input("Number of Reactions", 1, 3, 1)

    st.subheader("⚙️ Stoichiometric Coefficients")

    stoich = {}
    for comp in comps:
        vals = st.text_input(f"{comp} coefficients", ",".join(["0"]*num_rxn))
        try:
            stoich[comp] = list(map(float, vals.split(",")))
        except:
            stoich[comp] = [0]*num_rxn

    # -------------------------------
    # FLEXIBLE FEED INPUT
    # -------------------------------
    st.subheader("📥 Feed (Flexible Units)")

    feed = {}

    unit_options = [
        "Moles (mol)",
        "Molar Flowrate (mol/s)",
        "Mass (g)",
        "Mass Flowrate (g/s)",
        "Volume (L)",
        "Volumetric Flowrate (L/s)"
    ]

    Vm = 22.414  # L/mol

    for comp in comps:

        st.markdown(f"### {comp}")

        unit = st.selectbox(f"Unit for {comp}", unit_options, key=f"unit_{comp}")
        value = st.number_input(f"Value for {comp}", key=f"value_{comp}")

        formula = formulas[comp]
        row = chem_db[chem_db["Formula"] == formula]

        MW = row["MW"].values[0] if not row.empty else 1

        try:
            if "Moles" in unit:
                mol = value
            elif "Mass" in unit:
                mol = value / MW
            elif "Volume" in unit:
                mol = value / Vm
            else:
                mol = value

        except:
            mol = 0

        feed[comp] = mol
        st.write(f"➡️ {mol:.4f} mol")

    # SOLVER (UNCHANGED)
    st.subheader("⚡ Auto Solve Multiple Extents (ξ₁, ξ₂, …)")

    known_comps = st.multiselect("Select known outlets", comps)

    outlet_known = {}
    for comp in known_comps:
        outlet_known[comp] = st.number_input(f"Outlet {comp}", key=f"out_{comp}")

    xi = None

    unknowns = num_rxn
    equations = len(known_comps)
    dof = unknowns - equations

    st.subheader("📐 Degree of Freedom Analysis")
    st.write(f"DOF = {dof}")

    if dof == 0:
        try:
            A, b = [], []
            for comp in known_comps:
                A.append(stoich[comp])
                b.append(outlet_known[comp] - feed[comp])
            xi = np.linalg.solve(np.array(A), np.array(b))
            st.success(f"ξ = {xi}")
        except:
            st.error("Solve failed")

    # -------------------------------
    # PERFORMANCE METRICS SETUP
    # -------------------------------
    st.subheader("📈 Performance Metrics Setup")
    st.markdown("Select your key components to calculate conversion, yield, and selectivity.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        lim_react = st.selectbox("Limiting Reactant", R, key="lim_react")
    with col2:
        des_prod = st.selectbox("Desired Product", P, key="des_prod")
    with col3:
        undes_prod = st.selectbox("Undesired Product", ["None"] + P, key="undes_prod")

    if st.button("Run Simulation") and xi is not None:

        final = feed.copy()

        for j in range(num_rxn):
            for comp in comps:
                final[comp] += stoich[comp][j] * xi[j]

        st.write(final)
        flow_diagram([sum(feed.values())], [sum(final.values())], "PROCESS")

        # -------------------------------
        # PERFORMANCE METRICS CALCULATIONS
        # -------------------------------
        st.subheader("🎯 System Performance Metrics")

        # 1. Fractional Conversion
        fed_lr = feed.get(lim_react, 0)
        final_lr = final.get(lim_react, 0)
        conversion = (fed_lr - final_lr) / fed_lr if fed_lr > 1e-6 else 0

        # 2. Selectivity (Moles of Desired / Moles of Undesired)
        formed_dp = final.get(des_prod, 0) - feed.get(des_prod, 0)
        
        if undes_prod != "None":
            formed_up = final.get(undes_prod, 0) - feed.get(undes_prod, 0)
            selectivity = formed_dp / formed_up if formed_up > 1e-6 else float('inf')
        else:
            selectivity = float('inf')

        # 3. Reaction Yield (Actual DP formed / Theoretical DP from limiting reactant)
        stoich_lr = stoich[lim_react][0] if len(stoich[lim_react]) > 0 else 0
        stoich_dp = stoich[des_prod][0] if len(stoich[des_prod]) > 0 else 0

        if stoich_lr != 0 and fed_lr > 1e-6:
            theo_dp = fed_lr * abs(stoich_dp / stoich_lr)
            reaction_yield = formed_dp / theo_dp if theo_dp > 1e-6 else 0
        else:
            reaction_yield = 0

        # 4. Plant Yield (Mass of DP formed / Mass of LR fed)
        try:
            mw_dp = chem_db[chem_db["Formula"] == formulas[des_prod]]["MW"].values[0]
            mw_lr = chem_db[chem_db["Formula"] == formulas[lim_react]]["MW"].values[0]
        except IndexError:
            mw_dp, mw_lr = 1, 1 

        mass_formed_dp = formed_dp * mw_dp
        mass_fed_lr = fed_lr * mw_lr
        plant_yield = mass_formed_dp / mass_fed_lr if mass_fed_lr > 1e-6 else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Fractional Conversion", f"{conversion:.2%}")
        
        sel_text = f"{selectivity:.2f}" if selectivity != float('inf') else "N/A"
        m2.metric("Selectivity (DP/UP)", sel_text)
        
        m3.metric("Reaction Yield", f"{reaction_yield:.2%}")
        m4.metric("Plant Yield (Mass)", f"{plant_yield:.2f} g/g")