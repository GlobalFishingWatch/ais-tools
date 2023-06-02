#include <Python.h>
#include <stdbool.h>
#include <string.h>
#include "core.h"
#include "tagblock.h"

int decode_timestamp_field(struct TAGBLOCK_FIELD* field, PyObject* dict)
{
    const char* key = lookup_long_key(field->key);
    char * end;

    long value = strtol(field->value, &end, 10);
    if (errno || *end)
        return FAIL;

    if (value > 40000000000)
        value = value / 1000;
    PyDict_SetItemString(dict, key, PyLong_FromLong(value));
    return SUCCESS;
}

int decode_int_field(struct TAGBLOCK_FIELD* field, PyObject* dict)
{
    const char* key = lookup_long_key(field->key);
    char* end;

    long value = strtol(field->value, &end, 10);
    if (errno || *end)
        return FAIL;

    PyDict_SetItemString(dict, key, PyLong_FromLong(value));

    return SUCCESS;
}

int decode_text_field(struct TAGBLOCK_FIELD* field, PyObject* dict)
{
    const char* key = lookup_long_key(field->key);
    PyDict_SetItemString(dict, key, PyUnicode_FromString(field->value));

    return SUCCESS;
}

int decode_group_field(struct TAGBLOCK_FIELD* field, PyObject* dict)
{
    size_t idx = 0;
    char * save_ptr = NULL;
    long values[ARRAY_LENGTH(group_field_keys)];
    char buffer[MAX_VALUE_LEN];

    if (safe_strcpy(buffer, field->value, ARRAY_LENGTH(buffer)) >= ARRAY_LENGTH(buffer))
        return FAIL;

    char * f = strtok_r(buffer, GROUP_SEPARATOR, &save_ptr);
    while (f && idx < ARRAY_LENGTH(values))
    {
        char* end;
        values[idx++] = strtol(f, &end, 10);
        if (errno || *end)
            return FAIL;

        f = strtok_r(NULL, GROUP_SEPARATOR, &save_ptr);
    }
    if (idx == ARRAY_LENGTH(values))
    {
        for (idx = 0; idx < ARRAY_LENGTH(values); idx++)
            PyDict_SetItemString(dict, group_field_keys[idx], PyLong_FromLong(values[idx]));
        return SUCCESS;
    }

    return FAIL;
}

int decode_custom_field(struct TAGBLOCK_FIELD* field, PyObject* dict)
{
    char custom_key[MAX_KEY_LEN];
    snprintf(custom_key, ARRAY_LENGTH(custom_key), "%s%s", CUSTOM_FIELD_PREFIX, field->key);
    PyDict_SetItemString(dict, custom_key, PyUnicode_FromString(field->value));

    return SUCCESS;
}

PyObject * decode_tagblock(char * tagblock_str)
{
    struct TAGBLOCK_FIELD fields[MAX_TAGBLOCK_FIELDS];
    int num_fields = 0;
    int status = SUCCESS;

    PyObject* dict = PyDict_New();

    num_fields = split_fields(fields, tagblock_str, ARRAY_LENGTH(fields));
    if (num_fields < 0)
        status = FAIL;

    for (int i = 0; i < num_fields && status==SUCCESS; i++)
    {
        struct TAGBLOCK_FIELD* field = &fields[i];
        const char* key = field->key;

        switch(key[0])
        {
            case 'c':
                status = decode_timestamp_field(field, dict);
                break;
            case 'd':
            case 's':
            case 't':
                status = decode_text_field(field, dict);
                break;
            case 'g':
                status = decode_group_field(field, dict);
                break;
            case 'n':
            case 'r':
                status = decode_int_field(field, dict);
                break;
            default:
                status = decode_custom_field(field, dict);
        }
    }
    if (status == SUCCESS)
        return dict;
    else
        return NULL;
}
