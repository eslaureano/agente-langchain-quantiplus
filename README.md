# 🤖 Agente LangChain de Atención al Usuario - Quantiplus

Este proyecto implementa un asistente conversacional utilizando LangChain, Streamlit y herramientas personalizadas para automatizar la atención al usuario en cursos de Quantiplus.

---

## 🚀 Funcionalidades

- Registro automático de usuarios interesados (nombre, correo, curso).
- Envío de correos personalizados con la información del curso.
- Consulta de la próxima fecha de inicio de los cursos.
- Interfaz de chat web tipo asistente.
- Uso de herramientas (`@tool`),chain, prompt template integradas mediante LangChain.
- Comunicación vía Google Sheets y Gmail.

---

## 🧭 Diagrama de Arquitectura

<img width="631" height="390" alt="image" src="https://github.com/user-attachments/assets/82d8f96a-ef80-4672-9746-8d4bd7232ae7" />


---

## ⚙️ Explicación funcional de la arquitectura

1. **Streamlit** actúa como interfaz web para la interacción con el usuario.
2. **LangChain** permite estructurar el comportamiento del agente y gestionar herramientas.
3. **Tools personalizadas**: se encargan del registro en Google Sheets (`registrar_google_sheets`) y del envío de correos (`enviar_correo`).
4. **Google Sheets** funciona como base de datos ligera de leads.
5. **Gmail SMTP** permite el envío automático de correos de seguimiento.

---

## 📁 Estructura del repositorio

📦agente-langchain-quantiplus/
├── app.py # Interfaz Streamlit y ejecución del agente
├── tools.py # Herramientas personalizadas para LangChain
├── requirements.txt # Dependencias del proyecto
├── .env # Variables de entorno (no subir)
├── image/
│ ├── Logo_quantiplus.png
│ ├── bot_icon.png
│ ├── user_icon.png
│ └── arquitectura.png

yaml
Copiar
Editar
