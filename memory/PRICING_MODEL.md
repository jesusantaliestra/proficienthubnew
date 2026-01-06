# ProficientHub - Modelo de Precios y Análisis de Costos

## 1. COSTOS API (Precios Reales 2025)

### OpenAI API
| Servicio | Costo |
|----------|-------|
| GPT-4o (Input) | $2.50 / 1M tokens |
| GPT-4o (Output) | $10.00 / 1M tokens |
| GPT-4o mini (Input) | $0.15 / 1M tokens |
| GPT-4o mini (Output) | $0.60 / 1M tokens |
| Whisper STT | $0.06 / minuto |
| TTS (Text-to-Speech) | $0.24 / minuto de audio |

### ElevenLabs API (Plan Scale para volumen)
| Métrica | Costo |
|---------|-------|
| TTS por carácter | $0.00018 / carácter ($0.18/1000 chars) |
| Conversational AI | ~$0.08 / minuto |

---

## 2. ANÁLISIS DE COSTOS POR EXAMEN

### Características por Examen y Duración Total

| Examen | Reading | Listening | Speaking | Writing | Otros | **Total (min)** |
|--------|---------|-----------|----------|---------|-------|-----------------|
| TOEFL | 54 min | 41 min | 17 min | 50 min | - | **162 min** |
| IELTS | 60 min | 30 min | 14 min | 60 min | - | **164 min** |
| Cambridge | 90 min | 40 min | 15 min | 90 min | Use of English 75 min | **310 min** |
| PTE | 32 min | 45 min | - | - | Speaking+Writing 77 min | **154 min** |
| OET | 60 min | 45 min | 20 min | 45 min | - | **170 min** |

### Costo de AI por Sección (por estudiante/examen)

#### Speaking Test (STT + AI Evaluation + TTS Feedback)
```
Componentes:
1. STT (Whisper): Transcribir respuesta del estudiante
   - Duración promedio: 2-3 min por respuesta, ~5-6 respuestas = 15 min
   - Costo: 15 min × $0.06 = $0.90

2. AI Evaluation (GPT-4o): Evaluar transcripción
   - Input: ~500 tokens (transcripción + rubric)
   - Output: ~800 tokens (feedback detallado)
   - Costo: (500 × $2.50/1M) + (800 × $10/1M) = $0.00125 + $0.008 = $0.009

3. TTS Feedback (OpenAI): Leer feedback al estudiante
   - ~2 min de audio feedback
   - Costo: 2 × $0.24 = $0.48

TOTAL Speaking Test = $0.90 + $0.01 + $0.48 = **$1.39 por test**
```

#### Writing Test (AI Grading + Feedback)
```
Componentes:
1. AI Grading (GPT-4o): Evaluar essay completo
   - Input: ~1500 tokens (essay + rubric + criteria)
   - Output: ~1200 tokens (score + detailed feedback por criterio)
   - Costo: (1500 × $2.50/1M) + (1200 × $10/1M) = $0.00375 + $0.012 = $0.016

2. TTS Feedback (opcional, si incluido):
   - ~3 min de audio
   - Costo: 3 × $0.24 = $0.72

TOTAL Writing Test (sin audio) = **$0.02 por test**
TOTAL Writing Test (con audio feedback) = **$0.74 por test**

Usaremos promedio con audio básico (1 min): **$0.26 por test**
```

#### AI Tutor (Conversación)
```
Por minuto de conversación:
1. STT (si voz): $0.06
2. GPT-4o response: ~200 tokens input, ~300 tokens output
   - Costo: (200 × $2.50/1M) + (300 × $10/1M) = $0.0005 + $0.003 = $0.0035
3. TTS response: ~30 segundos = 0.5 min × $0.24 = $0.12

TOTAL por minuto (con voz) = $0.06 + $0.0035 + $0.12 = **$0.18/min**
TOTAL por minuto (solo texto) = **$0.004/min**
```

---

## 3. COSTO POR TIPO DE EXAMEN (Mock Test Completo)

### Asumiendo 1 Mock Test incluye:
- 1 Speaking Test completo
- 1 Writing Test completo  
- Reading/Listening: Solo corrección automática (sin costo AI significativo)

| Examen | Speaking Cost | Writing Cost | AI Correction | **Total Mock Test** |
|--------|---------------|--------------|---------------|---------------------|
| **TOEFL** | $1.39 (17 min) | $0.26 | $0.05 | **$1.70** |
| **IELTS** | $1.25 (14 min) | $0.26 | $0.05 | **$1.56** |
| **Cambridge** | $1.30 (15 min) | $0.52 (2 essays) | $0.08 | **$1.90** |
| **PTE** | $1.45 (combined) | $0.26 | $0.05 | **$1.76** |
| **OET** | $1.50 (20 min, medical) | $0.35 (specialized) | $0.06 | **$1.91** |

### **PROMEDIO por Mock Test = $1.77**

---

## 4. ESTRUCTURA DE PLANES POR PAQUETES DE EXÁMENES

