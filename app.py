import streamlit as st
from apify_client import ApifyClient

# Campo de entrada para el API token de Apify
st.title("Buscador con Apify y Streamlit")
st.write("Ingrese su token de API de Apify para utilizar la aplicación:")
api_token = st.text_input("API Token de Apify", type="password")

# Función para realizar la consulta en la API de Apify
def search_query(keyword, api_token):
    # Inicializa el cliente de Apify con el token proporcionado
    client = ApifyClient(api_token)
    
    # Prepara la entrada para el Actor de Apify
    run_input = {
        "queries": keyword,
        "resultsPerPage": 10,
        "maxPagesPerQuery": 1,
        "languageCode": "",
        "mobileResults": False,
        "includeUnfilteredResults": False,
        "saveHtml": False,
        "saveHtmlToKeyValueStore": False,
        "includeIcons": False,
    }

    # Ejecuta el Actor y espera a que termine
    run = client.actor("nFJndFXA5zjCTuudP").call(run_input=run_input)
    
    # Obtén los resultados
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)
    
    return results

# Función para calcular el riesgo de canibalización
def calculate_cannibalization_risk(results):
    # Filtra los resultados por orgánicos y pagados
    organic_results = [result for result in results if result.get("type") == "organic"]
    paid_results = [result for result in results if result.get("type") == "paid"]
    
    # Validación de que existan ambos tipos de resultados
    if not organic_results or not paid_results:
        return "Sin riesgo", "No se encontraron suficientes resultados para calcular el riesgo."
    
    # Condiciones de riesgo de canibalización
    first_organic_url = organic_results[0].get("url", "")
    paid_urls = [result.get("url", "") for result in paid_results]

    # 100% de canibalización
    if first_organic_url == paid_urls[0]:
        return "Alto", "⚠️ Riesgo alto de canibalización: el primer resultado orgánico es también el primer resultado pagado."
    
    # Riesgo medio
    elif first_organic_url in paid_urls and paid_urls.index(first_organic_url) <= 4:
        return "Medio", "⚠️ Riesgo medio de canibalización: el primer resultado orgánico está en los primeros 4 resultados pagados."
    
    # Sin riesgo
    else:
        return "Sin riesgo", "✅ Sin riesgo de canibalización: el primer resultado orgánico no aparece en los resultados pagados."

# Verifica que el token de API esté presente
if api_token:
    st.write("Ingrese una palabra clave para realizar la búsqueda:")

    # Campo de entrada de palabra clave
    keyword = st.text_input("Palabra clave")

    if st.button("Buscar") and keyword:
        # Llamada a la función de búsqueda y muestra de resultados
        results = search_query(keyword, api_token)
        
        if results:
            st.write(f"Mostrando resultados para: {keyword}")
            
            # Mostrar resultados y diferenciar orgánicos de pagados
            for result in results:
                result_type = result.get("type", "Sin tipo")
                st.write(f"### [{result_type.upper()}] {result.get('title', 'Sin título')}")
                st.write(result.get("url", "Sin URL"))
                st.write(result.get("snippet", "Sin descripción"))
                st.write("---")
            
            # Calcular y mostrar el riesgo de canibalización
            risk_level, risk_message = calculate_cannibalization_risk(results)
            st.metric("Riesgo de Canibalización", risk_level)
            st.write(risk_message)
        else:
            st.write("No se encontraron resultados.")
else:
    st.warning("Por favor, ingrese su API Token de Apify.")
