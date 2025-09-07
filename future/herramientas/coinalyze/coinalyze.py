def coinalyze():
    from playwright.sync_api import sync_playwright
    import pandas as pd
    try:
        with sync_playwright() as p:
            # Inicia navegador (abre Chrome/Chromium)
            navegador = p.firefox.launch(headless=True)  # headless=False para ver lo que hace
            pagina = navegador.new_page()

            for i in range(2):
                if i == 0:
                    tipo = "desc"
                if i == 1:
                    tipo = "asc"
                # Abre tu página
                pagina.goto(f"https://es.coinalyze.net/?order_by=oi_24h_pchange&order_dir={tipo}", wait_until="load")

                # Imprimir texto
                texto = pagina.locator("div.table-wrapper").locator("tbody").inner_text()
                #print(texto)
                
                # Organizar los datos
                datos = []
                for linea in texto.splitlines():
                    if linea != "":
                        linea_lista = []
                        for dato in linea.split('\t'):
                            if dato != "":
                                linea_lista.append(dato)
                        datos.append(linea_lista)
                #print(datos)

                # Definir las columnas
                cols = [
                "MONEDA", "PRECIO", "CHG 24H", "MKT CAP", "VOL 24H", "OPEN INTEREST",
                "OI CHG 24H", "OI SHARE", "OI/VOL24H", "FR AVG", "PFR AVG", "LIQS. 24H"
                ]
                        
                # Crear DataFrame
                df = pd.DataFrame(datos, columns=cols)
                if i == 0:
                    df_desc = df
                if i == 1:
                    df_asc = df
            
            # Cerrar el navegador
            #navegador.close()
            
            # Buscar monedas
            df_oi_desc = df_desc[((df_desc["OPEN INTEREST"].str.contains("m")) | (df_desc["OPEN INTEREST"].str.contains("b"))) &
                            ((df_desc["OPEN INTEREST"].str.extract(r"\$([\d\.]+)m").astype(float)[0] > 10) | (df_desc["OPEN INTEREST"].str.contains("b"))) &
                            ((df_desc["VOL 24H"].str.extract(r"\$([\d\.]+)m").astype(float)[0] > 100) | (df_desc["VOL 24H"].str.contains("b")))]
            df_oi_asc = df_asc[((df_asc["OPEN INTEREST"].str.contains("m")) | (df_asc["OPEN INTEREST"].str.contains("b"))) &
                            ((df_asc["OPEN INTEREST"].str.extract(r"\$([\d\.]+)m").astype(float)[0] > 10) | (df_asc["OPEN INTEREST"].str.contains("b"))) &
                            ((df_asc["VOL 24H"].str.extract(r"\$([\d\.]+)m").astype(float)[0] > 100) | (df_asc["VOL 24H"].str.contains("b")))]

            return(df_oi_desc,df_oi_asc)
        
    except Exception as e:
        print(f"\nERROR EN LA FUNCION coinalyze()\n{e}")

oi = coinalyze()
print(oi[0])
print(oi[1])