import pandas as pd

def find_cancelling_pairs(df):

    # Separate positive and negative transactions
    pos = df[df["Monto"] > 0].copy()
    neg = df[df["Monto"] < 0].copy()

    # Make amounts comparable
    neg["Monto"] = -neg["Monto"]

    # Sort to ensure consistent pairing
    pos = pos.sort_values("Fecha y hora", ascending=True)
    neg = neg.sort_values("Fecha y hora", ascending=True)

    # Assign group numbers
    pos["pair_id"] = pos.groupby(["Monto", "ID orden"]).cumcount()
    neg["pair_id"] = neg.groupby(["Monto", "ID orden"]).cumcount()

    # Merge pairs
    pairs = pos.merge(
        neg,
        on=["Monto", "ID orden", "pair_id"],
        suffixes=("_pos", "_neg")
    )

    matched_ids = set(pairs["ID transacción_pos"]) | set(pairs["ID transacción_neg"])
    unmatched = df[~df["ID transacción"].isin(matched_ids)]
    matched = df[df["ID transacción"].isin(matched_ids)]

    return unmatched, matched

def clean_table(table):
    table['Monto'] = -pd.to_numeric(table['Monto'],errors='coerce')
    table['Fecha y hora'] = pd.to_datetime(table['Fecha y hora'],errors='coerce')
    table, _ = find_cancelling_pairs(table)
    table = table[table['Monto']>=0]

    return table