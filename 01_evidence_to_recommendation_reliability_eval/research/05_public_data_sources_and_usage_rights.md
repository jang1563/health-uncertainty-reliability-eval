# Public Data Sources And Usage Rights

- checked_on: `2026-04-10`
- project: `Evidence-to-Recommendation Reliability Eval`

## 요약

v1은 `USPSTF + AHRQ + MedlinePlus` 조합으로 가되, benchmark row 자체는 `paraphrase-first structured dataset`로 설계하는 것이 가장 안전하다.

## source-by-source classification

| source | exact_url | classification | 사용 원칙 | 메모 |
|---|---|---|---|---|
| USPSTF grade definitions | https://www.uspreventiveservicestaskforce.org/uspstf/grade-definitions | `paraphrase only` | 등급 의미를 짧게 구조화해서 재기술하고 원문 장문 복사는 피함 | 등급 정의는 핵심 source of truth |
| USPSTF recommendation topics | https://www.uspreventiveservicestaskforce.org/uspstf/recommendation-topics | `paraphrase only` | topic, population, release date, URL 메타데이터만 구조화 | topic sampling의 canonical source |
| USPSTF recommendation statement copyright block, representative example | https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/oral-health-adults-screening-preventive-interventions | `short quote only` | public repo에서 adaptation disclaimer 문구를 참고하되 인용은 최소화 | representative current statement page에 copyright and adaptation notice가 노출됨 |
| AHRQ shared decision making | https://www.ahrq.gov/sdm/about/index.html | `paraphrase only` | rubric 원칙 derivation에만 사용 | mixed web assets 가능성 때문에 보수적으로 운영 |
| AHRQ SHARE approach | https://www.ahrq.gov/evidencenow/tools/share-approach.html | `paraphrase only` | preference-sensitive communication rubric에 반영 | dataset row에 원문 장문 복사 금지 |
| MedlinePlus content policy | https://medlineplus.gov/about/using/usingcontent/ | `short quote only` | public-domain 범위 확인용 정책 source | 어떤 content가 public domain인지 구분하는 기준 |
| MedlinePlus developer info | https://medlineplus.gov/about/developers/webservices/ | `safe to redistribute` for metadata only | topic identifiers, links, XML/web-service metadata 사용 | benchmark linking and metadata support |
| MedlinePlus health topic summaries and medical test pages | https://medlineplus.gov/ | `safe to redistribute` within policy scope | public-domain으로 명시된 summary/test content만 patient-friendly phrasing 참고 또는 짧은 derived summary 작성 | drug monograph와 encyclopedia는 제외 |

## 실무 규칙

### dataset row에 넣어도 되는 것

- source topic title
- source URL
- release date
- grade
- human-authored summary sentence
- human-authored expected posture
- human-authored required points

### dataset row에 넣지 않는 것

- USPSTF recommendation statement 장문 원문
- AHRQ 설명 페이지 장문 원문
- MedlinePlus copyrighted content
- MedlinePlus drug monographs
- A.D.A.M. encyclopedia content

## public repo disclaimer 초안

`This benchmark paraphrases public preventive-care recommendations and communication guidance for evaluation research. Source pages remain the authoritative reference. USPSTF content is cited to the original USPSTF pages, and any adapted summaries in this repository are the authors' own responsibility and do not imply endorsement by AHRQ, USPSTF, HHS, or NLM.`

## 최종 결론

- 데이터셋은 `source text redistribution project`가 아니라 `structured evaluation artifact`로 운영해야 한다.
- source fidelity는 `links + metadata + paraphrased benchmark rows`로 확보한다.
