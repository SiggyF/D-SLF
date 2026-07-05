import pyzsf


# Approximate dimensions of the new sea lock at IJmuiden (opened 2022), the
# largest sea lock in the world. It connects the North Sea to the North Sea
# Canal (leading to Amsterdam).
lock_parameters = {
    "lock_length": 500.0,
    "lock_width": 70.0,
    "lock_bottom": -18.0,
}

boundary_conditions = {
    # North Sea Canal side ("lake"): brackish/fresh, level kept slightly below NAP
    "head_lake": -0.40,
    "salinity_lake": 1.0,
    "temperature_lake": 12.0,
    # North Sea side ("sea"): full marine salinity, tidal water level
    "head_sea": 0.0,
    "salinity_sea": 30.0,
    "temperature_sea": 12.0,
}

operational_parameters = {
    "num_cycles": 8,
    "door_time_to_open": 600.0,
    "leveling_time": 900.0,
    "ship_volume_sea_to_lake": 50000.0,
    "ship_volume_lake_to_sea": 50000.0,
}

mean_tide_parameters = {**lock_parameters, **boundary_conditions, **operational_parameters}
low_tide_parameters = {**mean_tide_parameters, "head_sea": -1.0}
high_tide_parameters = {**mean_tide_parameters, "head_sea": 1.0}

print("IJmuiden sea lock, no salt intrusion measures:")

results = pyzsf.zsf_calc_steady(**mean_tide_parameters)
print("Mean tide = {:.1f} kg/s".format(-1 * results["salt_load_lake"]))

results = pyzsf.zsf_calc_steady(**low_tide_parameters)
print("Low tide = {:.1f} kg/s".format(-1 * results["salt_load_lake"]))

results = pyzsf.zsf_calc_steady(**high_tide_parameters)
print("High tide = {:.1f} kg/s".format(-1 * results["salt_load_lake"]))

# Auxiliary results, showing how long the doors are open at mean tide
print("\nDoor open times at mean tide:")
results = pyzsf.zsf_calc_steady(True, **mean_tide_parameters)
for k, v in results.items():
    if k.startswith("t_open"):
        print(f"{k} = {v}")
