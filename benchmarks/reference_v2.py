"""Independent Decimal/SI reference, separate from production science functions."""

import copy
import math
from decimal import Decimal, localcontext


def sigma_decimal(raw: dict, t: float, suffix: str = "") -> str:
    with localcontext() as ctx:
        ctx.prec = 60
        temperature = Decimal(str(t))
        ea_j = Decimal(raw["Ea" + suffix]) * Decimal("0.001") * Decimal("1.602176634e-19")
        return str(
            Decimal(raw["A" + suffix])
            / temperature
            * (-ea_j / (Decimal("1.380649e-23") * temperature)).exp()
        )


def root_decimal(left, right, ls="", rs="") -> str:
    with localcontext() as ctx:
        ctx.prec = 60
        energy = (
            (Decimal(left["Ea" + ls]) - Decimal(right["Ea" + rs]))
            * Decimal("0.001")
            * Decimal("1.602176634e-19")
        )
        log_a = Decimal(left["A" + ls]).ln() - Decimal(right["A" + rs]).ln()
        return str(energy / (Decimal("1.380649e-23") * log_a))


def synthetic_pair(repository, scenario):
    """SYNTHETIC_TEST_ONLY; explicit counterexamples, never a discovery demo."""
    repo = copy.copy(repository)
    records = []
    for row_id in [1, 2]:
        record = repository.by_id[row_id].model_copy(deep=True)
        record.formula = "SYNTHETIC_TEST_ONLY_" + str(row_id)
        record.raw.update(
            Formula=record.formula, Ea="500", A="100000", EaHT="", AHT="", **{"T*": ""}
        )
        if row_id == 2:
            if scenario == "discontinuity":
                record.raw.update(A="50000", EaHT="500", AHT="200000", **{"T*": "800"})
            else:
                root = 1400 if scenario == "outside" else 800
                record.raw.update(
                    Ea="600",
                    A=str(100000 * math.exp(0.1 / ((1.380649e-23 / 1.602176634e-19) * root))),
                )
        records.append(record)
    repo.records = records
    repo.by_id = {r.row_id: r for r in records}
    return repo
