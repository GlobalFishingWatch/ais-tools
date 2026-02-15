// checksum module

#include <Python.h>
#include <stdbool.h>
#include <string.h>
#include "core.h"
#include "checksum.h"

/*
 * Compute the checksum value of a string.  This is
 * computed by xor-ing the integer value of each character in the string
 * sequentially.
 */
int checksum(const char *s)
{
    int c = 0;
    while (*s)
      c = c ^ *s++;
    return c;
}

/*
 * Get the checksum value of a string as a 2-character hex string
 * This is always uppercase.  The destination buffer must be at least 3 chars
 * (one for the terminating null character)
 *
 * Returns a pointer to the destination buffer
 * Returns null  if the dest buffer is too small
 */
char* checksum_str(char * __restrict dst, const char* __restrict src, size_t dsize)
{
    if (dsize < 3)
        return NULL;

    int c = checksum(src);
    snprintf(dst, dsize, "%02X", c);
    return dst;
}


/*
 * Compute the checksum value of the given string and compare it to the checksum
 * that appears at the end of the string.
 * the checksum should be a 2 character hex value at the end separated by  a '*'
 *
 * For example:
 *    c:1000,s:old*5A
 *
 * If the string starts with any of these characrters ?!\ then the first character is ignored
 * for purposes of computing the checksum
 *
 * If no checksum is found at at the end of the string then the return is false
 *
 * Returns true if the checksum at the end of the string matches the computed checksum, else false
 *
 * NOTE: The given string will be modified to separate it into the body portion and the checksum portion
 */
bool is_checksum_valid(char* s)
{
  const char * skip_chars = "!?\\";
  const char separator = '*';

  char* body = s;
  char* c_str = NULL;
  char computed_checksum[3];

  if (*body && strchr(skip_chars, body[0]))
    body++;

  char* ptr = body;
  while (*ptr != '\0' && *ptr != separator)
      ptr++;

  if (*ptr == '*')
      *ptr++ = '\0';
  c_str = ptr;

  if (c_str == NULL || strlen(c_str) != 2)
    return false;

  checksum_str(computed_checksum, body, ARRAY_LENGTH(computed_checksum));
  return strcasecmp(c_str, computed_checksum) == 0;
}