from click.testing import CliRunner
from ais_tools.cli import update_tagblock

#issue 40 Update-tagblock fails on malformed group field in tagblock
# https://github.com/GlobalFishingWatch/ais-tools/issues/40

def test_issue_40():
    runner = CliRunner()
    input = "\\g:1-2--001,c:1326055296*3C\\!AIVDM,2,1,3,A,E7`B1:dW7oHth@@@@@@@@@@@@@@6@6R;mMQM@10888Qr8`8888888888,0*65"
    args = '--station=test'
    result = runner.invoke(update_tagblock, input=input, args=args)
    assert not result.exception
    assert result.output.strip() == input
