# Public Data Sources And Usage Rights

- checked_on: `2026-04-10`
- project: `Drug Safety Update Sensitivity Eval`

## 요약

v1은 `FDA Drug Safety Communications + SrLC + openFDA`를 중심에 두고, benchmark row는 `human-written normalized summaries`로 만드는 것이 가장 안전하다. `DailyMed`는 링크와 식별자 매핑에만 보수적으로 사용한다.

## source-by-source classification

| source | exact_url | classification | 사용 원칙 | 메모 |
|---|---|---|---|---|
| openFDA terms | https://open.fda.gov/terms/ | `safe to redistribute` for metadata | API metadata, queries, identifiers 사용 가능 | source text 장문 복사보다는 metadata 중심 |
| openFDA drug label API | https://open.fda.gov/apis/drug/label/ | `safe to redistribute` for metadata | spl_set_id, application number, section presence, identifiers 수집 | machine-readable linkage layer |
| openFDA drugs@FDA API | https://open.fda.gov/apis/drug/drugsfda/ | `safe to redistribute` for metadata | NDA/BLA eligibility 확인, approval history 확인 | regulatory product eligibility source |
| FDA Drug Safety Communications | https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications | `paraphrase only` | update event 요약을 human-written normalized summary로 작성 | long-copy 금지 |
| FDA SrLC overview | https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-related-labeling-changes-srlc-database-overview-updates-safety-information-fda-approved | `paraphrase only` | database 사용 맥락과 section-level change reference | rights는 보수적으로 운영 |
| FDA SrLC search entry | https://www.accessdata.fda.gov/scripts/cder/safetylabelingchanges/ | `link only` | case link와 update event lookup에 사용 | canonical change record pointer |
| DailyMed home/about | https://dailymed.nlm.nih.gov/dailymed/index.cfm | `link only` | current label URL, setid mapping, manual verification | benchmark text source로 쓰지 않음 |

## 실무 규칙

### dataset item에 넣어도 되는 것

- drug name
- active ingredient
- application type
- update date
- section changed
- source URLs
- openFDA query string
- human-authored `before_packet`
- human-authored `after_packet`
- human-authored `expected_answer_shift`

### dataset item에 넣지 않는 것

- FDA communication 장문 원문 복사
- DailyMed full label section 복사
- label XML의 긴 원문 section dump

## protocol rights-safe design

이 benchmark는 source text를 그대로 재배포하지 않는다. 대신 아래 방식으로 구현한다.

1. `before_packet`: 규제 업데이트 전 상태를 human-authored summary로 작성
2. `after_packet`: 새로운 FDA update를 반영한 human-authored summary로 작성
3. source URL은 모두 보존
4. source text 자체는 canonical reference로만 사용

## 최종 결론

- 이 프로젝트는 `openFDA metadata-driven benchmark`로 설계하는 것이 안전하다.
- source fidelity는 `metadata + links + normalized evidence packet` 구조로 확보한다.
