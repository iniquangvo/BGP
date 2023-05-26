import logging
import time

from pyats.log.utils import banner

from trex.stl.trex_stl_hltapi import *

class TrexAPIWrapper(object):

    def __init__(self, verbose = "error"):
        self._htl = CTRexHltApi(verbose=verbose)

    def connect(self, **user_kwargs):
        return self._htl.connect(**user_kwargs)

    def traffic_control(self, **user_kwargs):
        return self._htl.traffic_control(**user_kwargs)
    
    def interface_config(self, port_handle, mode='config'):
        # TODO
        pass
    
    def traffic_stats(self, **user_kwargs):
        return self._htl.traffic_stats(**user_kwargs)

    # timeout = maximal time to wait
    def wait_on_traffic(self, port_handle = None, timeout = None):
        return self._htl.wait_on_traffic(port_handle=port_handle, timeout=timeout)




## Logging ################################################################################
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
log.setLevel(logging.DEBUG)
###########################################################################################

devices = {}

class Variables():
    '''
    This Class is to have all the variables initialized and to be called all over the script.
    With this we can avoid using global variables
    '''
    dev_list = []
    host_list = []
    dut1_intf1_list = []
    dut1_intf2_list = []
    dut1_intf3_list = []
    dut1_intf4_list = []
    dut1_intf5_list = []
    dut1_intf6_list = []
    dut1_intf7_list = []
    dut2_intf1_list = []
    dut2_intf2_list = []
    dut2_intf3_list = []
    dut2_intf4_list = []
    dut2_intf5_list = []
    dut3_intf1_list = []
    dut3_intf2_list = []
    dut3_intf3_list = []
    dut3_intf4_list = []
    dut3_intf5_list = []
    dut3_intf6_list = []
    dut3_intf7_list = []
    dut4_intf1_list = []
    ixia_intf1 = []
    ixia_intf2 = []

def main():
    devices['trex'] = TrexAPIWrapper()

    # connect to TRex
    devices['trex'].connect(device="", port_list=[])


    log.info(banner("CLear stats on trex port connected to uut2"))
    devices['trex'].traffic_control(port_handle = Variables.ixia_intf1, action = 'clear_stats') 

    log.info(banner("Start traffic on trex port connected to uut2"))
    devices['trex'].traffic_control(action='run',port_handle=Variables.ixia_intf1)

    log.info("sleep for 20")
    time.sleep(20)

    log.info(banner("Stop traffic on trex port connected to uut2"))
    devices['trex'].traffic_control(action='stop',port_handle=Variables.ixia_intf1)

    log.info("sleep for 20")
    time.sleep(20)

    log.info(banner("Traffic stats on Trex ports connected to UUT1 and uut2"))
    ix1Stat = devices['trex'].traffic_stats(port_handle=Variables.ixia_intf1, mode='aggregate')
    log.debug(ix1Stat)
    time.sleep(5)
    ix2Stat = devices['trex'].traffic_stats(port_handle=Variables.ixia_intf2, mode='aggregate')
    log.debug(ix2Stat)

    log.info(banner("Checking counters connected on Trex ports connected to uut2"))
    ix1TxPckt = int(ix1Stat[Variables.ixia_intf1]['aggregate']['tx']['total_pkts'])
    log.debug(ix1TxPckt)
    ix2RxPckt = int(ix2Stat[Variables.ixia_intf2]['aggregate']['rx']['total_pkts'])
    log.debug(ix2RxPckt)

    log.info ("Traffic tx pkt count is "+ str(ix1TxPckt))
    log.info ("Traffic rx pkt count is "+ str(ix2RxPckt))

    # loss_count = (ix1TxPckt - ix2RxPckt) / (int(ratepps))

    # log.info ("Traffic loss in seconds"+ str(loss_count))

if __name__ == "__main__":
    main()