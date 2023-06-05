import configparser
import ipaddress
import os

from pynetbox import api

from .api.api import run_api
from .methods import create_cf

class WebDns:
    '''
    The WebDns starts Dnsmasq server and generates all config files obtained from 
    Netbox ipam (prefix and ip) objects

    Parameters
    ----------
    cpath : str
        Configuration file path of webdns

    Attributes
    ----------
    cpath : str
        Configuration file path of webdns,
    nburl : str
        Netbox URL,
    nbtoken : str
        Netbox API Token,
    port : int
        HTTP server port,
    cfpath : str
        Dir path of DNS Masq config files,
    nbpfparams : dict
        Netbox prefix filter params,
    '''
    def __init__(self, cpath) -> None:
        self.cpath = cpath
        self.nburl = None
        self.nbtoken = None
        self.cfpath = None 
        self.port = 8181
        self.nbpfparams = {}
        self.get_configs()
        self.create_cf()
        self.run_api()

    def get_configs(self):
        '''Get config parameters of webdns

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        None
        '''
        config = configparser.ConfigParser()
        config.read_file(open(self.cpath, 'r'))
        self.nburl = config.get('SETUP', 'NB_URL')
        self.nbtoken = config.get('SETUP', 'NB_TOKEN')
        self.cfpath = config.get('SETUP', 'CF_PATH')
        self.port = config.get('SETUP', 'PORT')
        try: 
            self.nbpfparams['role'] = config.get('SETUP', 'PARAMS_ROLE')
        except configparser.NoOptionError:
            self.nbpfparams['role'] = None
        try:
            self.nbpfparams['status'] = config.get('SETUP', 'PARAMS_STATUS')
        except configparser.NoOptionError:
            self.nbpfparams['status'] = None
        try:
            self.nbpfparams['site'] = config.get('SETUP', 'PARAMS_SITE')
        except configparser.NoOptionError:
            self.nbpfparams['site'] = None
        try:
            self.nbpfparams['vlan'] = config.get('SETUP', 'PARAMS_VLAN')
        except configparser.NoOptionError:
            self.nbpfparams['vlan'] = None
        return

    def create_cf(self):
        '''Create DNS masq config files from Netbox prefixes

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        None
        '''
        create_cf(self.cfpath, self.nburl, self.nbtoken, self.nbpfparams)
    
    
    def run_api(self):
        '''Run REST API 

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        None
        '''
        run_api(
            self.nburl, 
            self.nbtoken, 
            self.cfpath, 
            self.port
        )
        
        return