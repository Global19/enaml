#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from types import FunctionType

from .declarative import Declarative
from .enaml_def import EnamlDef


def _setup_binding_funcs(description, f_globals):
    """ A helper function which creates the functions for the bindings.

    This function is used to create the binding functions once, instead
    of several times for each instance on which the binding is used.
    This function will recursively operation on the entired description
    tree.

    Parameters
    ----------
    description : dict
        The description dictionary created by the Enaml compiler.

    f_globals : dict
        The dictionary of globals created by the Enaml compiler.

    """
    bindings = description['bindings']
    if len(bindings) > 0:
        for binding in bindings:
            code = binding['code']
            name = binding['name']
            # If the code is a tuple, it represents a delegation
            # expression which is a combination of subscription
            # and update functions.
            if isinstance(code, tuple):
                sub_code, upd_code = code
                func = FunctionType(sub_code, f_globals, name)
                func._update = FunctionType(upd_code, f_globals, name)
            else:
                func = FunctionType(code, f_globals, name)
            binding['func'] = func
    children = description['children']
    if len(children) > 0:
        for child in children:
            _setup_binding_funcs(child, f_globals)


def _make_enamldef_helper_(name, base, description, f_globals):
    """ A compiler helper function for creating a new EnamlDef type.

    This function is called by the bytecode generated by the Enaml
    compiler when an enaml module is imported. It is used to make new
    types from the 'enamldef' keyword.

    This helper will raise an exception if the base type is of an
    incompatible type.

    Parameters
    ----------
    name : str
        The name to use when generating the new type.

    base : type
        The base class to use for the new type. This must be a subclass
        of Declarative.

    description : dict
        The description dictionay by the Enaml compiler. This dict will
        be used during instantiation to populate new instances with
        children and bound expressions.

    f_globals : dict
        The dictionary of globals for objects created by this class.

    Returns
    -------
    result : EnamlDef
        A new enamldef subclass of the given base class.

    """
    if not isinstance(base, type) or not issubclass(base, Declarative):
        msg = "can't derive enamldef from '%s'"
        raise TypeError(msg % base)
    _setup_binding_funcs(description, f_globals)
    dct = {
        '__module__': f_globals.get('__name__', ''),
        '__doc__': description.get('__doc__', ''),
    }
    decl_cls = EnamlDef(name, (base,), dct)
    decl_cls.__declarative_descriptions__ += ((description, f_globals),)
    return decl_cls
