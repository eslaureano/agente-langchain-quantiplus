import smtplib
from email.message import EmailMessage
from langchain.tools import tool
import os
import pygsheets
import pandas as pd
import traceback
from dotenv import load_dotenv

# ----------------------
# Cargar credenciales
# ----------------------
load_dotenv()

EMAIL_USER = os.getenv("CORREO_REMITENTE")
EMAIL_PASSWORD = os.getenv("APP_PASSWORD_GMAIL")
SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
SERVICE_ACCOUNT_FILE = "proyecto-agentequantiplus-esl-e7b4217c7e2c.json"
SHEET_NAME = "datos"

# ----------------------
# Catálogo de cursos
# ----------------------
cursos_info = {
    "Credit Scoring & Rating": {
        "inicio": "28 DE AGOSTO",
        "duracion": "18 HORAS",
        "horario": "MARTES Y JUEVES 7 PM - 10 PM",
        "descripcion": "Curso-Taller que involucra todas las etapas de modelización del Credit Scoring y del Rating, desde su fabricación hasta su aplicación en la gestión del riesgo crediticio."
    },
    "Marco de Apetito de Riesgo": {
        "inicio": "14 DE AGOSTO",
        "duracion": "18 HORAS",
        "horario": "MARTES Y JUEVES 7 PM - 10 PM",
        "descripcion": "Curso-Taller para la elaboración de un sistema de apetito de riesgo, como herramienta fundamental para que la entidad financiera gestione el nivel de riesgo de sus operaciones crediticias."
    },
    "Modelos Avanzados de Riesgo de Crédito": {
        "inicio": "24 DE ABRIL",
        "duracion": "27 HORAS",
        "horario": "MARTES Y JUEVES 7 PM - 10 PM",
        "descripcion": "Curso-Taller especializado en metodologías para la gestión del riesgo de crédito. Se revisarán Roll Rates, Stress Testing, Pérdida Esperada y Pricing."
    },
    "Valoración y Proyección de la Cartera de Créditos": {
        "inicio": "24 DE AGOSTO",
        "duracion": "18 HORAS",
        "horario": "JUEVES 7 PM - 10 PM, SÁBADOS 9 AM - 12 PM",
        "descripcion": "Curso-Taller sobre técnicas de análisis y proyección del comportamiento de la cartera crediticia."
    },
    "Cumplimiento Normativo para el Riesgo de Crédito": {
        "inicio": "09 DE JULIO",
        "duracion": "15 HORAS",
        "horario": "LUNES 7 PM - 10 PM, MIÉRCOLES 9 AM - 12 PM",
        "descripcion": "Curso-Taller sobre regulación y supervisión para la gestión del riesgo crediticio, con énfasis en normativas locales e internacionales."
    },
    "Riesgo de Mercado y Liquidez": {
        "inicio": "09 DE JUNIO",
        "duracion": "18 HORAS",
        "horario": "LUNES 7 PM - 10 PM, MIÉRCOLES 7 PM - 10 PM",
        "descripcion": "Curso-Taller que aborda las herramientas para identificar, medir y controlar el riesgo de mercado y de liquidez en las instituciones financieras."
    }
}

# -----------------------------------
# Tool: Registrar en Google Sheets
# -----------------------------------
@tool
def registrar_google_sheets(nombre: str, correo: str, curso: str) -> str:
    """Registra los datos del usuario en Google Sheets."""
    import pygsheets
    gc = pygsheets.authorize(service_file="credenciales_google.json")
    sh = gc.open_by_key("1qJ1PH_zH2WW8Tt2RfPmkynBESWgUK2PenduWhRXOUl0")
    wks = sh[0]
    wks.append_table([nombre, correo, curso])
    return "Registrado en Google Sheets"

# ----------------------
# Tool: Enviar correo
# ----------------------
@tool
def enviar_correo(nombre: str, correo: str, curso: str) -> str:
    """Envía un correo al usuario con información del curso."""
    import smtplib
    from email.message import EmailMessage
    import os

    remitente = os.getenv("CORREO_REMITENTE")
    clave = os.getenv("APP_PASSWORD_GMAIL")

    mensaje = EmailMessage()
    mensaje["Subject"] = f"Información sobre el curso {curso}"
    mensaje["From"] = remitente
    mensaje["To"] = correo
    mensaje.set_content(f"""
Hola {nombre},

Gracias por tu interés en el curso: {curso}.

Pronto nos pondremos en contacto contigo con más detalles. Si tienes alguna pregunta, no dudes en responder a este correo.

Saludos cordiales,
Equipo Quantiplus
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(remitente, clave)
        smtp.send_message(mensaje)

    return f"Correo enviado a {correo}"

# ----------------------------------
# Tool: Procesar datos registrados
# ----------------------------------
@tool
def procesar_datos_registro(texto: str) -> str:
    """
    Extrae nombre, correo y curso desde el texto. Luego registra y envía correo.
    """
    try:
        nombre, correo, curso = [x.strip() for x in texto.split(",")]
        registrar_google_sheets.run({"nombre": nombre, "correo": correo, "curso": curso})
        enviar_correo.run({"nombre": nombre, "correo": correo, "curso": curso})
        return f"He registrado tus datos y enviado un correo con más información sobre el curso \"{curso}\" a {correo}. Si tienes alguna otra pregunta o necesitas más información, no dudes en decírmelo. ¡Espero que disfrutes del curso!"
    except Exception as e:
        return f"Hubo un error al procesar los datos. Asegúrate de escribir: Nombre, correo y curso. Error: {str(e)}"

# ------------------------------
# Tool: Consultar próxima fecha
# ------------------------------
@tool
def consultar_proxima_fecha(nombre_curso: str) -> str:
    """Devuelve la próxima fecha de inicio de un curso específico."""
    nombre_normalizado = nombre_curso.lower().strip()
    coincidencia = next((c for c in cursos_info if nombre_normalizado in c.lower()), None)

    if not coincidencia:
        return f"❌ No se encontró el curso '{nombre_curso}'."

    return f"📅 El curso '{coincidencia}' inicia el {cursos_info[coincidencia]['inicio']}."