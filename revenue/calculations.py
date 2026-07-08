import numpy as np
import pandas as pd
from scipy.stats import lognorm

def calc_revenues(data,trip_targets,ciudades,percentiles,num_sims=100_000,method='bootstrap',rng=np.random.default_rng()):
    sim_tables = {}
    resumenes={}
    for ciudad in ciudades:
        fees = data[ciudad]['Monto']
        if method == 'lognorm':
            shape, loc, scale = lognorm.fit(fees, floc=0)
        sims = pd.DataFrame({})
        for trips in trip_targets:
            # print(f'Simulando {trips} viajes en {ciudad}')
            
            if method == 'bootstrap':
                sample = rng.choice(
                    fees,
                    size=(trips,num_sims),
                    replace=True
                    )
            elif method == 'lognorm':
                sample = lognorm.rvs(
                    s=shape,
                    loc=loc,
                    scale=scale,
                    size=(trips,num_sims)
                    )
            totals = sample.sum(axis=0)
            sims[f'{trips}'] = totals
        sim_tables[ciudad] = sims
        resumenes[ciudad] = sims.describe(percentiles=percentiles).rename(index={'mean':'media','std':'desv'}).drop(index=['count','min','max']).T.rename_axis('Num viajes')

    return resumenes


def calc_trips(data,revenue_targets,ciudades,percentiles,num_sims=10_000,rng=np.random.default_rng()):
    sim_tables = {}
    resumenes={}
    for ciudad in ciudades:
        fees = data[ciudad]['Monto']
        sims = pd.DataFrame({})
        for target in revenue_targets:
            # print(f'Simulando viajes para meta de {target} soles en {ciudad}')

            n_exp = target/np.mean(fees)
            n_max = int(np.ceil(1.3*n_exp))
            # print(f'\t Esperado: {n_exp:.2f} viajes; simulando {n_max} viajes')

            samples = rng.choice(
                fees,
                size=(num_sims, n_max),
                replace=True
            )
            cumulative = samples.cumsum(axis=1)
            trip_counts = (
                cumulative >= target
            ).argmax(axis=1) + 1
            sims[f'S/ {target}'] = trip_counts
        sim_tables[ciudad] = sims
        resumenes[ciudad] = sims.describe(percentiles=percentiles).rename(index={'mean':'media','std':'desv'}).drop(index=['count','min','max']).T.rename_axis('Meta de ganancias')
    
    return resumenes