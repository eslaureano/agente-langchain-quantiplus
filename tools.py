import smtplib
from email.message import EmailMessage
from langchain.tools import tool
import os
import pygsheets
from dotenv import load_dotenv

# Cargar credenciales del entorno
load_dotenv()

EMAIL_USER = os.getenv("CORREO_REMITENTE")
EMAIL_PASSWORD = os.getenv("APP_PASSWORD_GMAIL")
SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

# Catálogo de cursos
cursos_info = {
    "Marco de Apetito de Riesgo": {
        "inicio": "14 DE AGOSTO",
        "duracion": "18 HORAS",
        "horario": "MARTES Y JUEVES 7 PM - 10 PM",
        "descripcion": "Curso-Taller para la elaboración de un sistema de apetito de riesgo, como herramienta fundamental para que la entidad financiera gestione el nivel de riesgo de sus operaciones crediticias."
    },
        "Valoración y Proyección de la Cartera de Créditos": {
        "inicio": "24 DE AGOSTO",
        "duracion": "18 HORAS",
        "horario": "JUEVES 7 PM - 10 PM, SÁBADOS 9 AM - 12 PM",
        "descripcion": "Curso-Taller sobre técnicas de análisis y proyección del comportamiento de la cartera crediticia."
    },
        "Credit Scoring & Rating": {
        "inicio": "28 DE AGOSTO",
        "duracion": "18 HORAS",
        "horario": "MARTES Y JUEVES 7 PM - 10 PM",
        "descripcion": "Curso-Taller que involucra todas las etapas de modelización del Credit Scoring y del Rating, desde su fabricación hasta su aplicación en la gestión del riesgo crediticio."
    },    
    "Modelos Avanzados de Riesgo de Crédito": {
        "inicio": "24 DE ABRIL",
        "duracion": "27 HORAS",
        "horario": "MARTES Y JUEVES 7 PM - 10 PM",
        "descripcion": "Curso-Taller especializado en metodologías para la gestión del riesgo de crédito. Se revisarán Roll Rates, Stress Testing, Pérdida Esperada y Pricing."
    },
    "Riesgo de Mercado y Liquidez": {
        "inicio": "09 DE JUNIO",
        "duracion": "18 HORAS",
        "horario": "LUNES 7 PM - 10 PM, MIÉRCOLES 7 PM - 10 PM",
        "descripcion": "Curso-Taller que aborda las herramientas para identificar, medir y controlar el riesgo de mercado y de liquidez en las instituciones financieras."
    },
        "Cumplimiento Normativo para el Riesgo de Crédito": {
        "inicio": "09 DE JULIO",
        "duracion": "15 HORAS",
        "horario": "LUNES 7 PM - 10 PM, MIÉRCOLES 9 AM - 12 PM",
        "descripcion": "Curso-Taller sobre regulación y supervisión para la gestión del riesgo crediticio, con énfasis en normativas locales e internacionales."
    }
}

@tool
def registrar_google_sheets(nombre: str, correo: str, curso: str) -> str:
    """Registra los datos del usuario en Google Sheets con encabezado e ID incremental."""
    SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
    gc = pygsheets.authorize(service_file=SERVICE_ACCOUNT_PATH)
    sh = gc.open_by_key(SHEET_ID)
    wks = sh[0]

    # Leer registros actuales (sin filas vacías al final)
    registros = wks.get_all_values(include_tailing_empty=False)

    # Si está vacía, escribe encabezado
    if len(registros) == 0:
        encabezado = ["ID", "Nombre", "Correo", "Curso"]
        wks.append_table(encabezado)

    # Nuevo ID = cantidad de registros actuales - 1 (por el encabezado)
    nuevo_id = len(wks.get_all_records()) + 1

    # Agregar fila con ID
    fila = [nuevo_id, nombre, correo, curso]
    wks.append_table(fila)

    return f"✅ Registrado en Google Sheets"

@tool
def enviar_correo(nombre: str, correo: str, curso: str) -> str:
    """
    Envía un correo personalizado al usuario con detalles del curso indicado.
    """
    try:
        # Buscar el curso por coincidencia parcial
        nombre_normalizado = curso.lower().strip()
        coincidencia = next((c for c in cursos_info if nombre_normalizado in c.lower()), None)

        if not coincidencia:
            return f"❌ El curso '{curso}' no se encuentra en la lista."

        datos = cursos_info[coincidencia]

        # Construcción del mensaje
        mensaje = f"""Hola {nombre},

Gracias por tu interés en el curso '{coincidencia}'. Aquí tienes más información:

📅 Inicio: {datos['inicio']}
⏱️ Duración: {datos['duracion']}
🕒 Horario: {datos['horario']}

{datos['descripcion']}

Para más información, visita nuestro sitio web:
🌐 http://www.quantiplus.com/home.html

Saludos cordiales,  
Equipo Quantiplus
"""

        # Envío por correo
        email = EmailMessage()
        email["From"] = EMAIL_USER
        email["To"] = correo
        email["Subject"] = f"📘 Información sobre el curso: {coincidencia}"
        email.set_content(mensaje)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(email)

        return f"✅ Correo enviado correctamente a {correo}."

    except Exception as e:
        return f"❌ Error al enviar correo: {str(e)}"
    
@tool
def procesar_datos_registro(texto: str) -> str:
    """Extrae datos y ejecuta registro + envío de correo."""
    try:
        nombre, correo, curso = [x.strip() for x in texto.split(",")]
        registrar_google_sheets.invoke({"nombre": nombre, "correo": correo, "curso": curso})
        enviar_correo.invoke({"nombre": nombre, "correo": correo, "curso": curso})
        return f"He registrado tus datos y enviado un correo con más información sobre el curso \"{curso}\" a {correo}."
    except Exception as e:
        return f"❌ Error al procesar los datos. Asegúrate de usar: Nombre, correo, curso. Detalle: {str(e)}"

@tool
def consultar_proxima_fecha(nombre_curso: str) -> str:
    """Devuelve la próxima fecha de inicio de un curso específico."""
    nombre_normalizado = nombre_curso.lower().strip()
    coincidencia = next((c for c in cursos_info if nombre_normalizado in c.lower()), None)
    if not coincidencia:
        return f"❌ No se encontró el curso '{nombre_curso}'."
    return f"📅 El curso '{coincidencia}' inicia el {cursos_info[coincidencia]['inicio']}."