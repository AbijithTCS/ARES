# ARES
ACCESSIBLE RECONFIGURABLE SPACE DESIGNER

Overview:-

The ARES Designer is a rapid prototyping tool that addresses the critical need for speed and compliance in early-stage habitat architecture. We developed an intuitive dashboard that uses Streamlit (Python) to implement a Constraint Engine based on NASA's volumetric standards. Users define crew size and add functional modules (e.g., Sleep, Galley, Exercise); the tool instantly validates the design against the required Min Net Habitable Volume (NHV \approx 29 \text{ m}^3 \text{ per crew}). This process eliminates guesswork, providing immediate RED/YELLOW/GREEN feedback to accelerate design iterations, mitigate human-factor risks, and ensure the future crew's safety and psychological comfort on long-duration missions.

Key features:-

Constraint Engine & Validation: Our core feature provides instant RED/YELLOW/GREEN status on design compliance. It validates total functional volume against the NASA-derived Min NHV floor (\approx 29 \text{ m}^3 \text{ per crew}), mitigating human-factor risks immediately.

Rapid Modular Prototyping: Allows users to quickly define mission parameters (Crew Size, Habitat Radius) and add pre-calibrated functional modules (like Sleep Quarters: \mathbf{13.96 \text{ m}^3}) from a clear palette.

Visualization and Accessibility: Presents the data via an intuitive, functional web dashboard built with Streamlit (Python) and displays a conceptual 3D visualization of module placement.

Future-Proof Design: The system is designed for future integration of Natural Language Processing (NLP) to query and refine complex, data-driven design standards conversationally.

