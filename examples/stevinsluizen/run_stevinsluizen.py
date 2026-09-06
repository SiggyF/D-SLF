from pathlib import Path
import pprint
import click
import pandas as pd
import pyzsf


DEFAULT_DIR = Path(__file__).parent


def run_scenario(
    csv_path: Path,
    lock_length: float,
    lock_width: float,
    lock_bottom: float,
    sill_height: float,
    salinity_lake: float,
    salinity_sea: float,
    temperature_lake: float,
    temperature_sea: float,
) -> tuple[dict, pd.DataFrame]:
    df_lockages = pd.read_csv(csv_path)

    lock_parameters = {
        "lock_length": lock_length,
        "lock_width": lock_width,
        "lock_bottom": lock_bottom,
        "sill_height_lake": sill_height,
        "sill_height_sea": sill_height,
    }

    boundary_conditions = {
        "head_lake": 0.0,
        "salinity_lake": salinity_lake,
        "salinity_sea": salinity_sea,
        "temperature_lake": temperature_lake,
        "temperature_sea": temperature_sea,
    }

    z = pyzsf.ZSFUnsteady(15.0, 0.0, **lock_parameters, **boundary_conditions)

    all_results = []
    times = []

    for _, row in df_lockages.iterrows():
        routine = int(row["routine"])
        params = {}
        if pd.notna(row["head_sea"]):
            params["head_sea"] = float(row["head_sea"])
        if pd.notna(row["ship_volume_lake_to_sea"]):
            params["ship_volume_lake_to_sea"] = float(row["ship_volume_lake_to_sea"])
        if pd.notna(row["ship_volume_sea_to_lake"]):
            params["ship_volume_sea_to_lake"] = float(row["ship_volume_sea_to_lake"])

        if routine == 1:
            step_res = z.step_phase_1(float(row["t_level"]), **params)
        elif routine == 2:
            if pd.isna(row["t_open_lake"]):
                continue
            step_res = z.step_phase_2(float(row["t_open_lake"]), **params)
        elif routine == 3:
            step_res = z.step_phase_3(float(row["t_level"]), **params)
        elif routine == 4:
            if pd.isna(row["t_open_sea"]):
                continue
            step_res = z.step_phase_4(float(row["t_open_sea"]), **params)
        else:
            raise ValueError(f"Unsupported routine {routine}")

        times.append(float(row["time"]))
        all_results.append(step_res)

    duration = times[-1] - times[0]

    overall_results = {}
    overall_mass_to_sea = 0.0
    overall_mass_to_lake = 0.0

    for results in all_results:
        for k, v in results.items():
            if k.startswith(("volume_", "mass_")):
                overall_results[k] = overall_results.get(k, 0.0) + v

        overall_mass_to_sea += results["volume_to_sea"] * results["salinity_to_sea"]
        overall_mass_to_lake += results["volume_to_lake"] * results["salinity_to_lake"]

    overall_results["salinity_to_sea"] = (
        overall_mass_to_sea / overall_results["volume_to_sea"]
    )
    overall_results["salinity_to_lake"] = (
        overall_mass_to_lake / overall_results["volume_to_lake"]
    )

    overall_discharges = {}
    for k, v in overall_results.items():
        if k.startswith("volume_"):
            overall_discharges[f"discharge_{k[7:]}"] = v / duration
        if k.startswith("mass_"):
            overall_discharges[f"flux_{k[5:]}"] = v / duration
    overall_results.update(overall_discharges)
    overall_results["duration_days"] = duration / 86400.0
    overall_results["total_steps"] = len(all_results)

    return overall_results, pd.DataFrame(all_results)


@click.command()
@click.option(
    "--scenario",
    type=click.Choice(["2023", "2050hsk", "2050lvk", "all"]),
    default="2023",
    show_default=True,
    help="BIVAS scenario to simulate.",
)
@click.option(
    "--data-dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_DIR,
    show_default=True,
    help="Directory containing the CSV lockage datasets.",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_DIR / "output",
    show_default=True,
    help="Directory to store simulation output files.",
)
@click.option(
    "--lock-length",
    type=float,
    default=120.0,
    show_default=True,
    help="Lock chamber length in meters (Stevinsluis: 120 m).",
)
@click.option(
    "--lock-width",
    type=float,
    default=13.5,
    show_default=True,
    help="Lock chamber width in meters (Stevinsluis: 13.5 m).",
)
@click.option(
    "--lock-bottom",
    type=float,
    default=-4.0,
    show_default=True,
    help="Lock bottom level in m NAP.",
)
@click.option(
    "--sill-height",
    type=float,
    default=0.5,
    show_default=True,
    help="Sill height above lock bottom in meters (sill at -3.5 m NAP).",
)
@click.option(
    "--salinity-lake",
    type=float,
    default=1.0,
    show_default=True,
    help="Salinity on lake side (IJsselmeer) in kg/m³.",
)
@click.option(
    "--salinity-sea",
    type=float,
    default=28.0,
    show_default=True,
    help="Salinity on sea side (Waddenzee) in kg/m³.",
)
@click.option(
    "--temperature",
    type=float,
    default=15.0,
    show_default=True,
    help="Water temperature in degrees Celsius.",
)
def main(
    scenario: str,
    data_dir: Path,
    output_dir: Path,
    lock_length: float,
    lock_width: float,
    lock_bottom: float,
    sill_height: float,
    salinity_lake: float,
    salinity_sea: float,
    temperature: float,
):
    """Run unsteady D-SLF simulation for Stevinsluizen lockages."""
    output_dir.mkdir(parents=True, exist_ok=True)

    available_scenarios = {
        "2023": data_dir / "lockages_bivas_2023.csv",
        "2050hsk": data_dir / "lockages_bivas_2050hsk.csv",
        "2050lvk": data_dir / "lockages_bivas_2050lvk.csv",
    }

    selected = (
        list(available_scenarios.keys()) if scenario == "all" else [scenario]
    )

    summary_rows = []

    for name in selected:
        csv_file = available_scenarios[name]
        click.echo("=" * 60)
        click.echo(f"Running Stevinsluizen simulation: Scenario {name}")
        click.echo(f"Data file: {csv_file}")
        click.echo("=" * 60)

        overall, df_results = run_scenario(
            csv_path=csv_file,
            lock_length=lock_length,
            lock_width=lock_width,
            lock_bottom=lock_bottom,
            sill_height=sill_height,
            salinity_lake=salinity_lake,
            salinity_sea=salinity_sea,
            temperature_lake=temperature,
            temperature_sea=temperature,
        )

        results_csv = output_dir / f"results_stevinsluizen_{name}.csv"
        df_results.to_csv(results_csv, index=False)
        click.echo(f"Per-step results saved to: {results_csv}")

        row = {"scenario": name, **overall}
        summary_rows.append(row)

        click.echo("\nAnnual Aggregates and Averages:")
        pprint.pprint(overall)

    df_summary = pd.DataFrame(summary_rows)
    summary_path = output_dir / "summary_scenarios.csv"
    df_summary.to_csv(summary_path, index=False)
    click.echo(f"\nScenario summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
