#include <Python.h>
#include <stdbool.h>
#include <string.h>
#include "core.h"
#include "tagblock.h"

PyObject *
method_compute_checksum(PyObject *module, PyObject *args)
{
    const char *str;
    int c;

    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;
    c = checksum(str);
    return PyLong_FromLong(c);
}

PyObject *
method_compute_checksum_str(PyObject *module, PyObject *args)
{
    const char *str;
    char c_str[3];

    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;
    checksum_str(c_str, str, ARRAY_LENGTH(c_str));
    return PyUnicode_FromString(c_str);
}

PyObject *
method_is_checksum_valid(PyObject *module, PyObject *args)
{
    char *str;
    char buffer[MAX_SENTENCE_LENGTH];

    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;

    if (safe_strcpy(buffer, str, ARRAY_LENGTH(buffer)) >= ARRAY_LENGTH(buffer))
    {
        PyErr_SetString(PyExc_ValueError, "String too long");
        return NULL;
    }

    return is_checksum_valid(buffer) ? Py_True: Py_False;
}

PyObject *
method_join_tagblock(PyObject *module,  PyObject *const *args, Py_ssize_t nargs)
{
    char buffer[MAX_SENTENCE_LENGTH];
    const char* tagblock_str;
    const char* nmea_str;

    if (nargs != 2)
        return PyErr_Format(PyExc_TypeError, "join expects 2 arguments");

    tagblock_str = PyUnicode_AsUTF8(PyObject_Str(args[0]));
    nmea_str = PyUnicode_AsUTF8(PyObject_Str(args[1]));

    if (FAIL == join_tagblock(buffer, ARRAY_LENGTH(buffer), tagblock_str, nmea_str))
        return PyErr_Format(PyExc_ValueError, ERR_NMEA_TOO_LONG);

    return PyUnicode_FromString(buffer);
}

PyObject *
method_split_tagblock(PyObject *module,  PyObject *const *args, Py_ssize_t nargs)
{
    const char* str;
    char buffer[MAX_SENTENCE_LENGTH];
    const char* tagblock_str;
    const char* nmea_str;

    if (nargs != 1)
        return PyErr_Format(PyExc_TypeError, "split expects only 1 argument");

    str = PyUnicode_AsUTF8(PyObject_Str(args[0]));
    if (safe_strcpy(buffer, str, ARRAY_LENGTH(buffer)) >= ARRAY_LENGTH(buffer))
        return PyErr_Format(PyExc_ValueError, ERR_NMEA_TOO_LONG);

    split_tagblock(buffer, &tagblock_str, &nmea_str);

    return PyTuple_Pack(2, PyUnicode_FromString(tagblock_str), PyUnicode_FromString(nmea_str));
}

PyObject *
method_decode_tagblock(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{
    const char *str;
    char tagblock_str[MAX_TAGBLOCK_STR_LEN];

    if (nargs != 1)
        return PyErr_Format(PyExc_TypeError, "decode expects only 1 argument");

    str = PyUnicode_AsUTF8(PyObject_Str(args[0]));

    if (safe_strcpy(tagblock_str, str, ARRAY_LENGTH(tagblock_str)) >= ARRAY_LENGTH(tagblock_str))
        return PyErr_Format(PyExc_ValueError, ERR_TAGBLOCK_TOO_LONG);

    PyObject* dict = decode_tagblock(tagblock_str);

    if (!dict)
        return PyErr_Format(PyExc_ValueError, ERR_TAGBLOCK_DECODE);

    return dict;
}


PyObject *
method_encode_tagblock(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
{

    PyObject *dict;
    int result;
    char tagblock_str[MAX_TAGBLOCK_STR_LEN];

    if (nargs != 1)
        return PyErr_Format(PyExc_TypeError, "encode expects only 1 argument");

    dict = args[0];

    result = encode_tagblock(tagblock_str, dict, ARRAY_LENGTH(tagblock_str));

    if (result < 0)
        switch(result)
        {
            case FAIL_TOO_MANY_FIELDS:
                return PyErr_Format(PyExc_ValueError, "encode failed: too many fields");
            case FAIL_STRING_TOO_LONG:
                return PyErr_Format(PyExc_ValueError, "encode failed: encoded string is too long");
        }

    return PyUnicode_FromString(tagblock_str);
}

PyObject *
method_update_tagblock(PyObject *module,  PyObject *const *args, Py_ssize_t nargs)
{
    const char* str;
    PyObject* dict;
    char message[MAX_SENTENCE_LENGTH];
    char updated_message[MAX_SENTENCE_LENGTH];

    if (nargs != 2)
        return PyErr_Format(PyExc_TypeError, "update expects 2 arguments");

    str = PyUnicode_AsUTF8(PyObject_Str(args[0]));
    dict = args[1];

    if (safe_strcpy(message, str, ARRAY_LENGTH(message)) >= ARRAY_LENGTH(message))
        return PyErr_Format(PyExc_ValueError, ERR_NMEA_TOO_LONG);

    int message_len = update_tagblock(updated_message, ARRAY_LENGTH(updated_message), message, dict);

    if (message_len < 0)
        switch(message_len)
        {
            case FAIL_STRING_TOO_LONG:
                return PyErr_Format(PyExc_ValueError, ERR_TAGBLOCK_TOO_LONG);
            case FAIL_TOO_MANY_FIELDS:
                return PyErr_Format(PyExc_ValueError, ERR_TOO_MANY_FIELDS);
            default:
                return PyErr_Format(PyExc_ValueError, ERR_UNKNOWN);
        }

    return PyUnicode_FromString(updated_message);
}
