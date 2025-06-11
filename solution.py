# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo[sql]",
#     "matplotlib==3.10.3",
#     "numpy==2.2.6",
#     "polars[pyarrow]==1.30.0",
# ]
# ///

import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Kolokwium NWP - 10.06.2025 - zadanie z SQL

    W podkatalogu `data` mamy trzy pliki z danymi, których strukturę i zawartość można poznać na podstawie początkowych komórek notatnika. Dwa pliki dotyczą wyników pierwszej tury wyborów prezydenckich z bieżącego (2025) roku (źródło: portal Państwowej Komisji Wyborczej), a jeden - demografii Polski w rozbiciu na powiaty wg. stanu z 2023 roku (nowszych danych GUS nie ma).

    Opisowo: 

    * `kandydaci2025.parquet` to lista kandydatów, ich dane oraz całkowita liczba głosów i procent głosów ważnych jakie każdy z nich uzyskał
    * `demografia2023.parquet` zawiera dla każdego powiatu, opisanego jego kodem TERYT (unikalny identyfikator), jego liczbę ludności (w tysiącach) oraz gęstość zaludnienia (osoby/km<sup>2</sup>) wg. stanu z 2023 roku
    * `wyniki2025.parquet` to wyniki głosowania w pierwszej turze wyborów w rozbiciu na powiaty. Powiaty identyfikują kody TERYT, a kandydatów ich numery na liście kandydatów. **Dane odnoszące się do "kandydata" o numerze zero są to całkowite liczby głosów ważnych oddanych w danym powiecie**.

    Dla ilustracji przedstawiłem poniżej wyniki głosowania na poszczególnych kandydatów na poziomie całego kraju za pomocą dwóch różnych typów wykresów.

    Przedmiotem zadania jest przedstawienie w kolejnych komórkach notatnika wyników głosowania na dwóch czołowych kandydatów w podziale na powiaty, w zależności od gęstości zaludnienia powiatu. To znaczy, produktem końcowym powinny być dwa scatter ploty, pokazujące procent głosów oddanych na kandydata w zależności od gęstości zaludnienia, z jednym punktem na każdy powiat, i skalą logarytmiczną na osi `X`. Dane do stworzenia tych wykresów należy uzyskać za pomocą zapytań SQL na dostarczonych plikach danych.
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import polars as pl
    return mo, pl, plt


@app.cell
def _(pl):
    demografia = pl.read_parquet("data/demografia2023.parquet")
    kandydaci = pl.read_parquet("data/kandydaci2025.parquet")
    wyniki = pl.read_parquet("data/wyniki2025.parquet")
    return demografia, kandydaci, wyniki


@app.cell
def _(kandydaci, mo):
    _ = mo.sql(
        f"""
        select * from kandydaci;
        """
    )
    return


@app.cell
def _(demografia, mo):
    _ = mo.sql(
        f"""
        select * from demografia;
        """
    )
    return


@app.cell
def _(mo, wyniki):
    _ = mo.sql(
        f"""
        select * from wyniki;
        """
    )
    return


@app.cell(hide_code=True)
def _(kandydaci, mo, plt):
    wyniki_ogolne = mo.sql("""
    select 
        "Procent głosów", 
        split("Nazwisko i imiona", ' ')[-1] as "Nazwisko",
    from kandydaci
    order by "Procent głosów" desc;
    """)

    fig1, ax1 = plt.subplots()
    ax1.bar("Nazwisko", "Procent głosów", label="Nazwisko", data=wyniki_ogolne, color=plt.cm.tab20.colors)
    plt.setp(
        ax1.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor"
    )
    plt.title("Procent głosów na poszczególnych kandydatów")
    plt.legend([f"{w}: {p}%" for (p, w) in wyniki_ogolne.rows()], loc="upper right")
    plt.tight_layout()
    plt.gca()
    return (wyniki_ogolne,)


@app.cell(hide_code=True)
def _(plt, wyniki_ogolne):
    fig2, ax2 = plt.subplots()
    _pie_labels = [f"{w}:\n{p}%" if p > 4 else None for (p, w) in wyniki_ogolne.rows()]
    _legend = [f"{w}: {p}%" for (p, w) in wyniki_ogolne.rows()]
    ax2.pie("Procent głosów", labels=_pie_labels, data=wyniki_ogolne, colors=plt.cm.tab20.colors)
    plt.title("Procent głosów na poszczególnych kandydatów")
    plt.legend(_legend, loc="upper right", bbox_to_anchor=(1.7, 1))
    plt.tight_layout()
    plt.gca()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Poniżej proszę stworzyć komórki z kodem wypełniającym polecenie zadania""")
    return


@app.cell
def _(mo):
    procenty = mo.sql(
        f"""
        with
            t1 as (
                select
                    demografia.*,
                    Kandydat,
                    "Liczba głosów"
                from
                    demografia
                    join wyniki using ("TERYT Powiatu")
                where
                    Kandydat in (0, 8, 11)
            ),
            t2 as (
                pivot t1 on Kandydat using first("Liczba głosów")
            )
        select
            "Osób/km^2",
            "Osób (tys.)",
            100.0 * "8" / "0" as Nawrocki,
            100.0 * "11" / "0" as Trzaskowski
        from
            t2;
        """
    )
    return (procenty,)


@app.cell
def _(plt, procenty):
    _fig, (_ax1, _ax2) = plt.subplots(1, 2, sharey=True, figsize=(12, 5))
    _ax1.scatter(
        "Osób/km^2", "Nawrocki", data=procenty, s=procenty["Osób (tys.)"] / 6
    )
    _ax1.set_xscale("log")
    _ax1.set_title("Nawrocki")
    _ax1.grid()
    _ax1.set_ylabel("Procent głosów")
    _ax1.set_xlabel("Osób/km^2")
    _ax2.scatter(
        "Osób/km^2", "Trzaskowski", data=procenty, s=procenty["Osób (tys.)"] / 6, color="r"
    )
    _ax2.set_xscale("log")
    _ax2.set_title("Trzaskowski")
    _ax2.grid()
    _ax2.set_xlabel("Osób/km^2")
    _fig.suptitle("Wyniki 1. tury wyborów 2025 w podziale na powiaty, w zależności od gęstości zaludnienia")
    _fig
    return


if __name__ == "__main__":
    app.run()
