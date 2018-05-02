from pybloqs.static import Resource, JScript, Css, DependencyTracker, register_interactive, write_interactive
import pytest
from six import StringIO


def test_resource_local_path():
    name = 'dummy'
    ext = 'ext'
    resource = Resource(name, ext)
    path = resource._local_path
    assert path.endswith(name + ext)


def test_jscript_raises_with_no_name_and_string():
    with pytest.raises(ValueError):
        JScript()


def test_jscript_write_string():
    script = 'test script'
    jscript = JScript(script_string=script, encode=False)
    output = jscript.write()
    output_string = output.__str__()
    assert output_string.startswith('<script>')
    assert output_string.endswith('</script>')
    assert script in output_string

    # Check that output is compressed if we ask for it
    jscript = JScript(script_string=script, encode=True)
    output = jscript.write()
    output_string = output.__str__()
    assert output_string.startswith('<script>')
    assert output_string.endswith('</script>')
    assert 'RawDeflate' in output_string
    assert script not in output_string


def test_jscript_write_string_compressed():
    script = 'test script'
    jscript = JScript(script_string=script)
    stream = StringIO()
    jscript.write_compressed(stream, script)
    output = stream.getvalue()
    assert output.startswith('blocksEval')
    assert script not in output

    # Do not compress if disabled globally
    JScript.global_encode = False
    jscript = JScript(script_string=script, encode=False)
    stream = StringIO()
    jscript.write_compressed(stream, script)
    output = stream.getvalue()
    assert output == script


def test_jscript():
    pass
