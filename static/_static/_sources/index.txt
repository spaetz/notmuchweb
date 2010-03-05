.. notmuch documentation master file, created by
   sphinx-quickstart on Tue Feb  2 10:00:47 2010.
.. currentmodule:: notmuch

Welcome to notmuch's documentation!
=================================

The :mod:`notmuch` module provides an interface to the `notmuch <http://notmuchmail.org>`_ functionality. The main work horse of this module is the class :class:`Notmuch` with important other classes representing a :class:`Thread` and a single :class:`Message`.

.. moduleauthor:: Sebastian Spaeth <Sebastian@SSpaeth.de>
:License: This module is covered under the GNU GPL v2 (or later).

This page contains the main API overview. More information on specific topics can be found on the following pages:

.. toctree::
   :maxdepth: 1

   thread

:mod:`notmuch` -- The Notmuch interface
=============================================

:class:`Notmuch` -- A notmuch call
------------------------------------

.. class:: Notmuch([logger=None])

   Notmuch represents a specific request. Calling its method will cause the actual notmuch calls.

   :param logger: A logging.Logger to be used for logging
   :type logger: logging.Logger
   :rtype: the initialized Notmuch instance


Methods
^^^^^^^^^^^^^^^^^^^

   .. automethod:: new()

      Perform a DNS request.

      This method should usually be used to perform DNS requests. Parameters given here, will replace those that have been used to initialize the :class:`DnsRequest`. All function parameters are identical to the :meth:`DnsRequest`. Specifying an invalid *qtype* argument will raise :exc:`DNSError` 'unknown query type'.

      :returns:  A :class:`DnsResult` instance (also bound to the :attr:`DnsRequest.response` attribute) or *None* (for async calls)
      :exception: :exc:`DNSError` in case of errors.

      .. note:: This function would usually be called by the user to perform a DNS query.
   
   .. automethod:: syncTags(self[,thorough=False[, frommaildir=False[,dryrun=False[, all_mails=None]]]]):

      :param thorough: DNS server hostname(s) as string or list of strings
      :type thorough: string or list of strings
      :TODO: should implement a fallback, as that is not going to to be incorporated anytime soon)


:class:`DnsResult` -- A DNS request result
------------------------------------------

.. autoclass:: DnsResult

    An instance of this class is created by the :class:`DnsRequest` and contains the results of a request.

    :param u: FIXME (elaborate here). *u* are passed to  :meth:`storeM`.
    :type u: FIXME check :meth:`storeM`
    :param args: args. *FIXME* check what this does. Are assigned to :attr:`DnsResult.args`.
    :type args: FIXME check

    .. method:: show

       *Print()*\ s out the DNS reply.

       :returns: None

    .. automethod:: storeM

    .. automethod:: storeQ

    .. method:: storeRR(u)

        :param u: FIXME
        :type u: FIXME: a RRunpacker

        Returns a dict with the following keys:

        * name
        * type
        * class
        * ttl
	* rdlength
        * typename: Type.typestr() of *type*
        * classstr: Class.classstr() of *class*

        mname = 'get%sdata' % r['typename']
        if hasattr(u, mname):r['data']=getattr(u, mname)()
        else:r['data']=u.getbytes(r['rdlength'])

	:returns: a dict containing the above keys.

    .. automethod:: storeM

    .. attribute:: answers

       *FIXME* All answers as a list of whatever :meth:`storeRR` returns.

:exc:`DNSError` -- A DNS request error
------------------------------------------
.. autoexception:: DNSError
   :members:

   This execption inherits directly from :exc:`Exception` and is raised on errors during the lookup.

Out of date and broken
----------------------

.. autoclass:: DnsAsyncRequest
.. ..(DnsRequest,asyncore.dispatcher_with_send):

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

