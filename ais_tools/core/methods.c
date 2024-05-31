#include <Python.h>
#include <stdbool.h>
#include <string.h>
#include "core.h"
#include "checksum.h"


PyObject *
method_compute_checksum(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{
    PyObject *py_str;
    PyObject *result;
    const char *str;

    if (nargs != 1)
        return PyErr_Format(PyExc_TypeError, "compute_checksum expects 1 argument");

    py_str = PyObject_Str(args[0]);

    str = PyUnicode_AsUTF8(py_str);

    result = PyLong_FromLong(checksum(str));

    Py_DECREF(py_str);

    return result;
}

PyObject *
method_compute_checksum_str(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{
    PyObject *py_str;
    PyObject *result;
    const char *str;
    char c_str[3];

    if (nargs != 1)
        return PyErr_Format(PyExc_TypeError, "checksum_str expects 1 argument");

    py_str = PyObject_Str(args[0]);

    str = PyUnicode_AsUTF8(py_str);

    checksum_str(c_str, str, ARRAY_LENGTH(c_str));

    result = PyUnicode_FromString(c_str);

    Py_DECREF(py_str);

    return result;
}

PyObject *
method_is_checksum_valid(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{
    PyObject *py_str;
    PyObject *result;
    const char *str;
    char buffer[MAX_SENTENCE_LENGTH];

    if (nargs != 1)
        return PyErr_Format(PyExc_TypeError, "checksum_str expects 1 argument");

    py_str = PyObject_Str(args[0]);

    str = PyUnicode_AsUTF8(py_str);

    if (safe_strcpy(buffer, str, ARRAY_LENGTH(buffer)) >= ARRAY_LENGTH(buffer))
        result = PyErr_Format(PyExc_ValueError, "String too long");
    else
        result = is_checksum_valid(buffer) ?  Py_NewRef(Py_True) :  Py_NewRef(Py_False);

    Py_DECREF(py_str);

    return result;
}
