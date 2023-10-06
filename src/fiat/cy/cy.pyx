import re
from libc.stdio cimport printf
from libc.string cimport strcpy, strlen
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free

cdef extern from "Python.h":
    char* PyUnicode_AsUTF8(object unicode)

cpdef char * return_char(char* st):
    print(st)
    return st.decode("utf-8")

cdef char ** create_string_array(size):
    cdef char **ret = <char **> PyMem_Malloc(size * sizeof(char *))
    return ret

cpdef tuple csv(int size, int skip, r, f):
    oid = [None]*size
    cdef int *linesize = <int *> PyMem_Malloc(
        size * sizeof(int))
    cdef int c = 0
    cdef char* l
    try:
        while True:
            line = f.readline().strip()
            if not line:
                break
            z = r.split(line)[1]
            oid[c] = z.decode("utf-8")
            linesize[c] = len(line)
            c += 1
        for x in linesize[:5]:
            print(x)
        return ([int(x) for x in linesize[:size]],oid)
    finally:
        PyMem_Free(linesize)
