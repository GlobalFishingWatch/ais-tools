// Module methods

PyObject * method_compute_checksum    (PyObject *module, PyObject *const *args, Py_ssize_t nargs);
PyObject * method_compute_checksum_str(PyObject *module, PyObject *const *args, Py_ssize_t nargs);
PyObject * method_is_checksum_valid   (PyObject *module, PyObject *const *args, Py_ssize_t nargs);
PyObject * method_join_tagblock       (PyObject *module, PyObject *const *args, Py_ssize_t nargs);
PyObject * method_split_tagblock      (PyObject *module, PyObject *const *args, Py_ssize_t nargs);
PyObject * method_decode_tagblock     (PyObject *module, PyObject *const *args, Py_ssize_t nargs);
PyObject * method_encode_tagblock     (PyObject *module, PyObject *const *args, Py_ssize_t nargs);
PyObject * method_update_tagblock     (PyObject *module, PyObject *const *args, Py_ssize_t nargs);