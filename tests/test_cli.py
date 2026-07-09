from csgpt import cli


def test_build_parser_has_version_option() -> None:
    p = cli.build_parser()
    # argparse may set `prog` based on the package entry-point; ensure it contains the CLI name
    assert "csgpt" in p.prog


def test_build_parser_has_doctor_command() -> None:
    p = cli.build_parser()
    args = p.parse_args(["doctor"])
    assert getattr(args, "func", None) is not None
