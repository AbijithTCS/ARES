import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIGURATION CONSTANTS (Based on NASA Data) ---

# Minimum Net Habitable Volume (NHV) Floor derived from the 4-crew minimum (115.83 m³ / 4 crew)
MIN_NHV_PER_CREW = 28.96

# Habitat configuration (fixed height for simplified cylindrical model)
HABITAT_HEIGHT = 8.0

# Define functional module properties (Type, Volume, Color)
MODULE_DATA = {
    'sleep': {'name': 'Sleep Quarters', 'volume': 13.96, 'color': 'orange', 'size': [2.0, 3.5, 2.0]},
    # Min volume for private quarters
    'galley': {'name': 'Galley/Prep', 'volume': 3.30, 'color': 'green', 'size': [1.5, 1.5, 1.5]},  # Meal Prep-2
    'eclss': {'name': 'ECLSS/Life Support', 'volume': 4.00, 'color': 'lightblue', 'size': [1.0, 4.0, 1.0]},
    # Systems volume example
    'social': {'name': 'Group Social/Rec', 'volume': 18.20, 'color': 'red', 'size': [4.0, 4.0, 1.5]},
    # Group Social-1/Training
    'exercise': {'name': 'Exercise/Rec', 'volume': 6.12, 'color': 'purple', 'size': [2.5, 1.2, 2.0]},  # Exercise-2
    'medical': {'name': 'Medical Bay', 'volume': 5.80, 'color': 'yellow', 'size': [2.0, 2.0, 1.5]},  # Medical-3
}

# --- 2. STREAMLIT UI SETUP ---

st.set_page_config(layout="wide", page_title="ARES Designer")
st.title("ARES Designer: Habitat Layout & Constraint Validator")
st.markdown("---")

# Initialize session state for modules and volumes
if 'modules' not in st.session_state:
    st.session_state.modules = []


# --- 3. CONSTRAINT ENGINE LOGIC ---

def get_constraint_feedback(crew_size, total_module_volume):
    """Calculates NHV requirements and returns status/message."""
    required_nhv = MIN_NHV_PER_CREW * crew_size

    status_message = ''
    status_emoji = ''
    occupied_pct = (total_module_volume / required_nhv) * 100 if required_nhv else 0

    if total_module_volume == 0:
        status_message = 'Add modules to the habitat to calculate Net Habitable Volume (NHV) utilization.'
        status_emoji = '🟡'
        status_color = '#FFD700'  # Gold (Yellow)
    elif occupied_pct < 80:
        status_message = f'🔴 CRITICAL: Occupied volume ({total_module_volume:.1f} m³) is too low. Design requires {required_nhv:.1f} m³ of functional space (80% minimum goal).**'
        status_emoji = '🔴'
        status_color = '#DC143C'  # Crimson (Red)
    elif occupied_pct < 100:
        status_message = f'🟡 CAUTION: NHV utilization is {occupied_pct:.0f}%. Still requires {(required_nhv - total_module_volume):.1f} m³ of space. Zoning review recommended.'
        status_emoji = '🟡'
        status_color = '#FFA500'  # Orange (Yellow)
    else:
        status_message = f'✅ CONSTRAINTS MET: Total calculated functional NHV ({total_module_volume:.1f} m³) meets or exceeds the minimum requirement.'
        status_emoji = '✅'
        status_color = '#3CB371'  # Medium Sea Green (Green)

    return required_nhv, occupied_pct, status_message, status_emoji, status_color


# --- 4. SIDEBAR INPUTS (Mission Parameters) ---

