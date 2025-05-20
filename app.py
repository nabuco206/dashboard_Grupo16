import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout='wide', initial_sidebar_state='expanded')
sns.set_style("whitegrid")

st.title("Análisis de Ventas y Clientes")

# Cargar CSV
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# Se definen los filtros que tendra el dashboard
st.sidebar.header("Filtros")
ciudad = st.sidebar.multiselect("Selecciona Ciudad", options=df["City"].unique(), default=df["City"].unique())
genero = st.sidebar.multiselect("Selecciona Género", options=df["Gender"].unique(), default=df["Gender"].unique())
tipo_cliente = st.sidebar.multiselect("Tipo de Cliente", options=df["Customer type"].unique(), default=df["Customer type"].unique())
Payment = st.sidebar.multiselect("Método de Pago", options=df["Payment"].unique(), default=df["Payment"].unique())

# Filtro por fecha
fecha_min = df["Date"].min()
fecha_max = df["Date"].max()
rango_fecha = st.sidebar.date_input("Rango de fechas", [fecha_min, fecha_max])

# Aplicar filtros en el df
df_filtrado = df[
    (df["City"].isin(ciudad)) &
    (df["Gender"].isin(genero)) &
    (df["Customer type"].isin(tipo_cliente)) &
    (df["Date"] >= pd.to_datetime(rango_fecha[0])) &
    (df["Date"] <= pd.to_datetime(rango_fecha[1])) &
    (df["Payment"].isin(Payment))
]

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📄 Datos Generales", 
    "📈 Ventas por Fecha", 
    "📊 Ingresos por Línea de Producto",
    "⭐ Calificaciones de Clientes",
    "💰 Gasto Total: Member vs Normal",
    "💳 Método de Pago",
    "📉 Costo vs Ganancia",
    "📊 Correlación Numérica",
    "🏬 Ingreso Bruto por Sucursal y Producto",
    "🕒 Horarios de Venta"
])

with tab1:
    st.subheader("Vista previa de los datos")
    st.dataframe(df_filtrado.head())

    st.subheader("Estadísticas generales")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Ventas", f"${df_filtrado['Total'].sum():,.2f}")
    col2.metric("Promedio por compra", f"${df_filtrado['Total'].mean():,.2f}")
    col3.metric("Unidades vendidas", int(df_filtrado["Quantity"].sum()))

    col4, col5, col6 = st.columns(3)
    col4.metric("Total Impuesto Pagado (5%)", f"${df_filtrado['Tax 5%'].sum():,.2f}")
    col5.metric("Costo Total (COGS)", f"${df_filtrado['cogs'].sum():,.2f}")
    col6.metric("Ingreso Bruto Total", f"${df_filtrado['gross income'].sum():,.2f}")

    # df.describe()
    st.subheader("DF Descripción")
    st.dataframe(df_filtrado.describe())


    st.subheader("Resumen por Línea de Producto")
    
    resumen_producto = df_filtrado.groupby("Product line").agg(
        Cantidad_Vendida=("Quantity", "sum"),
        Total_Ventas=("Total", "sum")
    ).sort_values(by="Total_Ventas", ascending=False)

    st.dataframe(resumen_producto.style.format({"Total_Ventas": "${:,.2f}"}))






with tab2:
    st.subheader("1.- Evolución de las Ventas Totales")
    ventas_por_fecha = df_filtrado.groupby('Date')['Total'].sum().reset_index()
    st.line_chart(ventas_por_fecha.set_index('Date'))

with tab3:
    st.subheader("2.- Ingresos por Línea de Producto")
    ingresos_producto = df_filtrado.groupby("Product line")["Total"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=ingresos_producto.values, y=ingresos_producto.index, palette="viridis", ax=ax)
    ax.set_xlabel("Total Ingresos")
    ax.set_ylabel("Línea de Producto")
    ax.set_title("Total de Ingresos por Línea de Producto")
    st.pyplot(fig)

