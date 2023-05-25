import copy
import socket

from trex.stl.trex_stl_client import *

traffic_control_kwargs = {
    'action': None,                         # (clear_stats | run | stop)
    'port_handle': None,
}

connect_kwargs = {
    'device': 'localhost',                  # ip or hostname of TRex
    'trex_rpc_port': None,                  # TRex extention: RPC port of TRex server (for several TRexes under same OS)
    'trex_pub_port': None,                  # TRex extention: Publisher port of TRex server (for several TRexes under same OS)
    'trex_timeout_sec': None,               # TRex extention: Timeout of rpc/pub connections
    'port_list': None,                      # list of ports
    'username': 'TRexUser',
    'reset': True,
    'break_locks': False,
}

class HLT_OK(dict):
    def __init__(self, init_dict = {}, **kwargs):
        dict.__init__(self, {'status': 1, 'log': None})
        dict.update(self, init_dict)
        dict.update(self, kwargs)

class TrexAPI(object):

    def __init__(self, verbose = "error"):
        self.trex_client = None
        self.verbose = verbose
        self._last_pg_id = 0                # pg_id acts as stream_handle
        self._streams_history = {}          # streams in format of HLT arguments for modify later
        self._native_handle_by_pg_id = {}   # pg_id -> native handle + port
        self._pg_id_by_id = {}              # stream_id -> pg_id
        self._pg_id_by_name = {}            # name -> pg_id

    def _merge_kwargs(default_kwargs, user_kwargs):
        kwargs = copy.deepcopy(default_kwargs)
        for key, value in user_kwargs.items():
            if key in kwargs:
                kwargs[key] = value
            elif key in ('save_to_yaml', 'save_to_pcap', 'pg_id'): # internal arguments
                kwargs[key] = value
            else:
                print("Warning: provided parameter '%s' is not supported" % key)
        return kwargs

    def connect(self, **user_kwargs):
        # Not finished implemented yet
        kwargs = self._merge_kwargs(connect_kwargs, user_kwargs)
        device = kwargs['device']
        try:
            device = socket.gethostbyname(device) # work with ip
        except: # give it another try
            try:
                device = socket.gethostbyname(device)
            except Exception as e:
                return print('Could not translate hostname "%s" to IP: %s' % (device, e))

        try:
            zmq_ports = {}
            if kwargs['trex_rpc_port']:
                zmq_ports['sync_port'] = kwargs['trex_rpc_port']
            if kwargs['trex_pub_port']:
                zmq_ports['async_port'] = kwargs['trex_pub_port']
            self.trex_client = STLClient(kwargs['username'], device, verbose_level = self.verbose, **zmq_ports)
            if kwargs['trex_timeout_sec'] is not None:
                self.trex_client.set_timeout(kwargs['trex_timeout_sec'])
        except Exception as e:
            return print('Could not init stateless client %s: %s' % (device, e))

        try:
            self.trex_client.connect()
        except Exception as e:
            self.trex_client = None
            return print('Could not connect to device %s: %s' % (device, e))

        # connection successfully created with server, try acquiring ports of TRex
        try:
            port_list = self._parse_port_list(kwargs['port_list'])
            self.trex_client.acquire(ports = port_list, force = kwargs['break_locks'])
            for port in port_list:
                self._native_handle_by_pg_id[port] = {}
        except Exception as e:
            self.trex_client = None
            return print('Could not acquire ports %s: %s' % (port_list, e))

        # arrived here, all desired ports were successfully acquired
        if kwargs['reset']:
            # remove all port traffic configuration from TRex
            try:
                self.trex_client.stop(ports = port_list)
                self.trex_client.reset(ports = port_list)
            except Exception as e:
                self.trex_client = None
                return print('Error in reset traffic: %s' % e)

        # self._streams_history = CStreamsPerPort(hlt_history = True)
        return print(port_handle = dict([(port_id, port_id) for port_id in port_list]))
        kwargs = merge_kwargs(cleanup_session_kwargs, user_kwargs)
        if not kwargs['maintain_lock']:
            # release taken ports
            port_list = kwargs['port_list'] or kwargs['port_handle'] or 'all'
            try:
                if port_list == 'all':
                    port_list = self.trex_client.get_acquired_ports()
                else:
                    port_list = self._parse_port_list(port_list)
            except Exception as e:
                return HLT_ERR('Unable to determine which ports to release: %s' % format_error(e))
            try:
                self.trex_client.stop(port_list)
            except Exception as e:
                return HLT_ERR('Unable to stop traffic %s: %s' % (port_list, format_error(e)))
            try:
                self.trex_client.remove_all_streams(port_list)
            except Exception as e:
                return HLT_ERR('Unable to remove all streams %s: %s' % (port_list, format_error(e)))
            try:
                self.trex_client.release(port_list)
            except Exception as e:
                return HLT_ERR('Unable to release ports %s: %s' % (port_list, format_error(e)))
        try:
            self.trex_client.disconnect(stop_traffic = False, release_ports = False)
        except Exception as e:
            return HLT_ERR('Error disconnecting: %s' % e)
        self.trex_client = None
        return HLT_OK()

    def interface_config(self, port_handle, mode='config'):
        # TODO
        if not self.trex_client:
            return print('Connect first')
        ALLOWED_MODES = ['config', 'modify', 'destroy']
        if mode not in ALLOWED_MODES:
            return print('Mode must be one of the following values: %s' % ALLOWED_MODES)
        # pass this function for now...
        return print('interface_config not implemented yet')


###########################
#    Traffic functions    #
###########################

    def traffic_control(self, **user_kwargs):
        if not self.trex_client:
            return print('Connect first')
        kwargs = self._merge_kwargs(traffic_control_kwargs, user_kwargs)
        action = kwargs['action']
        port_handle = kwargs['port_handle']
        ALLOWED_ACTIONS = ['clear_stats', 'run', 'stop', 'sync_run', 'poll', 'reset']
        if action not in ALLOWED_ACTIONS:
            return print('Action must be one of the following values: {actions}'.format(actions=ALLOWED_ACTIONS))

        if action == 'run':
            try:
                self.trex_client.start(ports = port_handle)
            except Exception as e:
                return print('Could not start traffic: %s' % e)

        elif action == 'stop':
            try:
                self.trex_client.stop(ports = port_handle)
            except Exception as e:
                return print('Could not stop traffic: %s' % e)

        elif action == 'clear_stats':
            try:
                self.trex_client.clear_stats(ports = port_handle)
            except Exception as e:
                return print('Could not clear stats: %s' % e)

        try:
            is_traffic_active = self.trex_client.is_traffic_active(ports = port_handle)
        except Exception as e:
            return 'Unable to determine ports status: %s' % e
        
        return HLT_OK(stopped = not is_traffic_active)

    def traffic_stats(self, **user_kwargs):
        # TODO
        pass

    # timeout = maximal time to wait
    def wait_on_traffic(self, port_handle = None, timeout = None):
        try:
            self.trex_client.wait_on_traffic(port_handle, timeout)
        except Exception as e:
            print('Unable to run wait_on_traffic: %s' % e)

