import fitz  # PyMuPDF

def extraer_texto_pdf(ruta_pdf):
    """
    Extrae el texto de un archivo PDF.
    """
    texto = ""
    with fitz.open(ruta_pdf) as pdf:
        for pagina in pdf:
            texto += pagina.get_text()
    return texto

def dividir_texto(texto, max_tokens=512):
    """
    Divide el texto en fragmentos más pequeños según el límite de tokens.
    """
    palabras = texto.split()
    fragmentos = []
    fragmento_actual = []
    
    for palabra in palabras:
        fragmento_actual.append(palabra)
        if len(fragmento_actual) >= max_tokens:
            fragmentos.append(" ".join(fragmento_actual))
            fragmento_actual = []
    
    if fragmento_actual:
        fragmentos.append(" ".join(fragmento_actual))
    
    return fragmentos
