#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 15:12:52 2024

@author: juliansanchez

"""
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# Conectar a la base de datos SQLite
conn = sqlite3.connect('health_tracker.db')
c = conn.cursor()

# Crear tablas si no existen
def create_tables():
    c.execute('''
    CREATE TABLE IF NOT EXISTS RegistroDiario (
        id INTEGER PRIMARY KEY,
        fecha DATE NOT NULL,
        calificacion_sueno INTEGER,
        horas_sueno TEXT,
        tipo_ejercicio TEXT,
        intensidad_ejercicio TEXT,
        cantidad_agua TEXT,
        bebidas_embrigantes TEXT,
        tipo_bebida TEXT,
        peso REAL,
        puntuacion_corporal REAL
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS Comida (
        id INTEGER PRIMARY KEY,
        registro_diario_id INTEGER,
        fecha DATE NOT NULL,
        tipo_comida TEXT,
        descripcion TEXT,
        FOREIGN KEY (registro_diario_id) REFERENCES RegistroDiario(id)
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS Medida (
        id INTEGER PRIMARY KEY,
        registro_diario_id INTEGER,
        fecha DATE NOT NULL,
        hora TIME NOT NULL,
        glucosa REAL,
        ua REAL,
        FOREIGN KEY (registro_diario_id) REFERENCES RegistroDiario(id)
    )
    ''')
    conn.commit()

# Crear las tablas si no existen
create_tables()

st.title('Health Tracker')

# Mostrar imagen más pequeña como logo
st.image('healthy_lifestyle_logo.png', width=200)

# Formulario para ingresar datos
st.header('Registro Diario')
fecha_diario = st.date_input('Fecha')
calificacion_sueno = st.number_input('Calificación del Sueño', min_value=0, max_value=100, step=1)
horas_sueno = st.text_input('Horas de Sueño')
tipo_ejercicio = st.text_input('Tipo de Ejercicio Realizado')
intensidad_ejercicio = st.selectbox('Intensidad del Ejercicio', ['Ninguna','Baja', 'Moderada', 'Alta'])
cantidad_agua = st.selectbox('Cantidad de Agua', ['Poca', 'Moderada', 'Bastante'])
bebidas_embrigantes = st.selectbox('Bebidas Embriagantes', ['Ninguna', 'Poca', 'Moderada', 'Bastante'])
tipo_bebida = st.text_input('Tipo de Bebida Embriagante')
peso = st.number_input('Peso (kg)', min_value=0.0, step=0.1)
puntuacion_corporal = st.number_input('Puntuación Corporal', min_value=0.0, step=0.1)

if st.button('Guardar Registro Diario'):
    c.execute('''
    INSERT INTO RegistroDiario (fecha, calificacion_sueno, horas_sueno, tipo_ejercicio, intensidad_ejercicio, cantidad_agua, bebidas_embrigantes, tipo_bebida, peso, puntuacion_corporal)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (fecha_diario, calificacion_sueno, horas_sueno, tipo_ejercicio, intensidad_ejercicio, cantidad_agua, bebidas_embrigantes, tipo_bebida, peso, puntuacion_corporal))
    conn.commit()
    st.success('Registro diario guardado exitosamente!')

st.header('Comidas')
fecha_comida = st.date_input('Fecha de la Comida')
tipo_comida = st.selectbox('Tipo de Comida', ['Desayuno', 'Almuerzo', 'Cena'])
descripcion_comida = st.text_area('Descripción de la Comida')

if st.button('Guardar Comida'):
    c.execute('SELECT id FROM RegistroDiario WHERE fecha = ? ORDER BY id DESC LIMIT 1', (fecha_comida,))
    result = c.fetchone()
    if result:
        registro_diario_id = result[0]
        c.execute('''
        INSERT INTO Comida (registro_diario_id, fecha, tipo_comida, descripcion)
        VALUES (?, ?, ?, ?)
        ''', (registro_diario_id, fecha_comida, tipo_comida, descripcion_comida))
        conn.commit()
        st.success('Comida guardada exitosamente!')
    else:
        st.error('No se encontró un registro diario para la fecha seleccionada.')

st.header('Mediciones de Glucosa y Ácido Úrico')
fecha_medida = st.date_input('Fecha de la Medición')
hora_medida = st.time_input('Hora de la Medición').strftime('%H:%M:%S')
glucosa = st.number_input('Medida de Glucosa', min_value=0.0, step=0.1)
ua = st.number_input('Medida de Ácido Úrico', min_value=0.0, step=0.1)

if st.button('Guardar Medición'):
    c.execute('SELECT id FROM RegistroDiario WHERE fecha = ? ORDER BY id DESC LIMIT 1', (fecha_medida,))
    result = c.fetchone()
    if result:
        registro_diario_id = result[0]
        c.execute('''
        INSERT INTO Medida (registro_diario_id, fecha, hora, glucosa, ua)
        VALUES (?, ?, ?, ?, ?)
        ''', (registro_diario_id, fecha_medida, hora_medida, glucosa, ua))
        conn.commit()
        st.success('Medición guardada exitosamente!')
    else:
        st.error('No se encontró un registro diario para la fecha seleccionada.')

# Mostrar registros
st.header('Registros')
df_diario = pd.read_sql_query('SELECT * FROM RegistroDiario', conn)
df_comidas = pd.read_sql_query('SELECT * FROM Comida', conn)
df_medidas = pd.read_sql_query('SELECT * FROM Medida', conn)
st.subheader('Registro Diario')
st.write(df_diario)
st.subheader('Comidas')
st.write(df_comidas)
st.subheader('Mediciones')
st.write(df_medidas)

# Módulo de Visualización
st.header('Visualización de Datos')

# Filtros para segmentar los datos
st.sidebar.header('Filtros')
fecha_inicio, fecha_fin = st.sidebar.date_input('Intervalo de Fechas', [datetime.now(), datetime.now()])
tipo_comida_seleccionada = st.sidebar.multiselect('Tipo de Comida', df_comidas['tipo_comida'].unique())
intensidad_ejercicio_seleccionada = st.sidebar.multiselect('Intensidad del Ejercicio', df_diario['intensidad_ejercicio'].unique())

# Filtrar los datos según los filtros seleccionados
if fecha_inicio and fecha_fin:
    df_diario = df_diario[(df_diario['fecha'] >= str(fecha_inicio)) & (df_diario['fecha'] <= str(fecha_fin))]
    df_comidas = df_comidas[df_comidas['registro_diario_id'].isin(df_diario['id'])]
    df_medidas = df_medidas[df_medidas['registro_diario_id'].isin(df_diario['id'])]

if tipo_comida_seleccionada:
    df_comidas = df_comidas[df_comidas['tipo_comida'].isin(tipo_comida_seleccionada)]

if intensidad_ejercicio_seleccionada:
    df_diario = df_diario[df_diario['intensidad_ejercicio'].isin(intensidad_ejercicio_seleccionada)]
    df_comidas = df_comidas[df_comidas['registro_diario_id'].isin(df_diario['id'])]
    df_medidas = df_medidas[df_medidas['registro_diario_id'].isin(df_diario['id'])]

# Gráficos interactivos
st.subheader('Gráficos Interactivos')
fig1 = px.line(df_medidas, x='fecha', y='glucosa', title='Niveles de Glucosa a lo largo del tiempo')
st.plotly_chart(fig1)

fig2 = px.line(df_medidas, x='fecha', y='ua', title='Niveles de Ácido Úrico a lo largo del tiempo')
st.plotly_chart(fig2)

# Funcionalidad para resetear la base de datos
def deep_reset():
    c.execute('DROP TABLE IF EXISTS RegistroDiario')
    c.execute('DROP TABLE IF EXISTS Comida')
    c.execute('DROP TABLE IF EXISTS Medida')
    create_tables()
    st.success('Base de datos reiniciada completamente.')

def soft_reset():
    c.execute('DELETE FROM RegistroDiario')
    c.execute('DELETE FROM Comida')
    c.execute('DELETE FROM Medida')
    conn.commit()
    st.success('Todos los registros eliminados, pero las tablas se mantienen.')


# Botones para resetear la base de datos

#if st.button('Reseteo Profundo (Eliminar y Recrear Tablas)'):
#    deep_reset()

#if st.button('Reseteo Suave (Eliminar Registros)'):
#    soft_reset()


# Botón para activar la funcionalidad de edición
if 'editar' not in st.session_state:
    st.session_state.editar = False

if st.button('Editar/Eliminar Registro Diario'):
    st.session_state.editar = not st.session_state.editar

if st.session_state.editar:
    st.header('Actualizar o Eliminar Registro Diario')
    registros_disponibles = df_diario['id'].tolist()
    registro_id = st.selectbox('Seleccionar Registro ID para actualizar', registros_disponibles, key='select_registro')

    registro_a_actualizar = df_diario[df_diario['id'] == registro_id]

    if not registro_a_actualizar.empty:
        fecha_actualizar = st.date_input('Fecha', value=pd.to_datetime(registro_a_actualizar['fecha'].values[0]), key='fecha')
        calificacion_sueno_actualizar = st.number_input('Calificación del Sueño', min_value=0, max_value=100, step=1, value=int(registro_a_actualizar['calificacion_sueno'].values[0]), key='calificacion_sueno')
        horas_sueno_actualizar = st.text_input('Horas de Sueño', value=registro_a_actualizar['horas_sueno'].values[0], key='horas_sueno')
        tipo_ejercicio_actualizar = st.text_input('Tipo de Ejercicio Realizado', value=registro_a_actualizar['tipo_ejercicio'].values[0], key='tipo_ejercicio')
        intensidad_ejercicio_actualizar = st.selectbox('Intensidad del Ejercicio', ['Ninguna','Baja', 'Moderada', 'Alta'], index=['Ninguna','Baja', 'Moderada', 'Alta'].index(registro_a_actualizar['intensidad_ejercicio'].values[0]), key='intensidad_ejercicio')
        cantidad_agua_actualizar = st.selectbox('Cantidad de Agua', ['Poca', 'Moderada', 'Bastante'], index=['Poca', 'Moderada', 'Bastante'].index(registro_a_actualizar['cantidad_agua'].values[0]), key='cantidad_agua')
        bebidas_embrigantes_actualizar = st.selectbox('Bebidas Embriagantes', ['Ninguna', 'Poca', 'Moderada', 'Bastante'], index=['Ninguna', 'Poca', 'Moderada', 'Bastante'].index(registro_a_actualizar['bebidas_embrigantes'].values[0]), key='bebidas_embrigantes')
        tipo_bebida_actualizar = st.text_input('Tipo de Bebida Embriagante', value=registro_a_actualizar['tipo_bebida'].values[0], key='tipo_bebida')
        peso_actualizar = st.number_input('Peso (kg)', min_value=0.0, step=0.1, value=float(registro_a_actualizar['peso'].values[0]), key='peso')
        puntuacion_corporal_actualizar = st.number_input('Puntuación Corporal', min_value=0.0, step=0.1, value=float(registro_a_actualizar['puntuacion_corporal'].values[0]), key='puntuacion_corporal')

        if st.button('Actualizar Registro Diario'):
            c.execute('''
            UPDATE RegistroDiario
            SET fecha = ?, calificacion_sueno = ?, horas_sueno = ?, tipo_ejercicio = ?, intensidad_ejercicio = ?, cantidad_agua = ?, bebidas_embrigantes = ?, tipo_bebida = ?, peso = ?, puntuacion_corporal = ?
            WHERE id = ?
            ''', (fecha_actualizar, calificacion_sueno_actualizar, horas_sueno_actualizar, tipo_ejercicio_actualizar, intensidad_ejercicio_actualizar, cantidad_agua_actualizar, bebidas_embrigantes_actualizar, tipo_bebida_actualizar, peso_actualizar, puntuacion_corporal_actualizar, registro_id))
            conn.commit()
            st.success('Registro diario actualizado exitosamente!')

        if st.button('Eliminar Registro Diario'):
            c.execute('DELETE FROM RegistroDiario WHERE id = ?', (registro_id,))
            conn.commit()
            st.success('Registro diario eliminado exitosamente!')

conn.close()








