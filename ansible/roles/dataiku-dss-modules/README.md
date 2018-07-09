Dataiku DSS modules
===================

This role packages custome modules to administrate Dataiku Data Science Studio platforms.

Requirements
------------

These modules require the Dataiku DSS API to be installed and available in the Python runtime executing the module. The `ansible_python_interpreter` option might be useful when using a virtualenv.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - dataiku-dss-modules # Makes the modules available

License
-------

MIT

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
