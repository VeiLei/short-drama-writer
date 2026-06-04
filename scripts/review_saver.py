"""Save review reports and write back review metrics."""

import json
import os
from datetime import datetime


class ReviewSaver:
    def __init__(self, project_root: str):
        self.review_dir = os.path.join(project_root, "审查报告")
        os.makedirs(self.review_dir, exist_ok=True)

    def save_review(self, episode_id: str, review_json: str):
        """Save review JSON and generate a markdown report."""
        review = json.loads(review_json)
        ep_num = episode_id.zfill(4) if episode_id.isdigit() else episode_id
        fname = f"第{ep_num}集审查报告.md"

        # Build markdown report
        lines = [
            f"# 第{ep_num}集审查报告",
            f"审查时间：{datetime.now().isoformat()}",
            "",
            f"## 摘要",
            f"问题总数：{len(review.get('issues', []))}",
        ]

        blocking = [i for i in review.get("issues", []) if i.get("blocking")]
        lines.append(f"阻塞问题：{len(blocking)}")

        for severity in ["critical", "high", "medium", "low"]:
            issues = [i for i in review.get("issues", [])
                      if i.get("severity") == severity]
            if issues:
                lines.append(f"\n## {severity.upper()} ({len(issues)}个)")
                for idx, issue in enumerate(issues, 1):
                    lines.append(f"\n### {idx}. [{issue.get('category')}] {issue.get('description')}")
                    lines.append(f"- **位置**: {issue.get('location')}")
                    lines.append(f"- **证据**: {issue.get('evidence')}")
                    lines.append(f"- **修复方向**: {issue.get('fix_hint')}")
                    lines.append(f"- **阻塞**: {'是' if issue.get('blocking') else '否'}")

        report = "\n".join(lines)
        fpath = os.path.join(self.review_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(report)

        # Also save raw JSON
        json_path = fpath.replace(".md", ".json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(review, f, ensure_ascii=False, indent=2)

        print(f"Review saved to {fpath}")
        return fpath

    def get_review(self, episode_id: str) -> str | None:
        ep_num = episode_id.zfill(4) if episode_id.isdigit() else episode_id
        json_path = os.path.join(self.review_dir, f"第{ep_num}集审查报告.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                return f.read()
        return None
