import streamlit as st
from datetime import date, timedelta
from revenue import (
    CONFIG, validate_num_from_txt, trip_fmt, rev_fmt,
    get_credentials, import_sql_table, fill_fees_query,
    clean_table,
    calc_revenues, calc_trips
)

server_name, database_name = get_credentials()

### FUNCIÓN PARA GUARDAR DATOS IMPORTADOS EN CACHE
@st.cache_data
def load_clean_data(ciudades,fecha_min,fecha_max):

    data = {}
    for ciudad in ciudades:
        query_fees = fill_fees_query(database_name,ciudad,fecha_min,fecha_max)
        data[ciudad] = import_sql_table(server_name,database_name,query_fees)

    for ciudad, table in data.items():
        table = clean_table(table)
        d_max = table['Fecha y hora'].max()
        d_min = table['Fecha y hora'].min()
        period = (date(d_max.year, d_max.month, d_max.day) - date(d_min.year, d_min.month, d_min.day)).days + 1
        ending = 's' if period > 1 else ''
        st.write(f"Datos de {ciudad} imporatdos. Periodo abarca {period} día{ending}.")
        print(f"Datos de {ciudad} imporatdos. Periodo abarca {period} día{ending}.")

    return data


### APP COMIENZA AQUÍ ####################################################################################

st.title("Taxi Revenue Forecast")

st.write("Welcome to the revenue and trip forecast simulator.")

if "clean_data" not in st.session_state:
    st.session_state.clean_data = None

### BARRA LATERAL PARA INGRESAR PARÁMETROS ####################################################################################

with st.sidebar:

    st.header("Adjust Simulation Settings")

    ciudades = st.multiselect(
        "Cities",
        CONFIG["ciudades"],
        default=[CONFIG["ciudades"][0]]
    )

    fecha_min = st.date_input(
        "Start date",
        min_value=date.today()-timedelta(days=90),
        max_value=date.today(),
        value=date.today()-timedelta(days=30)
    )

    fecha_max = st.date_input(
        "End date",
        min_value=fecha_min,
        max_value=date.today(),
        value=date.today()
    ) + timedelta(days=1)

    igv = st.number_input(
        "IGV",
        min_value=0.0,
        max_value=1.0,
        value=0.18,
        step=0.01
    )

    ### IMPORTAR DATOS HISTÓRICOS
    if st.button("Import & Clean Data"):
        with st.spinner("Loading historical data..."):
            st.session_state.clean_data = load_clean_data(ciudades,fecha_min,fecha_max)

    #### REVISAR SI LOS DATOS HAN SIDO CARGADOS
    st.header("Load historical data")

    if st.session_state.clean_data is None:
        st.warning("Status: No data loaded.")
    else:
        st.success("Status: Data is ready.")



### SIMULAR NÚMERO DESEADO DE VIAJES ####################################################################################
st.header("1. Revenue simulator")

trip_text = st.text_input(
    "Enter the target number(s) of trips:",
    "100,250,500"
)
trip_targets, error1 = validate_num_from_txt(trip_text,dtype=int,ll=1,ul=1000)
if error1 is not None:
    st.error(error1)

# ### CORRER SIMULACIONES Y MOSTRAR RESUMEN DE RESULTADOS
sim_revenues = st.button(
    "Simulate revenues",
    disabled = (st.session_state.clean_data is None) or (trip_targets is None)
)

if sim_revenues:

    with st.spinner("Running simulations..."):
        results = calc_revenues(st.session_state.clean_data,trip_targets,ciudades,CONFIG['percentiles'])

    for ciudad, resumen in results.items():
        st.write(f'Resumen de simulaciones para {ciudad}, ingreso esperado por comisiones:')
        st.dataframe(resumen.style.format(rev_fmt)
        )
        # st.line_chart(results[ciudad].loc[:,'media'])


### SIMULAR GANANCIAS DESEADAS ####################################################################################
st.header("2. Trip simulator")

revenue_text = st.text_input(
    "Enter target revenues:",
    "25,50,75"
)
revenue_targets, error2 = validate_num_from_txt(revenue_text,dtype=float,ll=1,ul=500)
if error2 is not None:
    st.error(error2)
if revenue_targets is not None:
    revenue_targets_igv = (revenue_targets * (1 + igv)).round(2)
else:
    revenue_targets_igv = None

### CORRER SIMULACIONES Y MOSTRAR RESUMEN DE RESULTADOS
sim_trips = st.button(
    "Simulate trips",
    disabled = (st.session_state.clean_data is None) or (revenue_targets_igv is None)
)
if sim_trips:
    
    with st.spinner("Running simulations..."):
        results = calc_trips(st.session_state.clean_data,revenue_targets_igv,ciudades,CONFIG['percentiles'])

    for ciudad, resumen in results.items():
        st.write(f'Resumen de simulaciones para {ciudad}, número de viajes necesarios por meta (con IGV de {igv:.0%}):')
        st.dataframe(resumen.style.format(trip_fmt)
        )
        # st.line_chart(results[ciudad].loc[:,'media'])