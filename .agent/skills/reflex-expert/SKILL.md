---
name: reflex-expert
description: Experto en el framework Reflex (Python puro) para aplicaciones web full-stack.
---

# Reglas de Desarrollo Reflex

1. **Estructura**: Separa siempre la UI (`pages/`) de la lógica (`state.py`).
2. **Estado**: Usa `rx.State` para variables reactivas. No uses variables globales fuera del State.
3. **Componentes**: Prefiere componentes pequeños y reutilizables.
4. **Estilo**: Usa `rx.box`, `rx.flex`, `rx.vstack` para layout en lugar de CSS crudo siempre que sea posible.
5. **Base de Datos**: Las consultas a DB (Supabase) deben ser métodos asíncronos dentro de la clase State o servicios externos llamados por el State.
