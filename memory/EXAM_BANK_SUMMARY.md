# ProficientHub - PRD Update

## Exam Bank Summary (January 2025)

### Total Exams Available: 100 (20 per exam type)

| Exam Type | Total Exams | Reading Passages | Writing Tasks | Speaking Prompts |
|-----------|-------------|------------------|---------------|------------------|
| IELTS | 20 | 60+ passages | 40 tasks | 40+ prompts |
| TOEFL | 20 | 40+ passages | 40 tasks | 20+ prompts |
| Cambridge | 20 | 40+ passages | 20 tasks | 20+ prompts |
| PTE | 20 | 40+ passages | 20 tasks | 20+ prompts |
| OET | 20 | 40+ passages | 20 tasks | 20+ role-plays |

### API Endpoints for Exams

- `GET /api/exams/types` - All exam types with 20 exams each
- `GET /api/exams/{exam_type}/available` - List of 20 available exams
- `GET /api/exams/{exam_type}/full/{exam_number}` - Complete exam (1-20)
- `GET /api/exams/{exam_type}/mock-test?exam_number=N` - Mock test for exam N
- `GET /api/exams/{exam_type}/practice` - Practice questions
- `GET /api/exams/{exam_type}/speaking-prompts` - Speaking prompts
- `GET /api/exams/{exam_type}/writing-tasks` - Writing tasks

### File Structure

```
/app/backend/
├── exam_questions.py      # Main loader
└── exam_banks/
    ├── __init__.py
    ├── ielts_bank.py      # 20 IELTS exams (40KB)
    ├── toefl_bank.py      # 20 TOEFL exams (30KB)
    └── other_exams_bank.py # Cambridge, PTE, OET (34KB)
```

### Content Types

**Reading Passages Cover:**
- Science & Technology (AI, climate, biology)
- Social Sciences (psychology, economics, history)
- Arts & Culture
- Health & Medicine
- Environment & Sustainability
- Business & Economics

**Writing Tasks Include:**
- IELTS Task 1 (graphs, charts, processes)
- IELTS Task 2 (opinion essays)
- TOEFL Independent essays
- TOEFL Integrated tasks
- Cambridge essays, reports, reviews
- PTE summarize, essays
- OET referral letters

**Speaking Topics:**
- Personal experiences
- Abstract discussions
- Academic topics
- Role-plays (OET healthcare)
