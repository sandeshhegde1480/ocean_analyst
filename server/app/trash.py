General Information Columns:
    • Date: The date when the data was recorded.
    • Time: The time of day when the data was recorded, likely in seconds or milliseconds since a reference point.
    •Id: Id of the row.

    Pressure-Related Columns (in Bar):
    • PT1(Bar) to PT12(Bar): These columns represent pressure measurements from various points in the system, possibly indicating pressures at different stages or components of the PTO system. The specific location of each pressure transducer (PT) would depend on the system's design.
    • PT21(Bar): Another pressure measurement, which might be a critical pressure point within the system.

    Displacement and Angle-Related Columns:
    • Zla1(mm), Zla2(mm), Zla3(mm): Vertical displacement measurements in millimeters, potentially from linear actuators or sensors monitoring vertical movement at different points.
    • theta1(deg), theta2(deg), theta3(deg): Angular measurements in degrees, likely representing rotational positions or orientations of components within the PTO system.

    Motion Reference Unit (MRU) Data (in degrees for rotations, meters for displacements):
    • Roll(deg): The rotational angle around the longitudinal axis (front to back), representing the side-to-side tilt.
    • Pitch(deg): The rotational angle around the transverse axis (side to side), representing the nose-up or nose-down tilt.
    • Yaw(deg): The rotational angle around the vertical axis, representing the heading or rotation in the horizontal plane.
    • Surge(m): The linear displacement along the longitudinal axis (forward/backward movement) in meters.
    • Sway(m): The linear displacement along the transverse axis (sideways movement) in meters.
    • Heave(m): The linear displacement along the vertical axis (up/down movement) in meters. Note that this column contains all null values in the provided sample.