import streamlit as st
import numpy as np
import time
from PIL import Image, ImageDraw

try:
    import cv2
except ImportError:
    st.error("Erro: A biblioteca OpenCV (cv2) não está instalada. Pare o terminal e rode: pip install opencv-python")
    st.stop()

st.set_page_config(
    page_title="MalariaDiag AI",
    page_icon="🩸",
    layout="wide"
)

def mock_yolo_detection(image):
    img_w, img_h = image.size
    
    if img_w < 100 or img_h < 100:
        w = min(100, max(50, img_w // 3))
        h = min(100, max(50, img_h // 3))
    else:
        w = 100
        h = 100
    
    detections = []
    configs = [
        (0.2, 0.3, True), (0.5, 0.5, False), (0.7, 0.2, True), 
        (0.3, 0.7, False), (0.6, 0.8, True)
    ]
    
    for i, (rx, ry, is_inf) in enumerate(configs):
        max_x = max(0, img_w - w)
        max_y = max(0, img_h - h)
        x = int(rx * max_x) if max_x > 0 else 0
        y = int(ry * max_y) if max_y > 0 else 0
        
        w_final = min(w, img_w - x) if x + w <= img_w else max(1, img_w - x)
        h_final = min(h, img_h - y) if y + h <= img_h else max(1, img_h - y)
        
        if w_final > 0 and h_final > 0:
            detections.append({
                "id": i+1,
                "bbox": [x, y, w_final, h_final],
                "class": "Infectado" if is_inf else "Não Infectado",
                "yolo_conf": 0.96 if is_inf else 0.88
            })
    return detections

def mock_gradcam(crop_img):
    img = np.array(crop_img)
    
    if len(img.shape) < 2 or img.shape[0] == 0 or img.shape[1] == 0:
        img = np.zeros((200, 200, 3), dtype=np.uint8)
    
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    elif img.shape[-1] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    elif img.shape[-1] != 3:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        
    h, w = img.shape[:2]
    heatmap = np.zeros((h, w), dtype=np.uint8)
    center_x, center_y = w//2, h//2
    radius = min(30, min(w, h) // 4)
    cv2.circle(heatmap, (center_x, center_y), radius, (255), -1)
    
    blur_size = min(51, min(w, h) // 4)
    if blur_size % 2 == 0:
        blur_size += 1
    heatmap = cv2.GaussianBlur(heatmap, (blur_size, blur_size), 0)
    heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    superimposed = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)
    return superimposed

try:
    col1, col2 = st.columns([1, 10])
    with col1:
        st.markdown("#") 
    with col2:
        st.title("MalariaDiag AI")
        st.caption("Protótipo: Detecção YOLOv8 + Predição Conforme")

    st.divider()

    with st.sidebar:
        st.header("Controles")
        uploaded_file = st.file_uploader("Carregar Lâmina", type=["jpg", "png", "jpeg"])
        confidence_level = st.slider("Nível de Confiança (1-alpha)", 0.80, 0.99, 0.95)
        st.info(f"Confiança exigida: {int(confidence_level*100)}%")

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        
        st.subheader("1. Detecção Global (YOLOv8)")
        
        my_bar = st.progress(0)
        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar.progress(percent_complete + 1)
        my_bar.empty()

        detections = mock_yolo_detection(image)
        
        img_draw = image.copy()
        draw = ImageDraw.Draw(img_draw)
        for det in detections:
            x, y, w, h = det['bbox']
            color = "#ff0000" if det['class'] == "Infectado" else "#00ff00"
            draw.rectangle([x, y, x+w, y+h], outline=color, width=5)
            
        st.image(img_draw, caption=f"YOLO encontrou {len(detections)} células")

        st.divider()
        st.subheader("2. Auditoria de Incerteza (MobileNetV2)")

        selected_id = st.selectbox(
            "Selecione uma célula para auditar:", 
            options=[d['id'] for d in detections],
            format_func=lambda x: f"Célula #{x} ({next(d['class'] for d in detections if d['id'] == x)})"
        )
        
        cell = next(d for d in detections if d['id'] == selected_id)
        x, y, w, h = cell['bbox']
        
        if w > 0 and h > 0:
            img_w, img_h = image.size
            x = max(0, min(x, img_w - 1))
            y = max(0, min(y, img_h - 1))
            w = min(w, img_w - x)
            h = min(h, img_h - y)
            
            if w > 0 and h > 0:
                cell_crop = image.crop((x, y, x+w, y+h)).resize((200, 200))
            else:
                st.error("Erro: Dimensões inválidas para o recorte da célula.")
                cell_crop = image.resize((200, 200))
        else:
            st.error("Erro: Dimensões inválidas para o recorte da célula.")
            cell_crop = image.resize((200, 200))
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown("**Recorte (ROI)**")
            st.image(cell_crop)
            
        with c2:
            st.markdown("**Predição Conforme**")
            
            if confidence_level > 0.95:
                pred_set = "{Infectado, Não Infectado}"
                color = "orange"
                note = "⚠️ Incerteza Alta"
            else:
                pred_set = f"{{{cell['class']}}}"
                color = "red" if cell['class'] == "Infectado" else "green"
                note = "Confiável"
                
            st.markdown(f"""
            <div style="border:1px solid #ddd; padding:10px; border-radius:5px;">
                <h3 style="color:{color}; text-align:center;">{pred_set}</h3>
                <p style="text-align:center;">{note}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with c3:
            st.markdown("**Explicabilidade**")
            heatmap = mock_gradcam(cell_crop)
            st.image(heatmap, caption="Grad-CAM")

    else:
        st.info("Faça o upload de uma imagem na barra lateral para começar.")

except Exception as e:
    st.error(f"Ocorreu um erro no script: {e}")