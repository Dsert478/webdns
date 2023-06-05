# WebDNS

The project aims to integrate a chain of automation processes to avoid manualy changes and erros during ip updates.

## Service configuration

Two services are required for correct operation. The first is a dns server that will respond to requests from a specific network. The second lets you create and update network entry configuration files. Both are implemented through containers with Dockerfile and docker-compose.yml.

### Configuration File

The webdns service has the configuration file 'webdns.conf'. In it we find the connection definitions with the netbox api, parameters, paths and ports:

```
[SETUP]
# Netbox URL
NB_URL = http://localhost

# Netbox token
#NB_TOKEN = token-hash

# HTTP Server PortNetbox token. Default is equal to 8181
#PORT = 8181

# Configuration files directory path
CF_PATH = /config/files/path

# Netbox prefix filter param vlan
#PARAMS_VLAN = vlan

```

## Create Network Configuration Files

The 'create_cf()' function create DNS masq config files from Netbox prefixes filtered according to the 'role', 'site', 'status' and 'vlan' parameters. These files will be updated if there is any change in the ip addressing and if they receive the correct request
```
def create_cf():
    nb = api(url=nburl, token=nbtoken)

        # Get nb prefixes based on config params
        prefixes = nb.ipam.prefixes.filter(
            role=nbpfparams['role'],
            site=nbpfparams['site'],
            status=nbpfparams['status'],
            vlan=nbpfparams['vlan'],
        )

        # Iterate over child prefixes (cp), creating config files
        for cp in prefixes:
            # Get tenant and open config file
            tenant = cp.tenant.slug
            cfile = open(f'{cfpath}{tenant}.conf', 'w')

            # Get ip address from ip prefix and get CIDR
            net = ipaddress.IPv4Network(cp)

            ips_cidr = [f'{str(host)}/{str(net.prefixlen)}' for host in net.hosts()]
            for ip in ips_cidr:
                # Check whether ip addr has DNS name
                ip_obj = nb.ipam.ip_addresses.get(address=str(ip))
                if ip_obj is not None:
                    dns_name = ip_obj.dns_name

                # Pop subnet mask from ip addr and write on file
                str_ip, _ = ip.split('/')
                cfile.write(f'address=/{dns_name}/{str_ip}\n')

            # Save file and close
            cfile.close()
        return
```

## Network File Update

In the api.py file we can find the Flask api initialization function and the network input files update function 'update_entries()', which is triggered to update the appropriate configuration file:
```
def update_entries():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        # Get data from request in Python format
        data = request.json
                
        # Validate data against JSON_UPDATE_SCHEMA
        data_is_valid = validate_json(data, JSON_UPDATE_SCHEMA)
        if not data_is_valid:
            return f'Invalid JSON data format. Please follow the following schema: {JSON_UPDATE_SCHEMA}\n'
        
        # Update config files based on input data
        update_cf(
            app.config['nburl'], 
            app.config['nbtoken'], 
            app.config['cfpath'], 
            data['tenant'], 
            data['ipaddresses']
        )
        return f'IP addresses updated on config file {data["tenant"]}.conf!\n'
        
    else:
        return 'Content-Type not supported!\n'
```

### Arguments

Through the 'configparser' and 'os' libraries, file name changes can be performed by HTTP requests in POST. We find exemplified in the function get_configs():

```
def get_configs():
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
```

### Making the Updates

The 'update_entries()' prepares the received JSON data and validates its format. After that, the 'update_cf()' function is called with the correct parameters to effectively update the network configuration file. 
The following is a example of an update request through an HTTP POST request with a valid JSON:

```bash
curl -H 'Content-Type: application/json' -X POST \
    -d '{"tenant": "ou-file-name",
         "ipaddresses":["access-ip",
                    "cpe-ip"]}' \
    localhost:8181/api/update_entries
```

The 'create_cf()' function can be found in methods.py file
```
def create_cf(cfpath, nburl, nbtoken, nbpfparams):
     # Check whether config file exists
    # TO-DO raise errors and deal with it
    filename = f'{cfpath}/{tenant}.conf'
    if not os.path.isfile(filename):
        print("Config file {} does not exist.".format(filename))
        exit(1)

    # Start nb connection
    nb = api(url=nburl, token=nbtoken)

    # Get nb ip addresses from Netbox
    ipaddrs = []
    for addr in ipaddresses:
        ipaddrs.append(
            nb.ipam.ip_addresses.get(
                address=addr,
            )
        )
                
    # Update IP addresses DNS masq entries based on dns_name from Netbox
    for ipaddr in ipaddrs:
        with open(filename, "r") as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            if (ipaddr.dns_name in line) and (ipaddr.address not in line):
                new_lines.append(f'address=/{ipaddr.dns_name}/{ipaddr.address.split("/")[0]}\n')
            # If there is no change
            elif (ipaddr.dns_name not in line) and (ipaddr.address not in line):   
                new_lines.append(line)

        # Open configuration file for write
        with open(filename, "w") as f:
            f.writelines(new_lines)

    return

```


