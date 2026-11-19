"""L2 contract unit tests for deterministic Korean/English prose_audit.py."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = PLUGIN_ROOT / "skills" / "world-class-writing" / "scripts" / "prose_audit.py"

spec = importlib.util.spec_from_file_location("prose_audit", AUDIT_SCRIPT)
assert spec is not None and spec.loader is not None
prose_audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prose_audit)


class TestProseAudit(unittest.TestCase):
    def test_ko_double_passive_blocks_with_error(self) -> None:
        text = "이 구조는 현장에서 가장 안정적인 대안으로 보여진다. 로그는 디스크에 쓰여졌다."
        rep = prose_audit.audit_text(text, genre="technical")
        self.assertFalse(rep["ok"])
        self.assertEqual(rep["scores"]["doublePassiveHits"], 2)
        rules = [f["rule"] for f in rep["findings"] if f["severity"] == "error"]
        self.assertIn("ko-double-passive", rules)

    def test_ko_valid_single_passives_do_not_false_positive(self) -> None:
        text = (
            "새 인덱스는 배치 작업으로 만들어진다. 장애 원인은 로그 분석에서 밝혀졌다. "
            "보안 규칙은 CI 단계에서 지켜진다. 트래픽은 두 리전으로 나눠진다."
        )
        rep = prose_audit.audit_text(text, genre="technical")
        self.assertEqual(rep["scores"]["doublePassiveHits"], 0)
        self.assertTrue(rep["ok"])

    def test_ko_high_density_ai_slop_blocks_p0(self) -> None:
        text = (
            "오늘날 급변하는 시장 환경에서 자동화는 중요합니다. "
            "이 변화는 단순히 비용 절감이 아니라 조직 문화의 혁신입니다. "
            "핵심은 바로 혁신적인 솔루션을 도입하는 것이라고 할 수 있습니다. "
            "앞으로의 행보가 기대됩니다."
        )
        rep = prose_audit.audit_text(text, genre="executive")
        self.assertFalse(rep["ok"])
        self.assertGreaterEqual(rep["scores"]["slopHits"], 4)
        self.assertTrue(any(f["severity"] == "error" and f["rule"].startswith("ai-slop-") for f in rep["findings"]))

    def test_en_ai_slop_and_nominalization_detection(self) -> None:
        text = (
            "In today's fast-paced world, we must delve into the tapestry of modern teams. "
            "It is important to note that this is a testament to our culture. "
            "We need to make a decision and conduct an investigation before Friday."
        )
        rep = prose_audit.audit_text(text, genre="essay")
        self.assertEqual(rep["language"], "en")
        self.assertFalse(rep["ok"])
        self.assertGreaterEqual(rep["scores"]["slopHits"], 4)
        self.assertGreaterEqual(rep["scores"]["nominalizationHits"], 2)

    def test_ko_translationese_and_ui_chaining_warnings_only(self) -> None:
        text = (
            "배포 과정에 있어서 장애가 팀에 의해 확인되었다. "
            "서비스의 아키텍처의 병목의 원인을 파악하는 것에 대해 논의했다."
        )
        rep = prose_audit.audit_text(text, genre="technical")
        self.assertTrue(rep["ok"], "Context-dependent translationese should warn without P0 exit failure.")
        self.assertGreaterEqual(rep["scores"]["translationeseHits"], 3)
        self.assertEqual(rep["scores"]["uiChainCount"], 1)
        rules = {f["rule"] for f in rep["findings"]}
        self.assertIn("ko-translationese", rules)
        self.assertIn("ko-ui-chaining", rules)

    def test_ko_end_stop_monotony_3_warns_5_blocks(self) -> None:
        warn_text = "캐시를 켰다. 지연이 줄었다. 비용도 내렸다. 오류는 없었다."
        rep_warn = prose_audit.audit_text(warn_text, genre="technical")
        self.assertTrue(rep_warn["ok"])
        self.assertEqual(rep_warn["scores"]["endingMonotonyRuns"], 1)
        self.assertTrue(any(f["rule"] == "ko-ending-monotony" and f["severity"] == "warning" for f in rep_warn["findings"]))

        err_text = "서버를 켰다. 캐시를 넣었다. 트래픽을 받았다. 경보를 닫았다. 배포를 마쳤다."
        rep_err = prose_audit.audit_text(err_text, genre="technical")
        self.assertFalse(rep_err["ok"])
        self.assertTrue(any(f["rule"] == "ko-ending-monotony" and f["severity"] == "error" for f in rep_err["findings"]))

    def test_ko_varied_formal_endings_do_not_false_positive(self) -> None:
        text = (
            "지난 분기 배포가 지연되었습니다. 핵심 원인은 스키마 누락이었습니다. "
            "다음 주부터 CI 검증을 의무화하겠습니다. 팀이 카나리 지표를 직접 확인합니다. "
            "목표는 배포 회귀율 50% 감소입니다."
        )
        rep = prose_audit.audit_text(text, genre="executive")
        self.assertTrue(rep["ok"])
        self.assertEqual(rep["scores"]["endingMonotonyRuns"], 0)

    def test_essay_bold_bullet_bloat_blocks_but_technical_allows(self) -> None:
        bullet_doc = (
            "## 핵심 구조\n\n"
            "- **속도:** 응답 시간을 40ms 이하로 유지합니다.\n"
            "- **안정성:** 재시도 한도를 3회로 제한합니다.\n"
            "- **관측성:** 모든 요청에 추적 ID를 부여합니다.\n"
            "- **복구:** 카나리 오류율 1% 초과 시 자동 롤백합니다.\n"
        )
        rep_essay = prose_audit.audit_text(bullet_doc, genre="essay")
        self.assertFalse(rep_essay["ok"])
        self.assertTrue(any(f["rule"] == "essay-bold-bullet-bloat" and f["severity"] == "error" for f in rep_essay["findings"]))

        rep_tech = prose_audit.audit_text(bullet_doc, genre="technical")
        self.assertTrue(rep_tech["ok"])

    def test_markdown_masking_ignores_frontmatter_code_quotes_and_urls(self) -> None:
        doc = (
            "---\n"
            "title: 오늘날 급변하는 테스트\n"
            "---\n\n"
            "# 배포 자동화가 회귀 결함을 42% 줄인 이유\n\n"
            "```python\n"
            "# 보여진다 쓰여진다 delve tapestry 오늘날 급변하는\n"
            "msg = '단순히 A가 아니라 B'\n"
            "```\n\n"
            "> 인용문: 이 문서는 보여진다. 오늘날 급변하는 시대이다.\n\n"
            "우리 팀은 `prose_audit.py`와 https://example.com/delve/tapestry 링크를 참고해 "
            "배포 시간을 12분에서 3분으로 단축했다. 장애 건수도 분기 14건에서 4건으로 줄었다.\n"
        )
        rep = prose_audit.audit_text(doc, genre="technical")
        self.assertTrue(rep["ok"], f"Unexpected findings from masked regions: {rep['findings']}")
        self.assertEqual(rep["scores"]["doublePassiveHits"], 0)
        self.assertEqual(rep["scores"]["slopHits"], 0)
        self.assertGreaterEqual(rep["stats"]["concreteAnchors"], 4)

    def test_generic_heading_detection(self) -> None:
        doc = "# 서론\n\n팀은 배포 파이프라인을 15분에서 4분으로 단축했다.\n\n## 결론\n\n다음 주 수요일부터 적용한다.\n"
        rep = prose_audit.audit_text(doc, genre="executive")
        self.assertEqual(rep["scores"]["genericHeadingCount"], 2)
        self.assertTrue(all(f["severity"] == "warning" for f in rep["findings"] if f["rule"] == "generic-heading"))

    def test_concrete_anchors_detected_in_korean_particles(self) -> None:
        doc = "배포 지연은 40%를 줄였고, 120ms에 응답하며, 2026년 11월 기준 월 15건의 오류를 막았다."
        rep = prose_audit.audit_text(doc, genre="executive")
        self.assertGreaterEqual(rep["stats"]["concreteAnchors"], 4)

    def test_cli_compare_mode_and_strict_flag(self) -> None:
        v1 = (
            "# 배경\n\n"
            "오늘날 급변하는 환경에 있어서 코드 리뷰는 매우 중요합니다. "
            "이 문제는 단순히 속도의 문제가 아니라 품질의 문제라고 할 수 있습니다. "
            "자동화 도구가 필수적이라고 보여진다. 앞으로의 개선이 기대됩니다.\n"
        )
        v2 = (
            "# 사전 정적 검증이 PR 리뷰 대기 시간을 18시간에서 4시간으로 줄인다\n\n"
            "지난 3분기 배포 지연 27건 중 19건은 병합 직전 스타일·스키마 오류에서 발생했다. "
            "사전 검증 스크립트를 CI에 넣으면 사람은 아키텍처와 실패 모드 판단에만 집중할 수 있다.\n\n"
            "다만 초기 규칙 튜닝에 엔지니어 1명의 3일이 든다. "
            "초기 2주는 경고 모드로 운영해 오탐률이 5% 이하로 내려간 뒤 차단 모드로 전환하자.\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            p1 = pathlib.Path(tmp) / "v1.md"
            p2 = pathlib.Path(tmp) / "v2.md"
            p1.write_text(v1, encoding="utf-8")
            p2.write_text(v2, encoding="utf-8")

            proc_v1 = subprocess.run(
                [sys.executable, str(AUDIT_SCRIPT), str(p1), "--genre", "executive"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_v1.returncode, 1)

            proc_cmp = subprocess.run(
                [sys.executable, str(AUDIT_SCRIPT), "--compare", str(p1), str(p2), "--genre", "executive", "--strict"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc_cmp.returncode, 0, proc_cmp.stdout + proc_cmp.stderr)
            payload = json.loads(proc_cmp.stdout)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["improved"])
            self.assertLess(payload["delta"]["slopDelta"], 0)
            self.assertLess(payload["delta"]["doublePassiveDelta"], 0)
            self.assertGreater(payload["delta"]["concreteAnchorDelta"], 0)

    def test_cli_stdin_mode(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(AUDIT_SCRIPT), "--stdin", "--genre", "general"],
            input="첫 문장부터 결론을 말한다. 2026년 11월 테스트는 12ms에 통과했다.\n",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["source"], "<stdin>")
        self.assertTrue(data["ok"])

    def test_low_burstiness_and_monotonous_cadence_detection(self) -> None:
        doc = (
            "첫 번째 문장은 길이를 비슷하게 맞추어 작성합니다. "
            "두 번째 문장도 비슷한 글자 수로 조용히 이어집니다. "
            "세 번째 문장 역시 거의 동일한 호흡을 유지합니다. "
            "네 번째 문장까지 같은 길이 패턴으로 흘러가네요. "
            "다섯 번째 문장도 비슷한 길이의 평서문으로 끝납니다. "
            "여섯 번째 문장 역시 단조로운 리듬을 그대로 반복해요."
        )
        rep = prose_audit.audit_text(doc, genre="essay")
        rules = {f["rule"] for f in rep["findings"]}
        self.assertIn("low-burstiness", rules)
        self.assertIn("monotonous-cadence-run", rules)

    def test_zero_concrete_anchors_triggers_hayakawa_warning(self) -> None:
        abstract_para = (
            "조직의 성장은 구성원의 자발적 몰입과 상호 신뢰에서 비롯된다. "
            "리더는 명확한 방향을 제시하고 열린 대화를 장려해야 한다. "
            "장기적 관점에서 학습 문화가 자리 잡으면 변화 대응력이 높아진다. "
            "각 팀은 공동 목표를 중심으로 협업하며 지속적 개선을 추구한다. "
            "이 과정은 조직 전체의 회복 탄력성을 높이는 토대가 된다. "
            "결국 사람의 역량과 일하는 방식의 조화가 경쟁력을 가른다. "
            "불확실성이 클수록 원칙에 기반한 판단과 투명한 공유가 빛난다. "
            "작은 실험을 꾸준히 이어가면 팀의 실행 역량이 단단해진다. "
            "서로의 맥락을 존중할 때 더 나은 의사결정이 자연스럽게 나온다. "
            "꾸준한 성찰과 피드백은 조직이 올바른 방향을 지키게 돕는다. "
            "결국 좋은 문화는 제도가 아니라 매일의 습관에서 자란다. "
            "구성원이 스스로 문제를 정의하고 해법을 찾는 환경이 중요하다. "
            "협업의 품질은 소통의 빈도가 아니라 신뢰의 깊이에서 갈린다. "
            "미래를 준비하는 팀은 단기 성과와 장기 역량의 균형을 맞춘다. "
            "변화를 두려워하지 않는 태도가 조직의 지속 가능성을 지탱한다."
        )
        self.assertGreaterEqual(len(abstract_para), 500)
        rep = prose_audit.audit_text(abstract_para, genre="executive")
        self.assertEqual(rep["stats"]["concreteAnchors"], 0)
        self.assertTrue(any(f["rule"] == "low-concreteness" for f in rep["findings"]))


if __name__ == "__main__":
    unittest.main()
