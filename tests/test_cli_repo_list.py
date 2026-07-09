from pathlib import Path

from csgpt.cli import build_parser


def test_repo_list_prints_sorted_table(tmp_path: Path, capsys) -> None:
    config_path = tmp_path / "repositories.yaml"
    config_path.write_text(
        """repositories:\n  - id: b-repo\n    name: B Repo\n    description: B repository\n    category: tooling\n    active: false\n    path: b-repo\n  - id: a-repo\n    name: A Repo\n    description: A repository\n    category: core\n    active: true\n    path: a-repo\n""",
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
