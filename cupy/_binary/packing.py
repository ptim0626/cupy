import cupy
from cupy import _core


_packbits_kernel = {
    'big': _core.ElementwiseKernel(
        'raw T myarray, raw int32 myarray_size', 'uint8 packed',
        '''for (int j = 0; j < 8; ++j) {
                    int k = i * 8 + j;
                    int bit = k < myarray_size && myarray[k] != 0;
                    packed |= bit << (7 - j);
                }''',
        'cupy_packbits_big'
    ),
    'little': _core.ElementwiseKernel(
        'raw T myarray, raw int32 myarray_size', 'uint8 packed',
        '''for (int j = 0; j < 8; ++j) {
                    int k = i * 8 + j;
                    int bit = k < myarray_size && myarray[k] != 0;
                    packed |= bit << j;
                }''',
        'cupy_packbits_little'
    )
}


def packbits(a, axis=None, bitorder='big'):
    """Packs the elements of a binary-valued array into bits in a uint8 array.

    This function currently does not support ``axis`` option.

    Args:
        myarray (cupy.ndarray): Input array.
        axis (int, optional): Not supported yet.
        bitorder (str, optional): bit order to use when packing the array,
            allowed values are `'little'` and `'big'`. Defaults to `'big'`.

    Returns:
        cupy.ndarray: The packed array.

    .. note::
        When the input array is empty, this function returns a copy of it,
        i.e., the type of the output array is not necessarily always uint8.
        This exactly follows the NumPy's behaviour (as of version 1.11),
        alghough this is inconsistent to the documentation.

    .. seealso:: :func:`numpy.packbits`
    """
    if myarray.dtype.kind not in 'biu':
        raise TypeError(
            'Expected an input array of integer or boolean data type')

    if bitorder not in ('big', 'little'):
        raise ValueError("bitorder must be either 'big' or 'little'")

    myarray = myarray.ravel()
    packed_size = (myarray.size + 7) // 8
    packed = cupy.zeros((packed_size,), dtype=cupy.uint8)
    return _packbits_kernel[bitorder](myarray, myarray.size, packed)


_unpackbits_kernel = {
    'big': _core.ElementwiseKernel(
        'raw uint8 myarray', 'T unpacked',
        'unpacked = (myarray[i / 8] >> (7 - i % 8)) & 1;',
        'cupy_unpackbits_big'
    ),
    'little': _core.ElementwiseKernel(
        'raw uint8 myarray', 'T unpacked',
        'unpacked = (myarray[i / 8] >> (i % 8)) & 1;',
        'cupy_unpackbits_little'
    )
}


def unpackbits(myarray, bitorder='big'):
    """Unpacks elements of a uint8 array into a binary-valued output array.

    This function currently does not support ``axis`` option.

    Args:
        myarray (cupy.ndarray): Input array.
        bitorder (str, optional): bit order to use when unpacking the array,
            allowed values are `'little'` and `'big'`. Defaults to `'big'`.

    Returns:
        cupy.ndarray: The unpacked array.

    .. seealso:: :func:`numpy.unpackbits`
    """
    if myarray.dtype != cupy.uint8:
        raise TypeError('Expected an input array of unsigned byte data type')

    if bitorder not in ['big', 'little']:
        raise ValueError("bitorder must be either 'big' or 'little'")

    unpacked = cupy.ndarray((myarray.size * 8), dtype=cupy.uint8)
    return _unpackbits_kernel[bitorder](myarray, unpacked)
