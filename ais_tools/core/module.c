#include <Python.h>
#include <stdbool.h>
#include "core.h"
#include "methods.h"

static PyMethodDef core_methods[] = {
    {
        "checksum",
        (PyCFunction)(void(*)(void))method_compute_checksum,
        METH_FASTCALL,
        PyDoc_STR("Compute checksum of a string. Returns an integer value.  The checksum for an empty string is 0")
    },
    {
        "checksum_str",
        (PyCFunction)(void(*)(void))method_compute_checksum_str,
        METH_FASTCALL,
        PyDoc_STR("Compute checksum of a string. Returns a 2-character hex string")
    },
    {
        "is_checksum_valid",
        (PyCFunction)(void(*)(void))method_is_checksum_valid,
        METH_FASTCALL,
        PyDoc_STR("Returns True if the given string is terminated with a valid checksum, else False")
    },
    {NULL, NULL, 0, NULL}   /* sentinel */
};

static struct PyModuleDef core_module = {
    PyModuleDef_HEAD_INIT,
    "core",
    PyDoc_STR("AIS Tools core methods implemented in C.  Supports computing checksums"),
    -1,
    core_methods
};

PyMODINIT_FUNC
PyInit_core(void)
{
    return PyModule_Create(&core_module);
}