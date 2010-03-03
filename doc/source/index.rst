.. pyDNS documentation master file, created by
   sphinx-quickstart on Tue Feb  2 10:00:47 2010.
.. currentmodule:: DNS

Welcome to pyDNS's documentation!
=================================

The :mod:`DNS` module provides DNS lookup functionality. It can operate in a synchronous or asynchronous manner (async not working). The development of pyDNS happens `here <http://pydns.sf.net>`_. The main work horse of this module is the class :class:`DnsRequest`.

:License: This module is covered by the standard Python License.

This page contains the main API overview. More information on specific topics can be found on the following pages:

.. toctree::
   :maxdepth: 1

   constants

:mod:`DNS` -- DNS lookups
=============================================

.. method:: DiscoverNameServers

   Retrieve the system name servers and sets them as default values for the :class:`DnsRequest` *server* parameter. This value will be taken as default value for all future :class:`DnsRequest` instances and as default in :meth:`DnsRequest.req` if the *server* parameter is not explicitely given. Calling this once per module lifetime suffices if your DNS servers have not changed in the meanwhile.

   :returns: None


.. method:: dumpQ(u)

   *FIXME*

.. method:: dumpRR(u)

   *FIXME*

Convenience methods
^^^^^^^^^^^^^^^^^^^

.. method:: revlookup(name):

    Convenience routine for doing a reverse lookup of an address. This will only return one of any records returned.

    :returns: DnsRequest(b, qtype = 'ptr').req().answers[0]['data']

.. method:: revlookup6(name):

   Takes an IPv6 textual address (rfc 2373 2.2 presentation format 
   (subpart 3, ::i.p.v.4 is explicitly NOT supported). 

   return q.answers[0]['data']

   :returns: a name (only one if more than one presented).


.. method:: mxlookup(name):

    Convenience routine for doing an MX lookup of a name. 

    :returns: List mail exchanger records sorted by preference.


:class:`DnsRequest` -- A DNS request
------------------------------------

.. class:: DnsRequest(name=''[,server=''][,protocol='udp'][,port=53][,opcode=Opcode.QUERY][,qtype=Type.A][,rd=1][,timing=1][,timout=30])

   DnsRequest represents a specific request with a high-level user interface. Call :meth:`DiscoverNameServers` in order to fill in the default values with the system DNS servers.

   :param server: DNS server as string or list of strings. You might want to use an IP address here.
   :type server: string or list of strings
   :param protocol: 'udp' or 'tcp'
   :param port: Port number to query
   :type port: int
   :param opcode: query opcode, e.g. QUERY, IQUERY, STATUS, NOTIFY, UPDATE
   :type opcode: :class:`DNS.Opcode`
   :param qtype: The query type, e.g. SOA, A, MX, CNAME, ANY
   :type qtype: :class:`DNS.Type`
   :param rd: recursion desired (defaults to 1)
   :type rd: int
   :param timing: *FIXME*
   :type timing: int
   :param timeout: Timeout of DNS request
   :type timeout: int
   :rtype: the initialized DNSRequest instance

   .. method:: req([name=''][,server=[]][,protocol='udp'][,port=53][,opcode=Opcode.QUERY][,qtype=Type.A][,rd=1][,timing=1][,timout=30])

      Perform a DNS request.

      This method should usually be used to perform DNS requests. Parameters given here, will replace those that have been used to initialize the :class:`DnsRequest`. All function parameters are identical to the :meth:`DnsRequest`. Specifying an invalid *qtype* argument will raise :exc:`DNSError` 'unknown query type'.

      :returns:  A :class:`DnsResult` instance (also bound to the :attr:`DnsRequest.response` attribute) or *None* (for async calls)
      :exception: :exc:`DNSError` in case of errors.

      .. note:: This function would usually be called by the user to perform a DNS query.
   

   .. method:: sendTCPRequest(server)

      Actually perform a TCP Request with the paramters that have previously been set up with the :class:`DNSRequest` initialization or the parameters passed to :meth:`req`.  This function would usually not be called directly by the user but is invoked from :meth:`req`.

      :param server: DNS server hostname(s) as string or list of strings
      :type server: string or list of strings

   .. method:: sendUDPRequest(server)

      Actually perform a UDP Request with the paramters that have previously been set up with the :class:`DNSRequest` initialization or the parameters passed to :meth:`req`. This function would usually not be called directly by the user but is invoked from :meth:`req`.

      :param server: DNS server hostname(s) as string or list of strings
      :type server: string or list of strings


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

