#include <Python.h>
#include <stdbool.h>
#include <string.h>
#include "core.h"
#include "checksum.h"


PyObject *
method_compute_checksum(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{
    const char *str;

    if (nargs != 1)
        return PyErr_Format(PyExc_TypeError, "compute_checksum expects 1 argument");

    str = PyUnicode_AsUTF8(PyObject_Str(args[0]));
    return PyLong_FromLong(checksum(str));
}

PyObject *
method_compute_checksum_str(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{
    const char *str;
    char c_str[3];

    if (nargs != 1)
        return PyErr_Format(PyExc_TypeError, "checksum_str expects 1 argument");

    str = PyUnicode_AsUTF8(PyObject_Str(args[0]));
    checksum_str(c_str, str, ARRAY_LENGTH(c_str));
    return PyUnicode_FromString(c_str);
}

PyObject *
method_is_checksum_valid(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{
    const char *str;
    char buffer[MAX_SENTENCE_LENGTH];

    if (nargs != 1)
        return PyErr_Format(PyExc_TypeError, "checksum_str expects 1 argument");

    str = PyUnicode_AsUTF8(PyObject_Str(args[0]));

    if (safe_strcpy(buffer, str, ARRAY_LENGTH(buffer)) >= ARRAY_LENGTH(buffer))
        return PyErr_Format(PyExc_ValueError, "String too long");

    if (is_checksum_valid(buffer))
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}
