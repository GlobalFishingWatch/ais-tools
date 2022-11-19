// checksum module

#define PY_SSIZE_T_CLEAN  /* Make "s#" use Py_ssize_t rather than int. */
#include <Python.h>
#include <stdbool.h>
#include <string.h>

int _checksum(const char *s)
{
    int c = 0;
    while (*s)
      c = c ^ *s++;
    return c;
}

char* _checksum_str(const char * s, char* checksum)
{
    int c = _checksum(s);
    sprintf(checksum, "%02X", c);
    return checksum;
}

bool _is_checksum_valid(char* s)
{
  const char * skip_chars = "!?\\";
  const char * separator = "*";

  char* body = s;
  char* checksum = NULL;
  char computed_checksum[3];
  char* lasts = NULL;

  if (*body && strchr(skip_chars, body[0]))
    body++;

  body = strtok_r(body, separator, &lasts);
  checksum = strtok_r(NULL, separator, &lasts);
  if (checksum == NULL || strlen(checksum) != 2)
    return false;

  _checksum_str(body, computed_checksum);
  return strcasecmp(checksum, computed_checksum) == 0;
}

static PyObject *
checksum_compute_checksum(PyObject *module, PyObject *args)
{
    const char *str;
    int c;

    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;
    c = _checksum(str);
    return PyLong_FromLong(c);
}

static PyObject *
checksum_compute_checksumstr(PyObject *module, PyObject *args)
{
    const char *str;
    char c_str[3];

    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;
    _checksum_str(str, c_str);
    return PyUnicode_FromString(c_str);
}

static PyObject *
checksum_is_checksum_valid(PyObject *module, PyObject *args)
{
    char *str;

    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;

    return _is_checksum_valid(str) ? Py_True: Py_False;
}


static PyMethodDef checksum_methods[] = {
    {"checksum", (PyCFunction)(void(*)(void))checksum_compute_checksum, METH_VARARGS,
     "Compute checksum of a string. returns an integer value"},
    {"checksumstr", (PyCFunction)(void(*)(void))checksum_compute_checksumstr, METH_VARARGS,
     "Compute checksum of a string. returns a 2-character hex string"},
    {"is_checksum_valid", (PyCFunction)(void(*)(void))checksum_is_checksum_valid, METH_VARARGS,
     "Returns True if the given string is terminated with a valid checksum, else False"},
    {NULL, NULL, 0, NULL}   /* sentinel */
};

static struct PyModuleDef checksum_module = {
    PyModuleDef_HEAD_INIT,
    "checksum",
    NULL,
    -1,
    checksum_methods
};

PyMODINIT_FUNC
PyInit_checksum(void)
{
    return PyModule_Create(&checksum_module);
}