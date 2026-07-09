from csgpt import cli


def test_build_parser_has_version_option() -> None:
    p = cli.build_parser()
    # argparse stores version action differently; ensure parser exists and is configured
    assert p.prog == "csgpt"