### Objetivo de Márgenes:
- Volumen bajo (20 exámenes): 70% margen → precio = costo × 3.33
- Volumen medio (40 exámenes): 80% margen → precio = costo × 5
- Volumen alto (100 exámenes): 90% margen → precio = costo × 10

### Plan BASE (Sin AI Tutor)

| Paquete | Mock Tests | Costo Interno | Precio (Margen) | **Precio Final** | Por Examen |
|---------|------------|---------------|-----------------|------------------|------------|
| **Starter 20** | 20 | $35.40 | 70% ($35.40 × 3.33) | **$118** | $5.90 |
| **Growth 40** | 40 | $70.80 | 80% ($70.80 × 5) | **$354** | $8.85 |
| **Scale 100** | 100 | $177.00 | 90% ($177 × 10) | **$1,770** | $17.70 |

### Plan CON AI TUTOR (Minutos incluidos)

#### Cálculo AI Tutor:
- Costo real: $0.18/min (con voz) o $0.004/min (texto)
- Promedio mixto: **$0.10/min**

| Paquete | Mock Tests | Min AI Tutor | Costo Exams | Costo Tutor | Costo Total | Precio (Margen) | **Precio Final** |
|---------|------------|--------------|-------------|-------------|-------------|-----------------|------------------|
| **Starter 20 + AI** | 20 | 60 min | $35.40 | $6.00 | $41.40 | 70% | **$138** |
| **Growth 40 + AI** | 40 | 150 min | $70.80 | $15.00 | $85.80 | 80% | **$429** |
| **Scale 100 + AI** | 100 | 500 min | $177.00 | $50.00 | $227.00 | 90% | **$2,270** |

---

## 5. PAQUETES SEPARADOS DE WRITING Y SPEAKING

### Writing Test Packages (Para reventa por instituciones)

| Paquete | Tests | Costo Interno | Margen | **Precio** | Por Test | Institución cobra |
|---------|-------|---------------|--------|------------|----------|-------------------|
| Writing 20 | 20 | $5.20 | 75% | **$21** | $1.05 | $3-5 |
| Writing 50 | 50 | $13.00 | 80% | **$65** | $1.30 | $3-5 |
| Writing 100 | 100 | $26.00 | 85% | **$173** | $1.73 | $3-5 |

### Speaking Test Packages

| Paquete | Tests | Costo Interno | Margen | **Precio** | Por Test | Institución cobra |
|---------|-------|---------------|--------|------------|----------|-------------------|
| Speaking 20 | 20 | $27.80 | 75% | **$111** | $5.55 | $10-15 |
| Speaking 50 | 50 | $69.50 | 80% | **$348** | $6.96 | $10-15 |
| Speaking 100 | 100 | $139.00 | 85% | **$927** | $9.27 | $10-15 |

---

## 6. CALCULADORA ROI PARA INSTITUCIONES

### Ejemplo: Institución compra "Growth 40 + AI" por $429

**Costo por estudiante para institución:**
- Si 20 estudiantes: $429 ÷ 20 = $21.45/estudiante
- Cada estudiante recibe: 2 mock tests + ~7.5 min AI tutor

**Precio sugerido a estudiantes:** $50-80/mes

**ROI Institución:**
- Cobra $60/estudiante × 20 = $1,200
- Costo: $429
- **Ganancia: $771 (64% margen)**

---

## 7. RESUMEN DE COSTOS INTERNOS FINALES

| Concepto | Costo Real |
|----------|------------|
| Mock Test TOEFL | $1.70 |
| Mock Test IELTS | $1.56 |
| Mock Test Cambridge | $1.90 |
| Mock Test PTE | $1.76 |
| Mock Test OET | $1.91 |
| **PROMEDIO Mock Test** | **$1.77** |
| Writing Test (individual) | $0.26 |
| Speaking Test (individual) | $1.39 |
| AI Tutor (por minuto, mixto) | $0.10 |
| AI Tutor (solo texto) | $0.004 |
| AI Tutor (con voz completo) | $0.18 |

---

## 8. PRECIOS FINALES RECOMENDADOS

### Planes por Paquete de Exámenes

| Plan | Exámenes | AI Tutor | Precio USD | Precio EUR |
|------|----------|----------|------------|------------|
| **Starter** | 20 mock tests | ❌ | $118 | €109 |
| **Starter + AI** | 20 mock tests | 60 min | $138 | €128 |
| **Growth** | 40 mock tests | ❌ | $354 | €328 |
| **Growth + AI** | 40 mock tests | 150 min | $429 | €397 |
| **Scale** | 100 mock tests | ❌ | $1,770 | €1,639 |
| **Scale + AI** | 100 mock tests | 500 min | $2,270 | €2,102 |

### Add-ons

| Add-on | Cantidad | Precio |
|--------|----------|--------|
| AI Tutor Extra | 30 min | $15 |
| AI Tutor Extra | 100 min | $45 |
| Writing Tests | 20 tests | $21 |
| Speaking Tests | 20 tests | $111 |
