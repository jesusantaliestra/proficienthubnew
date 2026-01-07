# ProficientHub - Análisis de Costes Internos (CONFIDENCIAL)

Este documento es **INTERNO** y no debe mostrarse a clientes.

---

## 1. Costes por Tipo de Examen (Mock Test)

| Examen | Speaking (min) | Writing Tasks | Coste Interno |
|--------|----------------|---------------|---------------|
| TOEFL  | 17 min         | 2             | $0.92         |
| IELTS  | 14 min         | 2             | $0.82         |
| Cambridge | 15 min      | 2             | $0.95         |
| PTE    | 20 min         | 2             | $0.98         |
| OET    | 20 min         | 1             | $1.02         |

**Promedio ponderado por mock test: $0.94**

---

## 2. Costes Individuales de Tests

| Servicio | Coste Interno | Componentes |
|----------|---------------|-------------|
| Writing Test | $0.05 | GPT-4 evaluation |
| Speaking Test | $0.85 | STT ($0.30) + TTS ($0.20) + AI eval ($0.35) |
| AI Tutor (voz/min) | $0.18 | STT + TTS + GPT streaming |
| AI Tutor (mixto/min) | $0.06 | GPT streaming only |

---

## 3. Planes de Exámenes - Estructura de Costes

| Plan | Exámenes/Licencia | Coste Base Interno |
|------|-------------------|-------------------|
| plan_5 | 5 | $4.70 |
| plan_10 | 10 | $9.40 |
| plan_20 | 20 | $18.80 |
| plan_40 | 40 | $37.60 |
| plan_60 | 60 | $56.40 |
| plan_100 | 100 | $94.00 |

---

## 4. Multiplicadores de Precio por Volumen de Licencias

| Tier | Rango Licencias | Multiplicador | Descuento | Margen Estimado |
|------|-----------------|---------------|-----------|-----------------|
| tier_100 | 1-100 | 2.00x | 0% | ~50% |
| tier_500 | 101-500 | 1.85x | 7% | ~46% |
| tier_1000 | 501-1,000 | 1.72x | 14% | ~42% |
| tier_2000 | 1,001-2,000 | 1.60x | 20% | ~37% |
| tier_5000 | 2,001-5,000 | 1.50x | 25% | ~33% |
| tier_10000 | 5,001-10,000 | 1.42x | 29% | ~30% |
| tier_100000 | 10,001-100,000 | 1.35x | 32% | ~26% |

---

## 5. AI Tutor Add-on - Costes y Precios

| Opción | Minutos | Coste Interno | Precio Venta | Margen |
|--------|---------|---------------|--------------|--------|
| none | 0 | $0 | $0 | - |
| basic | 30 | $1.80 | $5.00 | 64% |
| standard | 60 | $3.60 | $9.00 | 60% |
| premium | 120 | $7.20 | $15.00 | 52% |
| unlimited | 300 | $18.00 | $35.00 | 49% |

---

## 6. Paquetes Writing/Speaking - Precios Mayoristas

### Writing Tests
| Cantidad | Coste Interno | Precio Venta | Margen |
|----------|---------------|--------------|--------|
| 100 | $5.00 | $150 | 97% |
| 500 | $25.00 | $625 | 96% |
| 1,000 | $50.00 | $1,100 | 95% |
| 5,000 | $250.00 | $4,750 | 95% |
| 10,000 | $500.00 | $8,500 | 94% |

### Speaking Tests
| Cantidad | Coste Interno | Precio Venta | Margen |
|----------|---------------|--------------|--------|
| 100 | $85 | $350 | 76% |
| 500 | $425 | $1,500 | 72% |
| 1,000 | $850 | $2,700 | 69% |
| 5,000 | $4,250 | $11,500 | 63% |
| 10,000 | $8,500 | $20,000 | 58% |

---

## 7. Fórmula de Cálculo de Precios

```
Precio por Licencia = (Coste_Plan × Multiplicador_Volumen) + Precio_AI_Tutor

Ejemplo: Plan 20 exams + AI Standard + 500 licencias
= ($18.80 × 1.85) + $9.00
= $34.78 + $9.00
= $43.78 por licencia
```

---

**Última actualización:** Enero 2025
