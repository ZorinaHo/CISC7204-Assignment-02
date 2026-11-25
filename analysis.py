"""Reproduce selected recession comparisons from the automobile-sales assignment."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


SOURCE = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=SOURCE, help="IBM CSV URL or the local assignment reference CSV")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "visualizations")
    args = parser.parse_args()
    sales = pd.read_csv(args.input, usecols=["Year", "Recession", "Automobile_Sales", "Vehicle_Type"])
    annual = sales.groupby("Year")["Automobile_Sales"].mean()
    period = sales.groupby("Recession")["Automobile_Sales"].agg(["size", "mean"])
    by_type = sales.groupby(["Vehicle_Type", "Recession"])["Automobile_Sales"].mean().unstack()
    by_type = by_type.rename(columns={0: "Non-recession", 1: "Recession"})
    by_type = by_type.rename(index={
        "Executivecar": "Executive car", "Mediumfamilycar": "Medium family car",
        "Smallfamiliycar": "Small family car", "Sports": "Sports car", "Supperminicar": "Supermini",
    })

    print(f"Records: {len(sales):,}. Years: {annual.index.min()}-{annual.index.max()}.")
    print(period.round(2).to_string())
    print(f"Highest annual mean: {annual.idxmax()} ({annual.max():,.2f} units per record).")
    print(by_type.round(2).to_string())

    args.output.mkdir(parents=True, exist_ok=True)
    figure, ax = plt.subplots(figsize=(8.4, 4.5), layout="constrained")
    annual.plot(ax=ax, color="#146877", marker="o", markersize=3)
    ax.set_title("Average automobile sales by year", loc="left", fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean sales (vehicles per record)")
    ax.grid(axis="y", alpha=.25)
    figure.savefig(args.output / "annual-sales.png", dpi=160)
    plt.close(figure)

    figure, ax = plt.subplots(figsize=(8.4, 4.5), layout="constrained")
    by_type.plot.barh(ax=ax, color=["#146877", "#a44f2b"], width=.75)
    ax.set_title("Average sales by vehicle type and recession status", loc="left", fontweight="bold")
    ax.set_xlabel("Mean sales (vehicles per record)")
    ax.set_ylabel("Vehicle type")
    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.16), ncols=2, frameon=False)
    ax.grid(axis="x", alpha=.25)
    figure.savefig(args.output / "sales-by-vehicle-type.png", dpi=160)
    plt.close(figure)


if __name__ == "__main__":
    main()
