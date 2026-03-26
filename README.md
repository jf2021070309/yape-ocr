# Yape OCR Extractor Pro 🚀

Herramienta de escritorio basada en Python para la extracción automática de datos (Monto y Código de Seguridad) de capturas de pantalla de la aplicación Yape.

## ✨ Características
- **Detección de Monto Inteligente**: Soporta variaciones del OCR como `S/`, `SI`, `S1`, `S.` y evita confusiones con años (ej: 2025).
- **Extracción de Código de Seguridad**: Lógica avanzada para ignorar el icono informativo `(i)` y capturar los 3 dígitos exactos, incluso si están en cuadros separados.
- **Pre-procesamiento de Imagen**: Aplica re-escalado (Upscaling 2x), nitidez y balance de contraste automático para leer textos tenues en cuadros grises.
- **Interfaz Gráfica (Tkinter)**: Diseño moderno con previsualización de imagen en tiempo real y barra de progreso.
- **Privacidad Total**: Todo el procesamiento se realiza de forma local en tu computadora; no se envían datos a ningún servidor externo.

## 🛠️ Instalación

1. **Clonar o descargar** este repositorio en tu carpeta de trabajo.
2. Asegúrate de tener **Python 3.9+** instalado.
3. Instala las dependencias necesarias ejecutando el siguiente comando en tu terminal:

```bash
pip install easyocr pillow
```

*Nota: La primera vez que ejecutes el script, este descargará los modelos de reconocimiento de texto (aprox. 150MB). Esto solo ocurre una vez.*

## 🚀 Uso

Para iniciar la aplicación, ejecuta:

```bash
python yape_ocr.py
```

1. Haz clic en el botón **"Subir Imagen y Escanear"**.
2. Selecciona la captura de pantalla de Yape.
3. La aplicación mostrará la imagen a la derecha y los resultados extraídos (Monto y Código) a la izquierda.

## ⚙️ Requisitos Técnicos
- **Motor OCR**: EasyOCR (basado en PyTorch).
- **GPU (Opcional)**: Si tienes una tarjeta gráfica NVIDIA con CUDA, el procesamiento será mucho más rápido. De lo contrario, usará automáticamente el CPU (procesador).

## 📝 Notas de Precisión
- Para mejores resultados, utiliza capturas de pantalla directas del celular, no fotos de baja resolución tomadas a otro dispositivo.
- El script ignora automáticamente las advertencias técnicas de la terminal para mantener una experiencia limpia.

---
Desarrollado con ❤️ para agilizar la validación de pagos.
