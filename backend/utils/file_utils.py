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

def dividir_texto(texto, max_tokens=512, superposicion=50):
    """
    Divide el texto en fragmentos con superposición para preservar contexto.
    """
    palabras = texto.split()
    fragmentos = []
    num_palabras = len(palabras)

    for i in range(0, num_palabras, max_tokens - superposicion):
        fragmentos.append(" ".join(palabras[i:min(i + max_tokens, num_palabras)]))
    
    return fragmentos

