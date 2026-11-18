"""Shared HTTP session for all SIGPAC requests.

A single ``requests.Session`` is reused for every request made by the
library. This keeps the TCP connection alive (HTTP keep-alive) and, more
importantly for high-throughput callers, the DNS resolution of the SIGPAC
host is done once per process and then reused while the connection is
kept alive, instead of issuing a new DNS lookup for every single request.

The session (and its underlying urllib3 connection pool) is thread-safe,
so concurrent requests from multiple threads share the same session and
the same resolved endpoint.
"""

import requests

_session = requests.Session()

# Increase the connection pool size so that concurrent requests from
# multiple threads can each reuse a keep-alive connection instead of
# opening (and DNS-resolving) a new one.  The default pool_maxsize=10
# would force a new connection (and a new DNS lookup) for the 11th
# concurrent request.
_adapter = requests.adapters.HTTPAdapter(pool_maxsize=64)
_session.mount("http://", _adapter)
_session.mount("https://", _adapter)


def get(url, **kwargs):
    """Perform an HTTP GET using the shared session.

    Parameters
    ----------
    url : str
        The URL to request.
    **kwargs
        Any additional keyword argument accepted by
        ``requests.Session.get`` (e.g. ``verify=False``).

    Returns
    -------
    requests.Response
    """
    return _session.get(url, **kwargs)
