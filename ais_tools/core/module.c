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
    {
        "decode_tagblock",
        (PyCFunction)(void(*)(void))method_decode_tagblock,
        METH_FASTCALL,
        PyDoc_STR("Decode a tagblock string.  Returns a dict")
    },
    {
        "encode_tagblock",
        (PyCFunction)(void(*)(void))method_encode_tagblock,
        METH_FASTCALL,
        PyDoc_STR("Encode a tagblock string from a dict. Takes a dict and returns a string")
    },
    {
        "update_tagblock",
        (PyCFunction)(void(*)(void))method_update_tagblock,
        METH_FASTCALL,
        PyDoc_STR("Update a tagblock string from a dict.  Takes a string and a dict and returns a string")
    },
    {
        "split_tagblock",
        (PyCFunction)(void(*)(void))method_split_tagblock,
        METH_FASTCALL,
        PyDoc_STR("Split off the tagblock portion of a longer nmea string.  Returns a tuple containing two strings "
                  "(tagblock, nmea)")
    },
    {
        "join_tagblock",
        (PyCFunction)(void(*)(void))method_join_tagblock,
        METH_FASTCALL,
        PyDoc_STR("Join a tagblock to an AIVDM message.  Takes two strings and returns a string.")
    },
    {NULL, NULL, 0, NULL}   /* sentinel */
};

static struct PyModuleDef core_module = {
    PyModuleDef_HEAD_INIT,
    "core",
    PyDoc_STR("AIS Tools core methods implemented in C.  Supports tagblock manipulation and computing checksums"),
    -1,
    core_methods
};

PyMODINIT_FUNC
PyInit_core(void)
{
    return PyModule_Create(&core_module);
}