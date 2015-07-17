
from functools import reduce
import pprint
import inspect
import urllib.request
from lxml import html

__all__ = ['Scrap', 'Attribute']


class Scrap(object):
    """    Scrap class represents a bunch of data collected from information
        sources.
    """
    def __new__(cls, *args, **kwargs):
        obj = super(Scrap, cls).__new__(cls)
        pairs = [(k,v) for k,v in list(cls.__dict__.items()) if isinstance(v, Attribute)]
        obj.xpaths = {}
        obj.attrs = {}
        for k,v in pairs:
            v.index = k
            obj.xpaths[k] = v.xpath
            obj.attrs[k] = None
        return obj
    
    def __init__(self, **kwargs):
        prop_names = [member[0] for member in inspect.getmembers(self)
            if not member[0].startswith('__')]
        if '_error_is_none' not in prop_names:
            self._error_is_none = False
        for prop_name, prop_value in list(kwargs.items()):
            if prop_name not in prop_names:
                raise KeyError('Invalid attribute: ' + prop_name)
            try:
                setattr(self, prop_name, prop_value)
            except Exception as e:
                if not self._error_is_none:
                    raise e
                    
    def __repr__(self):
        d = {}
        for propname in self.attrs:
            d[propname] = getattr(self, propname)
        return pprint.pformat(d)
    
    __str__ = __repr__
    
    def lxml_parser(self, content):
        doc = html.document_fromstring(content)
        for k, xpath in list(self.xpaths.items()):
            elms = doc.xpath(xpath)
            setattr(self, k, [r.text_content().strip() for r in elms if r.text_content()])
    
    def fetch(self, url, *args, **kwargs):
        opener = urllib.request.build_opener()
        req = urllib.request.Request(url.format(*args, **kwargs))
        res = opener.open(req)
        self.lxml_parser(res.read())


class Attribute(object):
    """    Attribute class is a descriptor which represents each chunk of
        data extracted from a source of information.
    """
    def __init__(self, xpath, apply=[]):
        self.xpath = xpath
        self.index = None
        self.apply = apply
    
    def parse(self, value):
        return value
    
    def __set__(self, obj, value):
        """sets attribute's value"""
        try:
            iter(value)
        except:
            value = [value]
        if len(self.apply) == 0:
            apply = lambda x: x
        else:
            apply = compose(*self.apply)
        value = [apply(self.parse(v)) for v in value]
        obj.attrs[self.index] = value
    
    def __get__(self, obj, typo=None):
        """gets attribute's value"""
        try:
            return obj.attrs[self.index]
        except KeyError:
            return None
        
    def __delete__(self, obj):
        """resets to attribute's initial state"""
        obj.attrs[self.index] = None


def compose(*functions):
    f = list(functions)
    f.reverse()
    return reduce(lambda f, g: lambda x: f(g(x)), f)

