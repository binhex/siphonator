import requests
import backoff
import socket
import urllib3


@backoff.on_exception(backoff.expo, (socket.timeout, requests.exceptions.Timeout, requests.exceptions.HTTPError), max_tries=10)
def http_client(logger_instance, **kwargs):

    # user agent strings
    user_agent_chrome = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
    user_agent_iphone = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"

    # ignore cert insecure warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if kwargs is not None:

        if "url" in kwargs:

            url = kwargs['url']

        else:

            logger_instance.warning(u'No URL sent to function, exiting function...')
            return 1, None, None

        if "user_agent" in kwargs:

            user_agent = kwargs['user_agent']

            if user_agent == 'user_agent_chrome':
                user_agent = user_agent_chrome

            elif user_agent == 'user_agent_iphone':
                user_agent = user_agent_iphone

        else:

            user_agent = user_agent_chrome

        if "request_type" in kwargs:

            request_type = kwargs['request_type']

        else:

            logger_instance.warning(u'No request type (get/put/post) sent to function, exiting function...')
            return 1, None, None

        # optional stuff to include
        if "auth" in kwargs:

            auth = kwargs['auth']

        else:

            auth = None

        if "additional_header" in kwargs:

            additional_header = kwargs['additional_header']

        else:

            additional_header = None

        if "data_payload" in kwargs:

            data_payload = kwargs['data_payload']

        else:

            data_payload = None

    else:

        logger_instance.warning(u'No keyword args sent to function, exiting function...')
        return 1, None, None

    # set connection timeout value (max time to wait for connection)
    connect_timeout = 30.0

    # set read timeout value (max time to wait between each byte)
    read_timeout = 30.0

    # set status_code and content to None in case nothing returned
    status_code = None

    # use a context manager so the session (and its underlying connection pool) is
    # always closed on exit — even when backoff retries the decorated function
    with requests.Session() as session:

        try:

            # define dict of common arguments for requests
            requests_data_dict = {'url': url, 'timeout': (connect_timeout, read_timeout), 'allow_redirects': True, 'verify': False}

            # define default headers to compress and fake user agent
            session.headers.update({
                'Accept-encoding': 'gzip',
                'User-Agent': user_agent
            })

            if "additional_header" in kwargs:

                # append to headers dict with additional headers dict
                session.headers.update(additional_header)

            if "auth" in kwargs:

                session.auth = auth

            if request_type == "put":

                # add additional keyword arguments
                requests_data_dict.update({'data': data_payload})

            elif request_type == "post":

                # add additional keyword arguments
                requests_data_dict.update({'data': data_payload})

            # construct class.method from request_type
            request_method = getattr(session, request_type)

            # use keyword argument unpack to convert dict to keyword args
            response = request_method(**requests_data_dict)

            # get status code and content returned
            status_code = response.status_code
            content = response.content

            if status_code == 401:

                logger_instance.warning(f"The status code '{status_code}' indicates unauthorised access for '{url}', error is '{content}'")
                raise requests.exceptions.HTTPError(status_code, url, content)

            elif status_code == 404:

                logger_instance.warning(f"The status code '{status_code}' indicates the requested resource could not be found  for '{url}', error is '{content}'")
                raise requests.exceptions.HTTPError(status_code, url, content)

            elif status_code == 422:

                logger_instance.warning(f"The status code '{status_code}' indicates a request was well-formed but was unable to be followed due to semantic errors for '{url}', error is '{content}'")
                raise requests.exceptions.HTTPError(status_code, url, content)

            elif not 200 <= status_code <= 299:

                logger_instance.warning(f"The status code '{status_code}' indicates an unexpected error for '{url}', error is '{content}'")
                raise requests.exceptions.HTTPError(status_code, url, content)

        except requests.exceptions.ConnectTimeout as content:

            # connect timeout occurred
            logger_instance.warning(f"Connection timeout for URL '{url}' with error '{content}'")
            return 1, status_code, content

        except requests.exceptions.ConnectionError as content:

            # connection error occurred
            logger_instance.warning(f"Connection error for URL '{url}' with error '{content}'")
            return 1, status_code, content

        except requests.exceptions.TooManyRedirects as content:

            # too many redirects, bad site or circular redirect
            logger_instance.warning(f"Too many retries for URL '{url}' with error '{content}'")
            return 1, status_code, content

        except requests.exceptions.HTTPError as content:

            # catch http exceptions thrown by requests
            return 1, status_code, content

        except requests.exceptions.ReadTimeout as content:
            # too many redirects, bad site or circular redirect
            logger_instance.warning(f"Read timeout for URL '{url}' with error '{content}'")
            return 1, status_code, content

        except requests.exceptions.JSONDecodeError as content:

            # catch any other exceptions thrown by requests
            logger_instance.warning(f"Json decode error for URL '{url}' with error '{content}'")
            return 1, status_code, content

        except requests.exceptions.RequestException as content:

            # catch any other exceptions thrown by requests
            logger_instance.warning(f"Caught other exceptions for URL '{url}' with error '{content}'")
            return 1, status_code, content

        else:

            if 200 <= status_code <= 299:

                logger_instance.debug(f"The status code '{status_code}' indicates a successful request for '{url}'")
                return 0, status_code, content
