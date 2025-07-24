import streamlit as st
import time
import os
import pathlib
import re
from dotenv import load_dotenv
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda

from tools import registrar_google_sheets, enviar_correo, consultar_proxima_fecha, procesar_datos_registro

load_dotenv()

# Imágenes
current_dir = pathlib.Path(__file__).parent
image_path = current_dir / "image" / "Logo_quantiplus.png"
avatar_user_path = current_dir / "image" / "user_icon.png"
avatar_bot_path = current_dir / "image" / "bot_icon.png"

# Logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(str(image_path), width=900)

# Estado
if "messages" not in st.session_state:
    st.session_state.messages = []
if "welcomed" not in st.session_state:
    st.session_state.welcomed = False

# Historial
for message in st.session_state.messages:
    avatar = str(avatar_user_path) if message["role"] == "user" else str(avatar_bot_path)
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Efecto máquina de escribir
def typewriter(text: str, speed: int = 50):
    tokens = text.split()
    container = st.empty()
    for i in range(len(tokens) + 1):
        container.markdown(" ".join(tokens[:i]))
        time.sleep(1 / speed)

# LLM y agente
llm = ChatOpenAI(model="gpt-4o", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
Eres un asistente de Quantiplus. Tu tarea es asistir a los usuarios con información sobre cursos, fechas, docentes, registro y contacto por correo.

👋 ¡Hola! Bienvenido a Quantiplus. Nos especializamos en soluciones analíticas de datos utilizando técnicas avanzadas de minería de datos y herramientas informáticas, siempre con un enfoque en el sentido de negocio de la compañía. ¿En qué puedo ayudarte hoy?

Si preguntan por los cursos, responde solo con esta lista:
Estos son los cursos disponibles:
✅ Marco de Apetito de Riesgo
✅ Credit Scoring & Rating
✅ Modelos Avanzados de Riesgo de Crédito
✅ Valoración y Proyección de la Cartera de Créditos
✅ Cumplimiento Normativo para el Riesgo de Crédito
✅ Riesgo de Mercado y Liquidez

Si deseas más información sobre alguno de estos cursos, no dudes en preguntar.

Si preguntan sobre la empresa o sobre Quantiplus, no vuelvas a saludar, solo responde con:
QUANTIPLUS o la empresa se especializa en soluciones analíticas de datos basadas en técnicas avanzadas de minería de datos y herramientas informáticas, siempre enfocadas en el sentido de negocio de la compañía.

Si preguntan por el docente, no vuelvas a saludar, solo responde:
El docente de los cursos es Wilson Arias. Puedes revisar su perfil profesional aquí 👉 https://www.linkedin.com/in/wilson-a-b524a867/

Si preguntan por el curso próximo a iniciar,  no vuelvas a saludar, llama a la herramienta 'consultar_proxima_fecha'. Luego de dar la fecha, pregunta:
¿Te gustaría recibir más información sobre este curso?

Si el usuario responde que sí, solicita: nombre, correo electrónico y curso de interés.

Cuando recibas un mensaje que contenga directamente el nombre, correo y curso (por ejemplo: \"Evelyn Laureano, evelynsanzlau@gmail.com, Credit Scoring & Rating\"), registra de inmediato estos datos usando la herramienta 'procesar_datos_registro'. No pidas confirmación adicional. 

Luego de enviar el correo responde con:
He registrado tus datos y enviado un correo con más información sobre el curso \"NOMBRE_CURSO\" a CORREO. Si tienes alguna otra pregunta o necesitas más información, no dudes en decírmelo. ¡Espero que disfrutes del curso!

Si no tienes la información, responde:
Por el momento no cuento con esa información, pero nos pondremos en contacto contigo. Por favor deja tus datos como: Nombre completo, correo y curso de interés.
    """),
    MessagesPlaceholder(variable_name="messages"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

tools = [consultar_proxima_fecha, registrar_google_sheets, enviar_correo, procesar_datos_registro]
agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Extracción de datos
def extraer_datos_registro(text):
    match = re.match(r"(.+?),\s*([\w\.-]+@[\w\.-]+),\s*(.+)", text)
    if match:
        return {
            "nombre": match.group(1).strip(),
            "correo": match.group(2).strip(),
            "curso": match.group(3).strip()
        }
    return None

# Router
def dispatch_chain(x):
    datos = extraer_datos_registro(x["input"])
    if datos:
        return {
            "output": registrar_google_sheets.invoke(datos) + "\n" +
                      enviar_correo.invoke(datos)
        }
    else:
        return agent_executor.invoke({
            "messages": [HumanMessage(content=x["input"])]
        })

chain = RunnableLambda(dispatch_chain)

# Entrada del usuario
if prompt_input := st.chat_input("Escribir mensaje..."):
    st.session_state.messages.append({"role": "user", "content": prompt_input})
    with st.chat_message("user", avatar=str(avatar_user_path)):
        st.markdown(prompt_input)

    despedidas = ["gracias", "chau", "adiós", "adios", "hasta luego"]
    if any(d in prompt_input.lower() for d in despedidas):
        mensaje_final = "Gracias por la visita, cualquier duda nos escribes."
        st.session_state.messages.append({"role": "assistant", "content": mensaje_final})
        with st.chat_message("assistant", avatar=str(avatar_bot_path)):
            typewriter(mensaje_final)
        st.session_state.welcomed = False
    else:
        st.session_state.welcomed = True

        with st.spinner('Quantibot está escribiendo...'):
            st.toast('Estamos agradecidos por tu contacto!', icon='🎉')
            response = chain.invoke({"input": prompt_input})

        message_assistant = response.get("output", "Lo siento, no pude generar una respuesta.").replace("\n", "  \n")
        st.session_state.messages.append({"role": "assistant", "content": message_assistant})
        with st.chat_message("assistant", avatar=str(avatar_bot_path)):
            typewriter(message_assistant, speed=50)