#include <Python.h>
#include <stdbool.h>
#include "core.h"

static PyMethodDef core_methods[] = {
    {"checksum", (PyCFunction)(void(*)(void))method_compute_checksum, METH_VARARGS,
     "Compute checksum of a string. returns an integer value"},
    {"checksum_str", (PyCFunction)(void(*)(void))method_compute_checksum_str, METH_VARARGS,
     "Compute checksum of a string. returns a 2-character hex string"},
    {"is_checksum_valid", (PyCFunction)(void(*)(void))method_is_checksum_valid, METH_VARARGS,
     "Returns True if the given string is terminated with a valid checksum, else False"},
    {"decode_tagblock", (PyCFunction)(void(*)(void))method_decode_tagblock, METH_FASTCALL,
     "decode a tagblock string.  Returns a dict"},
    {"encode_tagblock", (PyCFunction)(void(*)(void))method_encode_tagblock, METH_FASTCALL,
     "encode a tagblock string from a dict.  Returns a string"},
//    {"update_tagblock", (PyCFunction)(void(*)(void))tagblock_update, METH_FASTCALL,
//     "update a tagblock string from a dict.  Returns a string"},
    {"split_tagblock", (PyCFunction)(void(*)(void))method_split_tagblock, METH_FASTCALL,
     "Split off the tagblock portion of a longer nmea string.  Returns a tuple containing two strings"},
    {"join_tagblock", (PyCFunction)(void(*)(void))method_join_tagblock, METH_FASTCALL,
     "Join a tagblock to an AIVDM message.  Returns a string."},
    {NULL, NULL, 0, NULL}   /* sentinel */
};

static struct PyModuleDef core_module = {
    PyModuleDef_HEAD_INIT,
    "core",
    NULL,
    -1,
    core_methods
};

PyMODINIT_FUNC
PyInit_core(void)
{
    return PyModule_Create(&core_module);
}