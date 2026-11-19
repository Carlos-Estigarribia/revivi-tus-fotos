
# Importamos Gradio para crear la interfaz web
import gradio_client
import gradio as gr
import os
import tempfile

# Importamos el cliente para comunicarnos con otro servidor Gradio
from gradio_client import Client


# Dirección pública del backend de Colab
BACKEND_URL = "https://c046dcec345c84ad80.gradio.live"

# Creamos el cliente para conectarnos con Colab
cliente = Client(BACKEND_URL)


# Función de conexión con el backend
def procesar_imagen_backend(imagen, semilla, nivel_reconstruccion):
    """
    Guarda temporalmente la fotografía, la envía al backend
    remoto y devuelve la imagen procesada y su análisis.
    """

    if imagen is None:
        raise gr.Error("Primero tenés que cargar una fotografía.")

    if semilla is None or not float(semilla).is_integer():
        raise gr.Error("Ingresá un número entero como semilla.")

    ruta_temporal = None

    try:
        # Guardamos temporalmente la imagen en formato PNG
        with tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False
        ) as archivo:
            ruta_temporal = archivo.name

        imagen.save(ruta_temporal, format="PNG")

        # Enviamos la fotografía y los parámetros a Colab
        resultado = cliente.predict(
            gradio_client.handle_file(ruta_temporal),
            int(semilla),
            int(nivel_reconstruccion),
            api_name="/procesar"
        )

        return resultado

    except Exception as error:
        raise gr.Error(
            f"No se pudo procesar la fotografía: {error}"
        )

    finally:
        # Eliminamos el archivo temporal
        if ruta_temporal and os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)


print("Iniciando Reviví tus fotos...")


# Interfaz principal
with gr.Blocks(title="Reviví tus fotos") as demo:

    gr.Markdown("# Reviví tus fotos")
    gr.Markdown("Tus recuerdos, con una nueva vida.")

    # Carga de fotografía
    imagen = gr.Image(
        label="Cargá una fotografía",
        type="pil"
    )

    # Configuración de la semilla
    semilla = gr.Number(
        label="Semilla",
        value=42,
        precision=0
    )

    # Selector del nivel de reconstrucción
    nivel_reconstruccion = gr.Radio(
        choices=[
            ("Conservador", 1),
            ("Equilibrado", 20),
            ("Creativo", 50)
        ],
        value=1,
        label="Nivel de reconstrucción",
        info=(
            "Elegí cuánto puede variar la imagen durante "
            "la reconstrucción. Para fotografías antiguas "
            "o deterioradas se recomienda comenzar "
            "con el nivel conservador."
        )
    )

    # Resultados
    with gr.Row():
        original = gr.Image(
            label="Fotografía original",
            format="png"
        )

        resultado = gr.Image(
            label="Fotografía reconstruida",
            format="png"
        )

    # Informe del análisis
    analisis = gr.Textbox(
        label="Análisis de la fotografía",
        lines=8,
        interactive=False
    )

    # Botón de procesamiento
    boton_restaurar = gr.Button(
        "Restaurar fotografía",
        variant="primary"
    )

    boton_restaurar.click(
        fn=procesar_imagen_backend,
        inputs=[
            imagen,
            semilla,
            nivel_reconstruccion
        ],
        outputs=[
            original,
            resultado,
            analisis
        ]
    )


print("Iniciando servidor web...")

demo.launch(
    server_name="127.0.0.1",
    server_port=7861,
    inbrowser=True
)

