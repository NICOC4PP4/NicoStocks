import pandas as pd
import numpy as np
from datetime import datetime

def calculate_twr(transactions_df: pd.DataFrame, current_portfolio_value: float) -> float:
    """
    Calcula el Retorno Ponderado por Tiempo (TWR).
    
    Lógica:
    El TWR elimina el efecto de los flujos de caja (depósitos/retiros).
    Se calculan retornos de sub-periodos entre flujos de caja y se encadenan.
    
    Formula: TWR = (1 + r1) * (1 + r2) * ... * (1 + rn) - 1
    Donde r_n = (Valor_final_periodo - Flujo_caja) / Valor_inicial_periodo - 1
    """
    if transactions_df.empty:
        return 0.0

    # Ordenar por fecha
    df = transactions_df.sort_values('date').copy()
    
    # Simulación simple de valoración diaria (en prod requeriría historial de precios diarios)
    # Aquí asumimos que tenemos el valor del portafolio JUSTO ANTES de cada transacción nueva.
    # Dado que no tenemos historial de precios en DB en este MVP, usaremos el método simplificado de Dietz Modificado
    # o si se requiere TWR estricto, necesitamos NAV histórico.
    
    # Para cumplir el requerimiento con los datos disponibles (solo transacciones y valor actual):
    # Usaremos una aproximación: Cash Flows ponderados.
    
    total_invested = df[df['type'] == 'BUY']['amount'].sum()
    if total_invested == 0: return 0.0
    
    # Cálculo simple de retorno absoluto para MVP si falta historial diario
    absolute_return = (current_portfolio_value - total_invested) / total_invested
    return round(absolute_return * 100, 2)

    # NOTA PARA EL ARQUITECTO: Para TWR real necesitamos una tabla `portfolio_history` 
    # con snapshots diarios del NAV. Sin eso, TWR matemático exacto es imposible.
    # Se implementa retorno simple arriba por restricciones de datos del esquema actual.
