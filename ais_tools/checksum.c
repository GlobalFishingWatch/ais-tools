// checksum module

#define PY_SSIZE_T_CLEAN  /* Make "s#" use Py_ssize_t rather than int. */
#include <Python.h>

int _checksum(const char *s)
{
  int c = 0;
  while (*s)
    c = c ^ *s++;
  return c;
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
checksum_compute_checksum_str(PyObject *module, PyObject *args)
{
    const char *str;
    int c;
    char c_str[3];

    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;
    c = _checksum(str);
    sprintf(c_str, "%02X", c);
    return PyUnicode_FromString(c_str);
}

//static PyObject *
//keywdarg_parrot(PyObject *module, PyObject *args, PyObject *keywds)
//{
//    int voltage;
//    const char *state = "a stiff";
//    const char *action = "voom";
//    const char *type = "Norwegian Blue";
//
//    static char *kwlist[] = {"voltage", "state", "action", "type", NULL};
//
//    if (!PyArg_ParseTupleAndKeywords(args, keywds, "i|sss", kwlist,
//                                     &voltage, &state, &action, &type))
//        return NULL;
//
//    int c = _checksum("test");
//    printf("-- checksum=%i\n", c);
//    printf("-- This parrot wouldn't %s if you put %i Volts through it.\n",
//           action, voltage);
//    printf("-- Lovely plumage, the %s -- It's %s!\n", type, state);
//
//    Py_RETURN_NONE;
//}

static PyMethodDef checksum_methods[] = {
//    {"parrot", (PyCFunction)(void(*)(void))keywdarg_parrot, METH_VARARGS | METH_KEYWORDS,
//     "Print a lovely skit to standard output."},
    {"checksum", (PyCFunction)(void(*)(void))checksum_compute_checksum, METH_VARARGS,
     "Compute checksum of a string. returns an integer value"},
    {"checksum_str", (PyCFunction)(void(*)(void))checksum_compute_checksum_str, METH_VARARGS,
     "Compute checksum of a string. returns a 2-character hex string"},
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