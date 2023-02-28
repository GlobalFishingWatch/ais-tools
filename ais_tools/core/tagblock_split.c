#include <Python.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include "core.h"

/*
 * Split a sentence into the tagblock part and the nmea part
 *
 * This method modifies the given message to write a null character to terminate
 * the tagblock part
 *
 * returns the length of the tagblock part
 *
 * Four cases for the given message string
 *
 * starts with '!' - no tagblock, entire message in nmea
 * starts with '\!' - no tagblock, strip off '\',entire message in nmea
 * starts with '\[^!]' - is a tagblock , strip off leading '\', nmea is whatever comes after the  next '\'.
 * starts with '[^\!]' - is a tagblock, nmea is whatever comes after the  next '\'.
 * starts with '[^!]' and there are no `\` delimiters - tagblock is empty, entire message in nmea
 */
int split_tagblock(char* message, const char** tagblock, const char** nmea)
{

    char* ptr;
    int tagblock_len = 0;

    ptr = message;
    if (*ptr == *TAGBLOCK_SEPARATOR)
        ptr ++;
    if (*ptr == *AIVDM_START)
    {
        *nmea = ptr;
        *tagblock = EMPTY_STRING;
    }
    else
    {
        *tagblock = ptr;
        for (ptr = &message[1]; *ptr != '\0' && *ptr != *TAGBLOCK_SEPARATOR; ptr++);
        tagblock_len = ptr - *tagblock;
        if (*ptr)
        {
            *ptr = '\0';
            *nmea = ptr + 1;
        }
        else
            *nmea = EMPTY_STRING;
    }

    return tagblock_len;
}