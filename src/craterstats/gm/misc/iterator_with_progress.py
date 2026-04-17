#  Copyright (c) 2026, Greg Michael
#  Licensed under BSD 3-Clause License. See LICENSE.txt for details.


def iterator_with_progress(enumerated_iterable, total=None, progress_queue=None):
    """
    Iterate over items with progress reporting.

    Parameters:
    - enumerated_iterable: enumerated items to iterate (i needed in calling loop)
    - total: total number of items (required for progressbar)
    - callback: optional function(current, total) to handle GUI updates

    Returns:
    - iterator over (index, item) tuples
    """

    if progress_queue is not None:
        def generator():
            for i, item in enumerated_iterable:
                progress_queue.put((i + 1, total, None))
                yield i, item
        return generator()
    else:
        from progressbar import progressbar
        return progressbar(enumerated_iterable, max_value=total)