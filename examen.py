import streamlit as st
import sympy as sp
import time
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Examen Cálculo Diferencial", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .big-font { font-size:20px !important; }
    .stAlert { margin-top: 20px; }
    .report-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; }
    .instruction { color: #555; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS DE EJERCICIOS (EXTRACCIÓN COMPLETA DE IMÁGENES) ---
def get_questions():
    x = sp.symbols('x')
    
    # Lista completa basada en tus imágenes
    questions = [
        # --- SECCIÓN 1: LÍMITES (Imagen 938621.png) ---
        {
            "id": 1,
            "topic": "Límites Directos",
            "latex": r"\lim_{x \to 2} (3x - 9)",
            "correct_expr": -3,
            "type": "value",
            "min_seconds": 10,
            "hint": "Sustitución directa."
        },
        {
            "id": 2,
            "topic": "Límites Racionales",
            "latex": r"\lim_{x \to 2} \frac{2x + 4}{x - 7}",
            "correct_expr": sp.Rational(8, -5), # -8/5
            "type": "value",
            "min_seconds": 20,
            "hint": "Sustituye y simplifica la fracción."
        },

        # --- SECCIÓN 2: DERIVADAS BÁSICAS Y TRIGONOMÉTRICAS (Img 937e7f.png) ---
        {
            "id": 3,
            "topic": "Derivada (Polinomio y Trig)",
            "latex": r"f(x) = x^2 - \cos(x)",
            "func": x**2 - sp.cos(x),
            "correct_expr": 2*x + sp.sin(x),
            "type": "derivative",
            "min_seconds": 15,
            "hint": "La derivada de cos(x) es -sen(x)."
        },
        {
            "id": 4,
            "topic": "Derivada (Regla del Producto)",
            "latex": r"f(x) = x \sin(x)",
            "func": x * sp.sin(x),
            "correct_expr": sp.sin(x) + x*sp.cos(x),
            "type": "derivative",
            "min_seconds": 25,
            "hint": "u'v + uv'"
        },
        {
            "id": 5,
            "topic": "Derivada (Producto con Trig)",
            "latex": r"f(x) = (x^3 - 2) \tan(x)",
            "func": (x**3 - 2) * sp.tan(x),
            "correct_expr": 3*x**2 * sp.tan(x) + (x**3 - 2) * sp.sec(x)**2,
            "type": "derivative",
            "min_seconds": 40,
            "hint": "Recuerda que la derivada de tan(x) es sec^2(x)."
        },

        # --- SECCIÓN 3: REGLA DE LA CADENA Y COCIENTE (Img 937ebd.png, 937f7d.png, 937b5e.png) ---
        {
            "id": 6,
            "topic": "Derivada (Regla de la Cadena)",
            "latex": r"f(x) = (6x - 1)^2",
            "func": (6*x - 1)**2,
            "correct_expr": 2 * (6*x - 1) * 6, # 12(6x-1)
            "type": "derivative",
            "min_seconds": 20,
            "hint": "Baja el 2, resta uno al exponente y multiplica por la derivada de adentro (6)."
        },
        {
            "id": 7,
            "topic": "Derivada (Cociente)",
            "latex": r"f(x) = \frac{10}{x^2 + 1}",
            "func": 10 / (x**2 + 1),
            "correct_expr": -20*x / (x**2 + 1)**2,
            "type": "derivative",
            "min_seconds": 45,
            "hint": "Usa la regla del cociente o reescribe como 10(x^2+1)^-1"
        },
        {
            "id": 8,
            "topic": "Cadena Compleja",
            "latex": r"f(x) = (x^3 + x^2)^3",
            "func": (x**3 + x**2)**3,
            "correct_expr": 3*(x**3 + x**2)**2 * (3*x**2 + 2*x),
            "type": "derivative",
            "min_seconds": 40,
            "hint": "Regla general de la potencia."
        },
        {
            "id": 9,
            "topic": "Derivada (Cociente Trigonométrico)",
            "latex": r"f(x) = \frac{\sin(5x)}{\cos(6x)}",
            "func": sp.sin(5*x) / sp.cos(6*x),
            "correct_expr": sp.diff(sp.sin(5*x) / sp.cos(6*x), x),
            "type": "derivative",
            "min_seconds": 90, # Esta es difícil, damos más tiempo
            "hint": "Cuidado con los argumentos 5x y 6x al derivar."
        },

        # --- SECCIÓN 4: MÁXIMOS Y MÍNIMOS (Img 937723.png, 937381.png) ---
        {
            "id": 10,
            "topic": "Puntos Críticos (Simple)",
            "latex": r"f(x) = -x^2 + 2x + 1 \quad (\text{Encuentra el valor crítico } x)",
            "func": -x**2 + 2*x + 1,
            "correct_expr": 1,
            "type": "value",
            "min_seconds": 25,
            "hint": "Iguala la primera derivada a cero."
        },
        {
            "id": 11,
            "topic": "Extremos Relativos (Polinomio Cúbico)",
            "latex": r"f(x) = x^3 - 3x \quad (\text{Encuentra el valor POSITIVO de } x \text{ donde f'(x)=0})",
            "func": x**3 - 3*x,
            "correct_expr": 1, # x^2 - 1 = 0 -> x = 1 (el positivo)
            "type": "value",
            "min_seconds": 35,
            "hint": "Deriva 3x^2 - 3 y despeja x. Ingresa solo la raíz positiva."
        }
    ]
    return questions

# --- FUNCIONES DE LÓGICA MATEMÁTICA ---
def parse_input(user_str):
    """Limpia y convierte texto del usuario a expresión SymPy"""
    if not user_str: return None
    try:
        # Normalización de entrada
        clean_str = user_str.replace("^", "**")
        clean_str = clean_str.replace("sen", "sin") # Español
        clean_str = clean_str.replace("sec", "1/cos") # SymPy a veces prefiere cos/sin básico
        clean_str = clean_str.replace("csc", "1/sin")
        
        # Transformaciones para permitir "2x" en lugar de "2*x"
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
        transformations = (standard_transformations + (implicit_multiplication_application,))
        
        expr = parse_expr(clean_str, transformations=transformations)
        return expr
    except Exception as e:
        return None

def check_answer(user_input, correct_expr, q_type):
    x = sp.symbols('x')
    user_expr = parse_input(user_input)
    
    if user_expr is None:
        return False, "Error de sintaxis"

    # Comparación algebraica simbólica
    # Simplify intenta reducir (Usuario - Correcto) a 0
    try:
        diff = sp.simplify(user_expr - correct_expr)
        # Verificamos si es 0 (exacto) o un valor numérico muy pequeño (flotante)
        if diff == 0:
            return True, user_expr
        # Doble verificación para identidades trigonométricas rebeldes
        if sp.trigsimp(diff) == 0:
            return True, user_expr
            
        return False, user_expr
    except:
        return False, user_expr

# --- GRÁFICAS INTERACTIVAS ---
def plot_function(func_expr):
    x_sym = sp.symbols('x')
    f_lamb = sp.lambdify(x_sym, func_expr, "numpy")
    
    # Rango dinámico
    x_vals = np.linspace(-6, 6, 400)
    try:
        y_vals = f_lamb(x_vals)
        # Limpiar asintotas para que la gráfica no se rompa visualmente
        threshold = 20
        y_vals[y_vals > threshold] = np.nan
        y_vals[y_vals < -threshold] = np.nan
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='f(x)', line=dict(color='#2E86C1', width=3)))
        fig.update_layout(
            title="Visualización Interactiva",
            xaxis_title="x",
            yaxis_title="f(x)",
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.write("Gráfica no disponible para esta función.")

# --- INICIALIZACIÓN DE ESTADO ---
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.results = []
    st.session_state.q_start_time = time.time()
    st.session_state.finished = False

questions = get_questions()

# --- INTERFAZ DE USUARIO ---
if not st.session_state.finished:
    q_data = questions[st.session_state.current_q]
    
    # Barra de progreso
    progress = (st.session_state.current_q) / len(questions)
    st.progress(progress)
    
    st.caption(f"Pregunta {st.session_state.current_q + 1} de {len(questions)} | Tema: {q_data['topic']}")

    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown(f"### Resuelve:")
        st.latex(q_data['latex'])
        
        st.markdown("**Tu respuesta:**")
        st.caption("Escribe la fórmula (ej: `3*x^2 + 5`). Usa `sqrt(x)` para raíces y `sen(x)` o `sin(x)`.")
        
        # Input con callback para detectar "Enter"
        user_response = st.text_input("f'(x) =", key=f"input_{st.session_state.current_q}")
        
        if st.button("Enviar Respuesta 🚀"):
            # 1. Cálculo de tiempo
            end_time = time.time()
            time_taken = end_time - st.session_state.q_start_time
            
            # 2. Validación
            is_correct, parsed_val = check_answer(user_response, q_data['correct_expr'], q_data['type'])
            
            # 3. Análisis Forense (Anti-trampa)
            flag = "NORMAL"
            if time_taken < q_data['min_seconds']:
                flag = "SOSPECHOSO (Muy rápido)"
            elif time_taken > (q_data['min_seconds'] * 8):
                flag = "LENTO (Distracción)"
                
            # Guardar datos
            st.session_state.results.append({
                "ID": q_data['id'],
                "Pregunta": q_data['latex'],
                "Tema": q_data['topic'],
                "Correcta": is_correct,
                "Tiempo (s)": round(time_taken, 1),
                "Min Esperado": q_data['min_seconds'],
                "Estado": flag,
                "Input Alumno": user_response
            })
            
            if is_correct:
                st.session_state.score += 1
                st.success("✅ ¡Correcto! Muy bien.")
            else:
                st.error(f"❌ Incorrecto. Revisa tus pasos.")
                if "hint" in q_data:
                    st.info(f"Pista: {q_data['hint']}")
            
            time.sleep(2) # Pausa para leer feedback
            
            # Avanzar
            if st.session_state.current_q < len(questions) - 1:
                st.session_state.current_q += 1
                st.session_state.q_start_time = time.time() # Reiniciar reloj
                st.rerun()
            else:
                st.session_state.finished = True
                st.rerun()

    with col2:
        if "func" in q_data:
            st.markdown('<div class="report-card">', unsafe_allow_html=True)
            plot_function(q_data['func'])
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Este ejercicio es numérico/algebraico puro y no requiere gráfica.")

else:
    # --- PANTALLA FINAL DE RESULTADOS ---
    st.balloons()
    st.title("📊 Reporte de Evaluación")
    
    score_pct = (st.session_state.score / len(questions)) * 100
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Calificación Final", f"{score_pct:.1f}%")
    c2.metric("Aciertos", f"{st.session_state.score} / {len(questions)}")
    c3.metric("Tiempo Total", f"{sum(r['Tiempo (s)'] for r in st.session_state.results) / 60:.1f} min")
    
    st.divider()
    
    st.subheader("🕵️ Auditoría de Integridad Académica")
    st.markdown("""
    Esta tabla muestra el **tiempo de reacción** por pregunta. 
    - Las filas **ROJAS** indican respuestas ingresadas inhumanamente rápido (posible copy-paste).
    - Las filas **BLANCAS** indican respuestas incorrectas.
    """)
    
    df = pd.DataFrame(st.session_state.results)
    
    # Función para colorear la tabla
    def highlight_rows(row):
        styles = []
        if "SOSPECHOSO" in row['Estado']:
            return ['background-color: #ffcccc; color: black'] * len(row)
        elif not row['Correcta']:
            return ['background-color: #f2f2f2; color: #555'] * len(row)
        else:
            return ['background-color: #ccffcc; color: black'] * len(row)

    st.dataframe(df.style.apply(highlight_rows, axis=1), use_container_width=True)
    
    # Mensaje final para el profesor
    n_sus = len(df[df['Estado'].str.contains("SOSPECHOSO")])
    if n_sus > 0:
        st.error(f"⚠️ ALERTA: Se detectaron {n_sus} respuestas sospechosas. Se recomienda revisión oral.")
    else:
        st.success("✅ INTEGRIDAD VERIFICADA: Los tiempos de respuesta son congruentes con un estudiante resolviendo los problemas manualmente.")

    if st.button("Reiniciar Examen"):
        st.session_state.clear()
        st.rerun()