with st.sidebar:
    st.header("1. Mission Parameters")

    crew_size = st.slider("Crew Size (Artemis/Mars)", 2, 8, 4)
    radius = st.slider("Cylinder Radius (m)", 3.0, 6.0, 4.0, 0.1)

    st.subheader("Habitat Class")
    habitat_class = st.radio("Select Habitat Type (Constrained by Launch Vehicle):",
                             ["Inflatable (Class II)", "Metallic (Class I)", "ISRU Derived (Class III)"])
    st.info(f"Using **Bottom-Up Methodology**: Min NHV Floor = {MIN_NHV_PER_CREW:.2f} m³/crew.")
    st.markdown("---")
    st.header("2. Module Palette")

    # Buttons to add modules
    for key, data in MODULE_DATA.items():
        if st.button(f"➕ {data['name']} ({data['volume']:.1f} m³)", key=key):
            # Calculate random position within the cylinder bounds (x, z must be within radius)
            position = [
                (np.random.rand() - 0.5) * radius * 1.8,  # x: -R to +R
                (np.random.rand() - 0.5) * HABITAT_HEIGHT,  # y: -H/2 to +H/2
                (np.random.rand() - 0.5) * radius * 1.8  # z: -R to +R
            ]
            st.session_state.modules.append({
                'id': len(st.session_state.modules),
                'name': data['name'],
                'volume': data['volume'],
                'color': data['color'],
                'position': position
            })

    if st.button("Clear All Modules", key='clear', type="secondary"):
        st.session_state.modules = []
        st.experimental_rerun()

# --- 5. MAIN PAGE LAYOUT ---

col_viz, col_metrics = st.columns([2, 1])

# Calculate metrics
total_module_volume = sum(mod['volume'] for mod in st.session_state.modules)
required_nhv, occupied_pct, status_message, status_emoji, status_color = get_constraint_feedback(crew_size,
                                                                                                 total_module_volume)

with col_metrics:
    st.header("3. Constraint Engine & Metrics")

    # Display Constraint Feedback
    st.markdown(
        f"<div style='background-color:{status_color}; padding: 15px; border-radius: 10px; color: black; font-weight: bold;'>"
        f"{status_emoji} {status_message}"
        "</div>",
        unsafe_allow_html=True
    )

    st.subheader("Volume Analysis")
    st.metric("Minimum Required NHV", f"{required_nhv:.1f} m³")
    st.metric("Total Occupied Volume", f"{total_module_volume:.1f} m³")
    st.metric("NHV Utilization", f"{occupied_pct:.0f} %")

    # Display Module List/Manifest
    st.subheader("Habitat Module Manifest")
    if st.session_state.modules:
        manifest_data = [{'Module': mod['name'], 'Volume (m³)': mod['volume']} for mod in st.session_state.modules]
        df = pd.DataFrame(manifest_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No modules placed yet.")

with col_viz:
    st.header("4. Habitat Visualization (Top-Down View)")

    # --- Plotly 3D Visualization Placeholder ---

    # Create the cylindrical container geometry
    x_circ = radius * np.cos(np.linspace(0, 2 * np.pi, 50))
    y_circ = radius * np.sin(np.linspace(0, 2 * np.pi, 50))
    z_floor = [-HABITAT_HEIGHT / 2] * 50
    z_ceiling = [HABITAT_HEIGHT / 2] * 50

    fig = go.Figure()

    # Add Habitat Floor (Circle)
    fig.add_trace(go.Scatter3d(x=x_circ, y=y_circ, z=z_floor, mode='lines', name='Habitat Boundary',
                               line=dict(color='blue', width=4)))

    # Add Habitat Modules (Scatter Points with Color/Size cues)
    x_mod, y_mod, z_mod, colors_mod, names_mod = [], [], [], [], []
    for mod in st.session_state.modules:
        x_mod.append(mod['position'][0])
        y_mod.append(mod['position'][2])  # Using Z for the depth axis
        z_mod.append(mod['position'][1])  # Using Y for the vertical axis (height)
        colors_mod.append(mod['color'])
        names_mod.append(f"{mod['name']} ({mod['volume']:.1f} m³)")

    fig.add_trace(go.Scatter3d(
        x=x_mod, y=y_mod, z=z_mod,
        mode='markers',
        marker=dict(size=10, color=colors_mod, opacity=0.8),
        name='Modules',
        text=names_mod
    ))

    # Set layout for a proper 3D habitat view
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X (m)', range=[-radius * 1.2, radius * 1.2]),
            yaxis=dict(title='Z (m)', range=[-radius * 1.2, radius * 1.2]),
            zaxis=dict(title='Y (m)', range=[-HABITAT_HEIGHT / 2 * 1.2, HABITAT_HEIGHT / 2 * 1.2]),
            aspectmode='cube'
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown(
        "**Note on Visualization:** Module locations are relative to the center and randomly placed within the volume for demonstration. The Constraint Engine logic runs independently of visual placement.")