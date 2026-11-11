import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import json

st.set_page_config(layout="wide")
st.title("Mosaico Pixel Art Guide 🛠️")

if "blocos_concluidos" not in st.session_state:
    st.session_state.blocos_concluidos = []

st.subheader("1. Carregue ou Envie a sua Imagem")
uploaded_file = st.file_uploader("Escolha qualquer imagem ou foto salva no seu computador/celular:")

if uploaded_file is not None:
    img_crua = Image.open(uploaded_file)
    
    if img_crua.mode in ("RGBA", "LA") or (img_crua.mode == "P" and "transparency" in img_crua.info):
        imagem_original = Image.new("RGB", img_crua.size, (255, 255, 255))
        imagem_original.paste(img_crua, (0, 0), img_crua.convert("RGBA"))
    else:
        imagem_original = img_crua.convert("RGB")

    largura_orig, altura_orig = imagem_original.size

    st.write("---")
    st.subheader("2. Configurações do Mosaico (Tamanho da Grade)")
    
    col_h, col_v = st.columns(2)
    pixels_h = col_h.slider("Quantidade de blocos na Horizontal", min_value=10, max_value=80, value=30, step=1)
    pixels_v = col_v.slider("Quantidade de blocos na Vertical", min_value=10, max_value=80, value=30, step=1)

    if pixels_h == pixels_v:
        menor_dimensao = min(largura_orig, altura_orig)
        pos_x = (largura_orig - menor_dimensao) // 2
        pos_y = (altura_orig - menor_dimensao) // 2
        imagem_processada = imagem_original.crop((pos_x, pos_y, pos_x + menor_dimensao, pos_y + menor_dimensao))
    else:
        imagem_processada = imagem_original

    img_pequena = imagem_processada.resize((pixels_h, pixels_v), resample=Image.Resampling.NEAREST)
    
    matriz_cores = []
    for y in range(pixels_v):
        linha = []
        for x in range(pixels_h):
            r, g, b = img_pequena.getpixel((x, y))
            linha.append(f"rgb({r},{g},{b})")
        matriz_cores.append(linha)

    st.write("---")
    st.subheader("3. Guia Interativo: Toque direto nos quadrados para marcar como Concluído")
    st.info("💡 Clique em cima de qualquer bloco para riscá-lo. O fundo transparente agora está corrigido!")

    dados_grade = json.dumps(matriz_cores)
    
    codigo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ background-color: #0e1117; color: white; font-family: sans-serif; margin: 0; padding: 10px; display: flex; justify-content: center; }}
            .container-mosaico {{ 
                display: flex; 
                flex-direction: column; 
                position: relative; 
                border: 2px solid #555; 
                user-select: none;
                width: 100%;
                max-width: 1000px;
                box-sizing: border-box;
                padding: 15px;
                background-color: #1a1c23;
                border-radius: 8px;
            }}
            .corpo-grade {{ display: flex; width: 100%; }}
            .grade {{ 
                display: grid; 
                grid-template-columns: repeat({pixels_h}, 1fr); 
                grid-template-rows: repeat({pixels_v}, 1fr); 
                gap: 1px; 
                background-color: #444; 
                width: 100%;
                aspect-ratio: {pixels_h} / {pixels_v};
            }}
            .pixel {{ 
                width: 100%; 
                height: 100%; 
                cursor: pointer; 
                position: relative; 
                box-sizing: border-box; 
            }}
            .pixel:hover {{ 
                outline: 2px solid #fff;
                z-index: 10; 
            }}
            .marcado::after {{
                content: "❌";
                position: absolute;
                top: 50%; left: 50%;
                transform: translate(-50%, -50%);
                font-size: clamp(6px, 1.5vw, 14px);
                color: #ff3333;
                text-shadow: 1px 1px 2px black;
            }}
            .marcado {{ filter: brightness(0.3); }}
            
            .regua-h {{ display: grid; grid-template-columns: repeat({pixels_h}, 1fr); margin-left: 25px; margin-bottom: 5px; }}
            .num-h {{ text-align: center; font-size: 10px; color: #aaa; min-height: 12px; }}
            .regua-v {{ display: grid; grid-template-rows: repeat({pixels_v}, 1fr); margin-right: 5px; width: 20px; }}
            .num-v {{ display: flex; align-items: center; justify-content: flex-end; font-size: 10px; color: #aaa; }}
        </style>
    </head>
    <body>

        <div class="container-mosaico">
            <div class="regua-h" id="reguaH"></div>
            <div class="corpo-grade">
                <div class="regua-v" id="reguaV"></div>
                <div class="grade" id="gradeMosaico"></div>
            </div>
        </div>

        <script>
            const cores = {dados_grade};
            const colunas = {pixels_h};
            const linhas = {pixels_v};
            
            const rH = document.getElementById('reguaH');
            for(let x=0; x<colunas; x++) {{
                const num = document.createElement('div');
                num.className = 'num-h';
                num.innerText = x % 5 === 0 ? x : '';
                rH.appendChild(num);
            }}
            
            const rV = document.getElementById('reguaV');
            for(let y=0; y<linhas; y++) {{
                const num = document.createElement('div');
                num.className = 'num-v';
                num.innerText = y % 5 === 0 ? y : '';
                rV.appendChild(num);
            }}

            const grade = document.getElementById('gradeMosaico');
            for(let y=0; y<linhas; y++) {{
                for(let x=0; x<colunas; x++) {{
                    const div = document.createElement('div');
                    div.className = 'pixel';
                    div.style.backgroundColor = cores[y][x];
                    div.title = `Coluna ${{x}}, Linha ${{y}}`;
                    
                    div.addEventListener('click', () => {{
                        div.classList.toggle('marcado');
                    }});
                    
                    grade.appendChild(div);
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    components.html(codigo_html, height=1050, scrolling=False)