"""
Transport module for Opentmi python client
"""
import json
import requests
from requests import Response, RequestException
from opentmi_client.utils import get_logger, resolve_host, TransportException

REQUEST_TIMEOUT = 30
NOT_FOUND = 404


class Transport(object):
    """
    Transport class which handle communication layer
    Mostly wrappers http rest requests to more simple APIs
    """

    __request_timeout = 10

    def __init__(self, host='localhost', port=3000):
        """
        Constructor for Transport
        :param host:
        :param port:
        """
        self.logger = get_logger()
        self.__token = None
        self.__host = None
        self.set_host(host, port)
        self.logger.info("OpenTMI host: %s", self.host)

    def set_host(self, host, port):
        """
        Set host address and port
        :param host:
        :param port:
        :return:
        """
        self.__host = resolve_host(host, port)

    @property
    def host(self):
        """
        Getter for host
        :return: host as a string
        """
        return self.__host

    def set_token(self, token):
        """
        Set authentication token
        :param token:
        :return: Transport
        """
        self.__token = token
        return self

    @property
    def __headers(self):
        headers = {
            "content-type": "application/json",
            "Connection": "close"
        }
        if self.__token:
            headers["Authorization"] = "Bearer " + self.__token

    def get_json(self, url, params=None):
        """
        GET request
        :param url: url as a string
        :param params: url parameters as dict
        :raise TransportException: when something goes wrong
        :return: dict object or None if not found
        """
        try:
            self.logger.debug("GET: %s", url)
            response = requests.get(url,
                                    headers=self.__headers,
                                    timeout=REQUEST_TIMEOUT,
                                    params=params)
            if Transport.is_success(response):
                return response.json()
            elif response.status_code == NOT_FOUND:
                self.logger.warning("not found")
            else:
                self.logger.warning("Request failed: %s (code: %s)",
                                    response.text, str(response.status_code))
                raise TransportException(response.text, response.status_code)
        except RequestException as error:
            self.logger.warning("Connection error %s", error)
            raise TransportException(str(error))
        except (ValueError, TypeError) as error:
            raise TransportException(str(error))
        return None

    def post_json(self, url, payload, files=None):
        """
        POST request
        :param url:
        :param payload:
        :param files:
        :return: response as dict
        """
        try:
            response = requests.post(url,
                                     json=payload,
                                     headers=self.__headers,
                                     files=files if not None else [],
                                     timeout=REQUEST_TIMEOUT)
            if Transport.is_success(response):
                data = json.loads(response.text)
                return data
            else:
                self.logger.warning("status_code: %s", str(response.status_code))
                self.logger.warning(response.text)
                raise TransportException(response.text, response.status_code)
        except RequestException as error:
            self.logger.warning(error)
            raise TransportException(str(error))
        except (ValueError, TypeError, KeyError) as error:
            raise TransportException(error)

    def put_json(self, url, payload):
        """
        PUT requests
        :param url:
        :param payload: dict
        :return: response as a dict
        """
        try:
            response = requests.put(url,
                                    json=payload,
                                    headers=self.__headers,
                                    timeout=REQUEST_TIMEOUT)
            if Transport.is_success(response):
                data = json.loads(response.text)
                return data
            else:
                self.logger.warning("status_code: %s", str(response.status_code))
                self.logger.warning(response.text)
                raise TransportException(response.text, response.status_code)
        except RequestException as error:
            self.logger.warning(error)
            raise TransportException(str(error))
        except (ValueError, TypeError) as error:
            raise TransportException(error)
        except Exception as error:
            self.logger.warning(error)
            raise TransportException(str(error))

    @staticmethod
    def is_success(response):
        """
        Check if status_code is success range
        :param response:
        :return:
        """
        assert isinstance(response, Response)
        code = response.status_code
        return 300 > code >= 200