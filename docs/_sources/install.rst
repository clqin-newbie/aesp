
Installation
############

Requirements
============

- miniconda
- python3


Installation
============

.. note::

   To use AESP, first install miniconda_:

.. _miniconda: https://docs.anaconda.com/miniconda/install/

If miniconda is already installed, you can install the appropriate version of the python environment and activate it.

.. code:: console

   conda create -n aesp python==3.11
   conda activate aesp

To install AESP, here are two options.

[1] one can simply type

.. code:: console
   
   pip install aesp

[2] or make a copy of the source code, and then install it manually.

.. code:: console

   git clone https://github.com/stupid-cloud/aesp.git
   cd aesp
   pip install ./

If you already have aesp installed, try typing ``aesp -v`` to see the current version. You expect to see the following output.

.. code:: console
   
   aesp v2024.8.4

