from pathlib import Path
from textwrap import dedent

from csgpt.cli import build_parser


def test_repo_list_prints_sorted_table(tmp_path: Path, capsys) -> None:
    config_path = tmp_path / "repositories.yaml"
    config_path.write_text(
        dedent("""
            repositories:
              - id: b-repo
                name: B Repo
                description: B repository
                category: tooling
                active: false
                path: b-repo
              - id: a-repo
                name: A Repo
                description: A repository
                category: core
                active: true
                path: a-repo
            """).strip() + "\n",
        encoding="utf-8",
    )

    parser = build_parser()
    args = parser.parse_args(["repo", "list", "--registry-path", str(config_path)])

    result = args.func(args)
    captured = capsys.readouterr()

    assert result == 0
    assert "ID" in captured.out
    assert "a-repo" in captured.out
    assert captured.out.index("a-repo") < captured.out.index("b-repo")
