"""Worked examples: one runnable script per formula quoted in the article.

Every number in `sections/` is produced by a module in this package.  Each is
a standalone CLI the reader can run and re-run with different parameters, and
each exports the same small interface so that `verify_examples.py` can import
it and check the article's own figures against it.

See `_harness.py` for the interface a module must supply.
"""