with tab4:
    st.subheader("3 Distribución de Calificaciones de los Clientes")

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df_filtrado["Rating"], bins=20, kde=True, color='skyblue', ax=ax)
    ax.set_title("Distribución de Calificaciones")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Frecuencia")
    st.pyplot(fig)  

with tab5:
    st.subheader("4 Comparación del Gasto Total entre Clientes Member y Normal")

    fig, ax = plt.subplots(figsize=(6, 3))
    sns.boxplot(data=df_filtrado, x="Customer type", y="Total", palette="Set2", ax=ax)
    ax.set_title("Distribución del Gasto Total por Tipo de Cliente")
    ax.set_xlabel("Tipo de Cliente")
    ax.set_ylabel("Gasto Total")
    st.pyplot(fig)

with tab6:
    st.subheader("6 Distribución de Ventas por Método de Pago")

    pagos = df_filtrado.groupby("Payment")["Total"].sum()
    labels = pagos.index
    valores = pagos.values

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(valores, labels=labels, autopct="%1.1f%%", startangle=90, colors=sns.color_palette("pastel"))
    ax.axis("equal") 
    st.pyplot(fig)

with tab7:
    st.subheader("5.- Relación entre Costo (COGS) y Ganancia Bruta")

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=df_filtrado, x="cogs", y="gross income", hue="Product line", palette="tab10", ax=ax)
    ax.set_title("Relación entre Costo y Ganancia Bruta")
    ax.set_xlabel("Costo de Bienes Vendidos (COGS)")
    ax.set_ylabel("Ganancia Bruta")
    st.pyplot(fig)    

with tab8:
    st.subheader("7.- Análisis de Correlación entre Variables Numéricas")


    columnas_numericas = ["Unit price", "Quantity", "Tax 5%", "Total", "cogs", "gross income", "Rating"]
    corr = df_filtrado[columnas_numericas].corr()

    # Heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, ax=ax)
    ax.set_title("Matriz de Correlación")
    st.pyplot(fig)    

with tab9:
    st.subheader("8.- Composición del Ingreso Bruto por Sucursal y Línea de Producto")

    # Agrupar datos por Branch y Product line
    ingreso_composicion = df_filtrado.groupby(["Branch", "Product line"])["gross income"].sum().unstack().fillna(0)

    # Crear gráfico de barras apiladas
    fig, ax = plt.subplots(figsize=(10, 6))
    ingreso_composicion.plot(kind="bar", stacked=True, ax=ax, colormap="tab20c")
    ax.set_title("Ingreso Bruto por Sucursal y Línea de Producto")
    ax.set_xlabel("Sucursal (Branch)")
    ax.set_ylabel("Ingreso Bruto")
    ax.legend(title="Product Line", bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)   

with tab10:
    st.subheader("Análisis de Horarios de Venta")

    # Extraer la hora
    df_filtrado["Hora"] = pd.to_datetime(df_filtrado["Time"]).dt.hour

    # Agrupar por hora y sumar ventas
    ventas_por_hora = df_filtrado.groupby("Hora")["Total"].sum().reset_index()

    # Crear gráfico
    fig, ax = plt.subplots(figsize=(10, 4))
    cmap = sns.color_palette("Reds", as_cmap=True)
    colores = sns.color_palette("Reds", len(ventas_por_hora))

    sns.barplot(data=ventas_por_hora, x="Hora", y="Total", palette=colores, ax=ax)
    ax.set_title("Ventas Totales por Hora del Día")
    ax.set_xlabel("Hora del Día (24h)")
    ax.set_ylabel("Ventas Totales")
    st.pyplot(fig)


    st.subheader("Tabla Resumen de Ventas por Hora")
    ventas_por_hora_tabla = ventas_por_hora.copy()
    ventas_por_hora_tabla["Total"] = ventas_por_hora_tabla["Total"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(ventas_por_hora_tabla)

