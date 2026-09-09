import re

# diccionario de amenidades de los hoteles
# algunas amenidades viene con texto extra e.g. wifi puede venir como "free wifi" o "good wifi"
# entonces se guardo en base a palabras clave, usando el mismo ejemplo de wifi, su palabra clave es simplemente wifi
AMENIDADES = {
    "pool": ["pool"],
    "wifi": ["wifi"],
    "parking": ["parking"],
    "beachfront": ["beachfront", "private beach area"],
    "breakfast": ["breakfast"],
    "restaurant": ["restaurant"],
    "bar": ["bar"],
    "gym": ["fitness", "gym"],
    "spa": ["spa"],
    "accesibility": ["disabled", "accessib"],
    "family": ["family room"],
    "airport": ["airport shuttle", "airport transfer"],
    "service": ["room service"],
    "non smoking": ["non-smoking"],
    "pet": ["pet"],
    "seaview": ["sea view", "ocean view", "beach view"],
    "ac": ["air condition", "a/c"]
}

def precio(txt):
    # este patron matchea con precios de booking (es moneda espacio monto: MXN $1,234.)
    # en caso de usar otro vendedor como fuente, verificar que cumpla con el patron 
    # o modifcarlo/agregar otro para que se ajusto al vendedor.
    pattern = r"^([A-Z]{2,4})\s+([\d,]+(?:\.\d+)?)$"
    match = re.match(pattern, txt)
    if match:
        moneda, monto = match.group(1), match.group(2)
    else:
        raise ValueError(f"Patron de precio no reconocido.\n{txt}")
    monto = monto.replace(",", "")
    monto = float(monto)
    return moneda, monto

def calif(txt):
    if txt is None:
        return None
    numRating = float(txt)
    return numRating

def resenas(txt):
    if txt is None:
        return None
    txt = txt.replace(",", "")
    numResenas = int(txt)
    return numResenas

def normalizarAmenidades(txt):
    txt = txt.lower()
    for cat, keys in AMENIDADES.items():
        for keyword in keys:
            pattern = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, txt):
                return cat
    return None

def extraerAmenidades(hotel):
    amenidades = set()

    fuentes = [
        # puede que una fuente no exista. en los datos que tenemos ahorita siempre existe 'facilidades_populares'
        # pero 'property_highlights' es nulo en por lo menos 1 caso.
        hotel.get("facilidades_populares") or [],
        hotel.get("property_highlights") or []
    ]

    for lista in fuentes:
        for text in lista:
            categoria = normalizarAmenidades(text)
            if categoria is not None:
                amenidades.add(categoria)
    
    return amenidades

