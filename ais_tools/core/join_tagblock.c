#include <Python.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include "core.h"


int join_tagblock(char* buffer, size_t buf_size, const char* tagblock_str, const char* nmea_str)
{
    char* end = buffer + buf_size - 1;
    char* ptr = buffer;

    if (*tagblock_str && *nmea_str)
    {
        if (*tagblock_str != *TAGBLOCK_SEPARATOR)
            ptr = unsafe_strcpy(ptr, end, TAGBLOCK_SEPARATOR);
        ptr = unsafe_strcpy(ptr, end, tagblock_str);

        if (*nmea_str != *TAGBLOCK_SEPARATOR)
            ptr = unsafe_strcpy(ptr, end, TAGBLOCK_SEPARATOR);
        ptr = unsafe_strcpy(ptr, end, nmea_str);
    }
    else
    {
        ptr = unsafe_strcpy(ptr, end, tagblock_str);
        ptr = unsafe_strcpy(ptr, end, nmea_str);
    }

    if (ptr <= end)
    {
        *ptr = '\0';
        return ptr - buffer;
    }
    else
    {
        *end = '\0';
        return FAIL;
    }

    return SUCCESS;
}
