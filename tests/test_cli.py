from click.testing import CliRunner

from ais_tools.cli import cli
from ais_tools.cli import add_tagblock


def test_add_tagblock():
    runner = CliRunner()
    input = '!AIVDM123'
    result = runner.invoke(add_tagblock, input=input)
    assert not result.exception
    assert result.output == 'command not implemented\n'