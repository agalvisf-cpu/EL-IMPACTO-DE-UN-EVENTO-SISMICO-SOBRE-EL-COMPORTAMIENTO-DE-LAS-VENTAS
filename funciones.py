

SEMANAS = [32, 33, 34]
PERIODOS = {32: "Pre", 33: "Durante", 34: "Post"}
ORDEN = ["Pre", "Durante", "Post"]
ORDEN_PERIODO = ORDEN  


RENOMBRAR = {"cadena": "Cadena",
             "Último Inventario [und]": "Inventario",
             "Inventario [und]": "Inventario"}


COLUMNAS = {"semana": "semana", "periodo": "periodo", "Cadena": "cadena",
            "Tipo_Supermercado": "tipo_supermercado", "Región": "region",
            "GLN Punto de Venta": "punto_venta", "GTIN": "gtin",
            "Proveedor": "proveedor", "Segmento": "familia", "Clase": "categoria",
            "SubCategoria": "subcategoria", "Unidades vendidas": "unidades",
            "Ventas": "ventas", "Inventario": "inventario"}

DIMENSIONES = ["cadena", "tipo_supermercado", "region", "proveedor",
               "familia", "categoria", "subcategoria"]
REGIONES_FOCO = ["PACIFICO", "VALLE", "EJE CAFETERO", "ANTIOQUIA"]
ALFA = 0.05


def cargar_datos(carpeta="data"):
    carpeta = Path(carpeta)
    tablas = []
    for semana in SEMANAS:
        archivos = sorted(carpeta.glob(f"*{semana}*.csv*"))   
        if not archivos:
            raise FileNotFoundError(
                f"No encontre el archivo de la semana {semana} en '{carpeta.resolve()}'. "
                f"Deja los 3 CSV en esa carpeta o pasa la ruta correcta a cargar_datos().")
        df = pd.read_csv(archivos[0], sep=";", encoding="utf-8-sig", dtype=str)
        df = df.rename(columns=RENOMBRAR)
        df["semana"] = semana
        df["periodo"] = PERIODOS[semana]
        tablas.append(df)
    return pd.concat(tablas, ignore_index=True)


def a_numero(serie):
    serie = serie.astype("string").str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(serie, errors="coerce")


def limpiar(datos):
  
    df = datos.rename(columns=COLUMNAS)
    df = df[list(dict.fromkeys(COLUMNAS.values()))].copy()

    df["region"] = df["region"].replace("BOGOTA ", "BOGOTA")
    for col in DIMENSIONES:
        df[col] = df[col].astype("string").str.strip()
    df["region"] = df["region"].str.upper()

    for col in ["unidades", "ventas", "inventario"]:
        df[col] = a_numero(df[col])

    df["ventas"] = df["ventas"].fillna(0)
    df["unidades"] = df["unidades"].fillna(0)

    df = df.drop_duplicates().reset_index(drop=True)
    df["periodo"] = pd.Categorical(df["periodo"], categories=ORDEN, ordered=True)
    return df


def reporte_calidad(bases, limpio):
    vacios = {c: round(float(a_numero(bases[o]).isna().mean() * 100), 1)
              for o, c in [("Ventas", "ventas"), ("Unidades vendidas", "unidades")]}
    cats = limpio.groupby("gtin")["categoria"].nunique()
    consistentes = int((cats == 1).sum())
    return {
        "duplicados_eliminados": len(bases) - len(limpio),
        "ventas_cero_o_sin_venta": int((limpio["ventas"] == 0).sum()),
        "pct_vacios_medida_cruda": vacios,
        "taxonomia_consistente_gtin_%": round(consistentes / len(cats) * 100, 1),
        "gtin_consistentes": f"{consistentes}/{len(cats)}",
        "regiones": limpio["region"].nunique(),
        "familias": limpio["familia"].nunique(),
        "categorias": limpio["categoria"].nunique(),
        "subcategorias": limpio["subcategoria"].nunique(),
    }


def resumen_por_periodo(df):
    r = df.groupby("periodo", observed=True).agg(
        ventas=("ventas", "sum"),
        unidades=("unidades", "sum"),
        inventario_prom=("inventario", "mean")).reindex(ORDEN)
    return r.round(1)


def variacion_vs_pre(resumen, columna):
    base = resumen.loc["Pre", columna]
    out = resumen[[columna]].copy()
    out["var_%_vs_Pre"] = ((out[columna] / base - 1) * 100).round(1)
    return out


def ventas_por_dimension(df, dimension, valor="ventas"):

    t = df.pivot_table(index=dimension, columns="periodo", values=valor,
                       aggfunc="sum", fill_value=0, observed=True).reindex(columns=ORDEN, fill_value=0)
    t["var_Durante_%"] = ((t["Durante"] - t["Pre"]) / t["Pre"].where(t["Pre"] != 0) * 100).round(1)
    t["var_Post_%"] = ((t["Post"] - t["Pre"]) / t["Pre"].where(t["Pre"] != 0) * 100).round(1)
    return t.sort_values("Pre", ascending=False)


def top_movimientos(df, dimension, n=8):
    t = ventas_por_dimension(df, dimension)
    t = t[t["Pre"] >= t["Pre"].median()]
    suben = t.sort_values("var_Durante_%", ascending=False).head(n)
    bajan = t.sort_values("var_Durante_%").head(n)
    return suben, bajan


def analisis_inventario(df):
    inv = df[df["inventario"].notna()].copy()
    inv["agotado"] = inv["inventario"] == 0
    t = inv.groupby("periodo", observed=True).agg(
        inventario_total=("inventario", "sum"),
        tasa_quiebre_pct=("agotado", "mean")).reindex(ORDEN)
    t["tasa_quiebre_pct"] = (t["tasa_quiebre_pct"] * 100).round(1)
    return t


def muestras_por_periodo(df, valor="ventas"):
    t = df.pivot_table(index=["region", "categoria"], columns="periodo", values=valor,
                       aggfunc="sum", fill_value=0, observed=True).reindex(columns=ORDEN, fill_value=0)
    return [t[p].to_numpy(dtype=float) for p in ORDEN]


def anova(df, valor="ventas"):
    grupos = muestras_por_periodo(df, valor)
    f, p = stats.f_oneway(*grupos)
    _, p_levene = stats.levene(*grupos)          
    _, p_kruskal = stats.kruskal(*grupos)        
    _, p_friedman = stats.friedmanchisquare(*grupos) 
    return {"valor": valor, "n_por_grupo": len(grupos[0]),
            "F": round(float(f), 3), "p_value": float(p),
            "eta2": round(float(_eta(grupos)), 4),
            "levene_p": float(p_levene), "kruskal_p": float(p_kruskal),
            "friedman_p": float(p_friedman), "rechaza_H0": bool(p < ALFA)}


def _eta(grupos):
    todos = np.concatenate(grupos)
    ss_total = ((todos - todos.mean()) ** 2).sum()
    ss_entre = sum(len(g) * (g.mean() - todos.mean()) ** 2 for g in grupos)
    return ss_entre / ss_total if ss_total else 0


def anova_regiones(df, valor="ventas", regiones=REGIONES_FOCO):
    return anova(df[df["region"].isin(regiones)], valor)
