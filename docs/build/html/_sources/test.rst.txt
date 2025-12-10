Testing
=======

Run pytest and output HTML report:

.. code-block:: bash

    pytest --html=all_testcases_report.html

Place the generated `all_testcases_report.html` into
`docs/source/_static/` (create `_static/assets/` and copy CSS there) and then open:

.. raw:: html

   <p><a href="_static/all_testcases_report.html" target="_blank">Open test report</a></p>

Or embed:

.. raw:: html

   <iframe src="_static/all_testcases_report.html" style="width:100%;height:800px;border:0"></iframe>