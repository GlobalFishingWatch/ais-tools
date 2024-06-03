#include <sys/types.h>

/*
 * Copy a source str to a dest str
 *
 * Does not write a null terminator
 * dest_end should point to the last position in the dest string buffer.  This method will
 * stop at the character immediately before this position
 *
 * returns a pointer the the position immediately after the last position written in dest
 * you can use the return pointer for a subsequent copy, or if you are finished, write a
 * null char to that position to terminate the string
 */
char * unsafe_strcpy(char * __restrict dest, const char * __restrict dest_end, const char * __restrict src)
{
    while (dest < dest_end && *src)
        *dest++ = *src++;
    return dest;
}


/*
 * Copy string src to buffer dst of size dsize.  At most dsize-1
 * chars will be copied.  Always NUL terminates (unless dsize == 0).
 * Returns strlen(src); if retval >= dsize, truncation occurred.
 */
size_t safe_strcpy(char * __restrict dst, const char * __restrict src, size_t dsize)
{
	const char *osrc = src;
	size_t nleft = dsize;

	/* Copy as many bytes as will fit. */
	if (nleft != 0) {
		while (--nleft != 0) {
			if ((*dst++ = *src++) == '\0')
				break;
		}
	}

	/* Not enough room in dst, add NUL and traverse rest of src. */
	if (nleft == 0) {
		if (dsize != 0)
			*dst = '\0';		/* NUL-terminate dst */
		while (*src++)
			;
	}

	return(src - osrc - 1);	/* count does not include NUL */
}