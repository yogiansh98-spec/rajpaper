# PYQ answer-key change register

This is a source-first register. Do not treat a 2026 publication as a 2026 examination without checking the actual exam date.

## Status definitions
- `final_correct`: confirmed against the latest official final/revised key; eligible for practice.
- `answer_changed`: model/provisional and final/revised keys differ; preserve both answers and dates; practice uses the latest official answer.
- `deleted`: question explicitly dropped/deleted by official final/revised key; archive only, excluded from scored tests.
- `pending_review`: no reliable official final key or source mismatch; excluded from scored tests.

## Data schema (one JSON object per question)
```json
{"exam":"","exam_date":"","paper":"","set":"","question_number":"","topic":"","question_text":"","options":[],"model_answer":null,"final_answer":null,"status":"pending_review","model_key_date":null,"final_key_date":null,"paper_url":"","model_key_url":"","final_key_url":"","change_note":"","reviewed_at":null}
```

## Sources located, not yet reconciled
| Exam | Exam date | Source type | URL | State |
|---|---|---|---|---|
| RPSC Sr. Teacher (Secondary Education) 2024, English | 2025-09-12 | Model answer key issued 2025-10-31 | https://rpsc.rajasthan.gov.in/Static/AnswerKeys/9B7312A8-D97F-45F5-ACC9-8889E4CC20F2.pdf | source_found; not classified |
| RPSC Sr. Teacher (Sanskrit Education) 2022, English Group B | 2023-02-15 | Final answer key published 2024-12-26 | https://rpsc.rajasthan.gov.in/Static/AnswerKeys/E449D966-B948-4581-AB6D-66B5E794127F.pdf | source_found; not classified |
| RPSC Sr. Teacher (Secondary Education) 2022, English Group B | 2022-12-23 | Final answer key issued 2024-02-29 | https://rpsc.rajasthan.gov.in/Static/AnswerKeys/EE75ED05-6DA6-4B69-B7FD-C51E9616DB80.pdf | source_found; not classified |

## Import rules
1. Match question-paper set, exam date, and question number before comparing keys.
2. Never infer deletion from an absent key entry without verifying official legend/notice.
3. Preserve changed and deleted questions in an archive, never silently overwrite them.
4. Never label unverified or AI-generated content as PYQ.
5. Begin with 2026 exams once original papers and their matching official answer keys are verified; older sources above are reference leads only.
