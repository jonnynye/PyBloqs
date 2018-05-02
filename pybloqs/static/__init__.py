import itertools

from pybloqs.html import js_elem, append_to, root, render
from pybloqs.util import encode_string

from pkg_resources import resource_filename

try:
    from cStringIO import StringIO
except ImportError:
    from six import StringIO


class Resource(object):
    def __init__(self, name, extension):
        """
        An external script dependency definition.

        :param name: Canonical name of the script.
        :param extension: Script file extension.
        """
        self._name = name
        self._extension = extension
        self._hash = hash(name)

    @property
    def _local_path(self):
        """
        Generate the local path to the script using pkg_resources and taking the minification
        switch into account.
        """
        return resource_filename(__name__, self._name + self._extension)

    def write(self, parent):
        pass

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if not isinstance(other, Resource):
            return False
        return self._hash == other._hash


class JScript(Resource):
    """
    Definition for external JS script dependencies.
    """
    # global flag to turn off script encoding/compression across the board
    global_encode = True

    def __init__(self, name=None, encode=True, script_string=None):
        """
        An javascript dependency definition.

        :param name: Canonical name of the script
        :param encode: Whether to compress and base64 encode the script.
        """
        if name is None and script_string is None:
            raise ValueError('Please specify either resource name or script_string')
        super(JScript, self).__init__(name, ".js")
        self._encode = encode
        self._script_string = script_string

    def write(self, parent=None):
        stream = StringIO()

        if self._script_string is None:
            # Write out init condition
            _sentinel_var_name = "_pybloqs_load_sentinel_{}".format(self._name.replace("-", "_"))
            stream.write("if(typeof({}) == 'undefined'){{".format(_sentinel_var_name))

            with open(self._local_path, "rb") as f:
                if self._encode:
                    self.write_compressed(stream, f.read())
                else:
                    stream.write(f.read())

            stream.write("{} = true;".format(_sentinel_var_name))

            stream.write("}")

            self._script_string = stream.getvalue()
        elif self._encode:
            self.write_compressed(stream, self._script_string)
            self._script_string = stream.getvalue()

        return js_elem(parent, self._script_string)

    @classmethod
    def write_compressed(cls, stream, data):
        if cls.global_encode:
            stream.write('blocksEval(RawDeflate.inflate(atob("')
            stream.write(encode_string(data))
            stream.write('")));')
        else:
            stream.write(data)


class Css(Resource):
    def __init__(self, name=None, tag_id=None,  css_string=None):
        super(Css, self).__init__(name, ".css")
        if name is None and css_string is None:
            raise ValueError('Please specify either resource name or script_string')
        self._css_string = css_string
        self._tag_id = tag_id

    def write(self, parent=None):
        if parent is None:
            el = root("style")
        else:
            el = append_to(parent, "style")

        el["type"] = "text/css"

        if self._tag_id is not None:
            el["id"] = self._tag_id

        if self._css_string is None:
            with open(self._local_path, "rb") as f:
                self._css_string = f.read()
        el.string = self._css_string

        return el


class DependencyTracker(object):
    def __init__(self, *args):
        self._deps = list(args)
        self._deps_set = set(args)

    def add(self, *resources):
        for resource in resources:
            if resource not in self._deps_set:
                self._deps.append(resource)
                self._deps_set.add(resource)

    def any(self, type_filter=None):
        if type_filter is None:
            return len(self._deps) > 0

        return any(itertools.imap(lambda res: isinstance(res, type_filter), self._deps))

    def __iter__(self):
        return iter(self._deps)


# JS deflation script and the reporting core functionality is always registered
script_block_core = JScript("block-core", encode=False)
script_inflate = JScript("jsinflate", encode=False)

_registered_resources = DependencyTracker(script_block_core, script_inflate)


def register_interactive(*scripts):
    _registered_resources.add(*scripts)


def write_interactive(stream):
    for script in _registered_resources:
        stream.write(render(script.write(), pretty=False))
