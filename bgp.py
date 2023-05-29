#!/bin/env python
#################################################################################
##Script Header
# Copyright (c) 2022-2023 by Cisco Systems, Inc.
# Script file
# All rights reserved.
#__date__ = 'Dec 2022'
#__version__ = '1.0'
#################################################################################
'''
***********************************************************
         BGP Testcases automation
***********************************************************
'''
"""
Name:
=====
#
YAML:
      bgp.yaml
AUTHOR:
      Yugandhar Kotla (ykotla@cisco.com)  
      
DESCRIPTION:
       Verify all configs are getting saved.
Supported Platforms:
      catalyst 9k
Device Under Test:
      Catalyst 9k
Notes, Bugs, Enhancements:
Feature Name : BGP
EDCS number: EDCS-23757061
Testcase Information:
The script contains the following testcases:
Common Setup:

TC_01: To verify sync between BGP and IGP.  No sync enables the router to advertise a network route without waiting for the IGP
TC_02: To verify EBGP neighbor can be formed by configuring neighbor command
TC_03: To verify devices which are not directly connected can be made as BGP  neighbor by configuring multihop command 
TC_04: To verify load balancing between two eBGP over parallel lines
TC_05: To verify the removed network dropped from the BGP routing table
TC_06: To verify that the new EBGP routes can be added to  the BGP table
TC_07: To verify BGP updates from being send out using route-maps
TC_08: To verify BGP updates from inbound BGP filtering using route-maps
TC_10: To verify the L3 forwarding behavior to the routes learnt from the adjacent router
TC_17: To verify EBGP load balancing with maximum-paths 

How to Run: pyats run job <job file name> -testbed_file <testbed file name>
"""
#############################################################################################
#  TEST SCRIPT INITIALIZATION BLOCK
#############################################################################################
# Import the libraries
from os import sync
from ssl import PROTOCOL_TLSv1
from genie.testbed import load
from pyats import aetest
from pyats.results import Passed, Failed
from pyats.async_ import pcall
from unicon.eal.dialogs import Statement, Dialog
from unicon.core.errors import SubCommandFailure
from pyats.log import ScreenHandler
from pyats.log.utils import banner
from genie.conf.base import Interface, Device, Testbed, Link
from genie.libs.conf.vlan import Vlan
from genie.libs.sdk import apis
from pyats.datastructures import AttrDict
from genie.libs.sdk import apis
import sys
import logging
import pprint
import time
## Logging ##
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
log.setLevel(logging.DEBUG)
###########################################################################################
class ixia_configurations():

        

    def ixia_BGP_config(self, devices):       
        
        log.info(banner("Configuring ixia interfaces connected to UUT1"))

        config_UUT1_interface = devices['ixia'].interface_config(
                port_handle =Variables.ixia_intf1,
                autonegotiation=arp_req,
                intf_ip_addr=ipadd_ixia1,
                gateway=ixia_inf1_ipadd,
                src_mac_addr=src_mac_in_ixia1,
                arp_send_req=arp_req,
                phy_mode=phy1_mode,
                netmask=loop_mask,
                speed_autonegotiation=speed_autonegotiation
        )

        log.info(banner("Configuring ixia interfaces connected to UUT2"))
        config_UUT2_interface = devices['ixia'].interface_config(
                port_handle =Variables.ixia_intf2,
                autonegotiation=arp_req,
                intf_ip_addr=ipadd_ixia2,
                gateway=ixia_inf2_ipadd,
                arp_send_req=arp_req,
                src_mac_addr=src_mac_in_ixia2,
                netmask=loop_mask,
                data_integrity= arp_req,
                integrity_signature= integrity_signature,
                integrity_signature_offset=integrity_signature_offset,
                phy_mode=phy1_mode,
                speed_autonegotiation=speed_autonegotiation
        )
        log.info(banner("Arp send for both ixia ports connected to UUT1 and UUT2"))
        time.sleep(20)
        arp_send1 =devices['ixia'].interface_config(mode='modify',arp_send_req=1,port_handle =Variables.ixia_intf1)
        arp_send1 =devices['ixia'].interface_config(mode='modify',arp_send_req=1,port_handle =Variables.ixia_intf1)
        arp_send2 =devices['ixia'].interface_config(mode='modify',arp_send_req=1,port_handle =Variables.ixia_intf2) 
        arp_send2 =devices['ixia'].interface_config(mode='modify',arp_send_req=1,port_handle =Variables.ixia_intf2)
      
        log.info(banner("Ipv4 stream creation for both ixia ports connected to UUT1 and UUT2"))
        time.sleep(10)
        
        
        uut1_uut2_ipv4_stream=devices['ixia'].traffic_config(mode='create', 
                            name='L3_IPV4_Traffic1',transmit_mode='continuous', 
                            emulation_src_handle=Variables.ixia_intf1, 
                            emulation_dst_handle=Variables.ixia_intf2,
                            l3_protocol='ipv4',
                            frame_size= frame_size,
                            circuit_endpoint_type=protocol1, track_by="traffic_item", 
                            rate_pps=ratepps)
        log.info("sleep for 10")
        time.sleep(10)
 
        log.info(banner("CLear stats on ixia port connected to uut2"))
        devices['ixia'].traffic_control(port_handle = Variables.ixia_intf1, action = 'clear_stats')
        

        log.info(banner("Start traffic on ixia port connected to uut2"))
        devices['ixia'].traffic_control(action='run',port_handle=Variables.ixia_intf1)

        log.info("sleep for 20")
        time.sleep(20)


        log.info(banner("Stop traffic on ixia port connected to uut2"))
        devices['ixia'].traffic_control(action='stop',port_handle=Variables.ixia_intf1)

        log.info("sleep for 20")
        time.sleep(20)

        log.info(banner("Traffic stats on ixia ports connected to UUT1 and uut2"))
        ix1Stat = devices['ixia'].traffic_stats(port_handle=Variables.ixia_intf1, mode='aggregate')
        log.debug(ix1Stat)
        time.sleep(5)
        ix2Stat = devices['ixia'].traffic_stats(port_handle=Variables.ixia_intf2, mode='aggregate')
        log.debug(ix2Stat)

        log.info(banner("Checking counters connected on ixia ports connected to uut2"))
        ix1TxPckt = int(ix1Stat[Variables.ixia_intf1]['aggregate']['tx']['total_pkts'])
        log.debug(ix1TxPckt)
        ix2RxPckt = int(ix2Stat[Variables.ixia_intf2]['aggregate']['rx']['total_pkts'])
        log.debug(ix2RxPckt)

        log.info ("Traffic tx pkt count is "+ str(ix1TxPckt))
        log.info ("Traffic rx pkt count is "+ str(ix2RxPckt))

        loss_count = (ix1TxPckt - ix2RxPckt) / (int(ratepps))

        log.info ("Traffic loss in seconds"+ str(loss_count))

        
        if ix1TxPckt != 0 and ix2RxPckt !=0 :
            if loss_count >1:
                self.failed("Traffic loss seen with TCP traffic " )
            else:
                log.info("NO TRAFFIC LOSS SEEN")
        else:
            self.failed("Traffic loss seen with TCP traffic " )
    def clear_ixia_configs(self,devices):
        config_UUT1_interface = devices['ixia'].interface_config(
                mode='destroy',
                port_handle =Variables.ixia_intf1,
                autonegotiation=arp_req,
                intf_ip_addr=ipadd_ixia1,
                gateway=ixia_inf1_ipadd,
                src_mac_addr=src_mac_in_ixia1,
                arp_send_req=arp_req,
                phy_mode=phy1_mode,
                netmask=loop_mask,
                speed_autonegotiation=speed_autonegotiation
        )

        log.info(banner("Configuring ixia interfaces connected to UUT2"))
        config_UUT2_interface = devices['ixia'].interface_config(
                mode='destroy',
                port_handle =Variables.ixia_intf2,
                autonegotiation=arp_req,
                intf_ip_addr=ipadd_ixia2,
                gateway=ixia_inf2_ipadd,
                arp_send_req=arp_req,
                src_mac_addr=src_mac_in_ixia2,
                netmask=loop_mask,
                data_integrity= arp_req,
                integrity_signature= integrity_signature,
                integrity_signature_offset=integrity_signature_offset,
                phy_mode=phy1_mode,
                speed_autonegotiation=speed_autonegotiation
        )
        uut1_uut2_ipv4_stream=devices['ixia'].traffic_config(mode='reset', 
                            name='L3_IPV4_Traffic1',transmit_mode='continuous', 
                            emulation_src_handle=Variables.ixia_intf1, 
                            emulation_dst_handle=Variables.ixia_intf2,
                            l3_protocol='ipv4',
                            frame_size= frame_size,
                            circuit_endpoint_type=protocol1, track_by="traffic_item", 
                            rate_pps=ratepps)

        log.info("clear ip route")
        devices['uut1'].api.remove_routing_ip_route(ip_address=uut1_iproute,mask=loop_mask,dest_add=uut3_intf5_ipadd)
        devices['uut3'].api.remove_routing_ip_route(ip_address=uut3_iproute,mask=loop_mask,dest_add=uut1_intf5_ipadd)
        log.info("default the ixia interfaces")
        devices['uut1'].api.default_interface(Variables.dut1_intf5_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf4_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf5_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf4_list)
class ixia_ipv6_traffic():
    def assign_ip_to_ixia_interfaces(self,devices):
        devices['uut1'].api.clear_interface_counters(Variables.dut1_intf5_list[0])
        devices['uut3'].api.clear_interface_counters(Variables.dut3_intf5_list[0])
        devices['uut1'].api.clear_interface_counters(Variables.dut1_intf4_list[0])
        devices['uut3'].api.clear_interface_counters(Variables.dut3_intf4_list[0])
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf5_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf5_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf4_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf4_list)
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf5_list[0])
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf5_list[0],ipv6_address=uut1_ipv6_add_intf1)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf5_list)
        devices['uut3'].api.configure_interface_no_switchport(Variables.dut3_intf5_list[0])
        devices['uut3'].api.config_ip_on_interface(Variables.dut3_intf5_list[0],ipv6_address=uut2_ipv6_add_intf1)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf5_list)
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf4_list[0])
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf4_list[0],ipv6_address=uut1_ipv6_add_intf2)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf4_list)
        devices['uut3'].api.configure_interface_no_switchport(Variables.dut3_intf4_list[0])
        devices['uut3'].api.config_ip_on_interface(Variables.dut3_intf4_list[0],ipv6_address=uut2_ipv6_add_intf2)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf4_list)
        devices['uut1'].api.configure_routing_ipv6_route(ipv6_address=ipv6_route_add1,dest_add=uut2_ipv6_add_l3_svi)
        devices['uut3'].api.configure_routing_ipv6_route(ipv6_address=ipv6_route_add2,dest_add=uut1_ipv6_add_l3_svi)
    def ixia_ipv6_config(self, devices):       
        
        log.info(banner("Configuring ixia interfaces connected to UUT1"))
        time.sleep(30)
        config_UUT1_interface = devices['ixia'].interface_config(
                port_handle =Variables.ixia_intf1,
                autonegotiation=arp_req,
                ipv6_intf_addr=ixia_intf_ipv6_add1,
                ipv6_gateway=gateway_uut1_ipv6,
                arp_send_req=arp_req,
                ipv6_prefix_length=ipv6_prefix_length,
                speed_autonegotiation=speed_autonegotiation,
                phy_mode=phy1_mode
        )

        log.info(banner("Configuring ixia interfaces connected to UUT3"))
        config_UUT3_interface = devices['ixia'].interface_config(
                port_handle =Variables.ixia_intf2,
                autonegotiation=arp_req,
                ipv6_intf_addr=ixia_intf_ipv6_add2,
                ipv6_gateway=gateway_uut2_ipv6,
                arp_send_req=arp_req,
                ipv6_prefix_length=ipv6_prefix_length,
                data_integrity= arp_req,
                integrity_signature= integrity_signature,
                integrity_signature_offset=integrity_signature_offset,
                phy_mode=phy1_mode,
                speed_autonegotiation=speed_autonegotiation,
        )

        log.info(banner("Arp send for both ixia ports connected to UUT1 and UUT3"))
        time.sleep(20)
        arp_send1 =devices['ixia'].interface_config(mode='modify',arp_send_req=1,port_handle =Variables.ixia_intf1)
        arp_send1 =devices['ixia'].interface_config(mode='modify',arp_send_req=1,port_handle =Variables.ixia_intf1)
        arp_send1 =devices['ixia'].interface_config(mode='modify',arp_send_req=1,port_handle =Variables.ixia_intf1)
        arp_send1 =devices['ixia'].interface_config(mode='modify',arp_send_req=1,port_handle =Variables.ixia_intf1)
        arp_send2 =devices['ixia'].interface_config(mode='modify',arp_send_req=1,port_handle =Variables.ixia_intf2) 
        arp_send2 =devices['ixia'].interface_config(mode='modify',arp_send_req=1,port_handle =Variables.ixia_intf2)
        arp_send2 =devices['ixia'].interface_config(mode='modify',arp_send_req=1,port_handle =Variables.ixia_intf2)
        arp_send2 =devices['ixia'].interface_config(mode='modify',arp_send_req=1,port_handle =Variables.ixia_intf2)

        log.info(banner("Ipv6 stream creation for both ixia ports connected to UUT1 and UUT3"))
        time.sleep(20)
        
        uut1_uut2_ipv6_stream=devices['ixia'].traffic_config(mode='create', 
                            name='L3_IPV6_Traffic1',transmit_mode='continuous', 
                            emulation_src_handle=Variables.ixia_intf1, 
                            emulation_dst_handle=Variables.ixia_intf2,
                            l3_protocol='ipv6',
                            frame_size= frame_size,
                            circuit_endpoint_type=protocol2, track_by="traffic_item", 
                            rate_pps=ratepps
        )
                        

                        
        log.info(banner("TCP config on ixia port connected to UUT1"))
        time.sleep(15)
 
        log.info(banner("CLear stats on ixia port connected to uut2"))
        devices['ixia'].traffic_control(port_handle = Variables.ixia_intf1, action = 'clear_stats')
        time.sleep(30)
        log.info(banner("Start traffic on ixia port connected to uut2"))
        devices['ixia'].traffic_control(action='run',port_handle=Variables.ixia_intf1)

        log.info("sleep for 80")
        time.sleep(80)

        log.info(banner("Stop traffic on ixia port connected to uut2"))
        devices['ixia'].traffic_control(action='stop',port_handle=Variables.ixia_intf1)

        log.info("sleep for 20")
        time.sleep(20)

        log.info(banner("Traffic stats on ixia ports connected to UUT1 and uut2"))
        ix1Stat = devices['ixia'].traffic_stats(port_handle=Variables.ixia_intf1, mode='aggregate')
        log.debug(ix1Stat)
        time.sleep(5)
        ix2Stat = devices['ixia'].traffic_stats(port_handle=Variables.ixia_intf2, mode='aggregate')
        log.debug(ix2Stat)

        log.info(banner("Checking counters connected on ixia ports connected to uut2"))
        ix1TxPckt = int(ix1Stat[Variables.ixia_intf1]['aggregate']['tx']['total_pkts'])
        log.debug(ix1TxPckt)
        ix2RxPckt = int(ix2Stat[Variables.ixia_intf2]['aggregate']['rx']['total_pkts'])
        log.debug(ix2RxPckt)

        log.info ("Traffic tx pkt count is "+ str(ix1TxPckt))
        log.info ("Traffic rx pkt count is "+ str(ix2RxPckt))

        loss_count = (ix1TxPckt - ix2RxPckt) / (int(ratepps))

        log.info ("Traffic loss in seconds"+ str(loss_count))

        
        if ix1TxPckt != 0 and ix2RxPckt !=0 :
            if loss_count > 3:
                self.failed("Traffic loss seen with TCP traffic " )
            else:
                log.info("NO TRAFFIC LOSS SEEN")
        else:
            self.failed("Traffic loss seen with TCP traffic " )
  
    def clearing_configs_on_interface(self,devices):
        config_UUT1_interface = devices['ixia'].interface_config(
                mode='destroy',
                port_handle =Variables.ixia_intf1,
                autonegotiation=arp_req,
                ipv6_intf_addr=ixia_intf_ipv6_add1,
                ipv6_gateway=gateway_uut1_ipv6,
                arp_send_req=arp_req,
                ipv6_prefix_length=ipv6_prefix_length,
                speed_autonegotiation=speed_autonegotiation,
                phy_mode=phy1_mode
        )

        log.info(banner("Configuring ixia interfaces connected to UUT3"))
        config_UUT3_interface = devices['ixia'].interface_config(
                mode='destroy',
                port_handle =Variables.ixia_intf2,
                autonegotiation=arp_req,
                ipv6_intf_addr=ixia_intf_ipv6_add2,
                ipv6_gateway=gateway_uut2_ipv6,
                arp_send_req=arp_req,
                ipv6_prefix_length=ipv6_prefix_length,
                data_integrity= arp_req,
                integrity_signature= integrity_signature,
                integrity_signature_offset=integrity_signature_offset,
                speed_autonegotiation=speed_autonegotiation,
                phy_mode=phy1_mode
        )
        uut1_uut2_ipv6_stream=devices['ixia'].traffic_config(mode='reset', 
                            name='L3_IPV6_Traffic1',transmit_mode='continuous', 
                            emulation_src_handle=Variables.ixia_intf1, 
                            emulation_dst_handle=Variables.ixia_intf2,
                            l3_protocol='ipv6',
                            frame_size= frame_size,
                            circuit_endpoint_type=protocol2, track_by="traffic_item", 
                            rate_pps=ratepps)
        log.info("defaulting interfaces and ip route")

        devices['uut1'].api.default_interface(Variables.dut1_intf5_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf4_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf5_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf4_list)
        devices['uut1'].api.unconfigure_routing_ipv6_route(ipv6_address=ipv6_route_add1,dest_add=uut2_ipv6_add_l3_svi)
        devices['uut2'].api.unconfigure_routing_ipv6_route(ipv6_address=ipv6_route_add2,dest_add=uut1_ipv6_add_l3_svi)
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

class CommonSetup(aetest.CommonSetup):
    '''
    Step 1: param module: Setup Module
    Step 2: Connect to the devices cat9K uut
    '''
    @aetest.subsection
    def common_setup(self, testbed):
        ''' Common setup method for initializing test variables and parameters
        :param testbed: testbed for device connection
        '''
        if not testbed or not testbed.devices:
            log.error('No testbed was provided to script launch')
            self.failed(goto=['exit'])
        try:
            devices = {}
            ixia_ports={}
            
            ixia = testbed.devices["ixia"]
            
            devices = AttrDict(ixia=ixia)
            

            ixia_ports["ixia_intf1"] = devices.ixia.interfaces['ixia_uut1_int6']
            

            Variables.ixia_intf1=ixia_ports["ixia_intf1"]

            self.parent.parameters.update(devices=devices)
            log.info("Common Setup Completed Successfully")
            self.passed()
        except Exception as e:
            log.info("Environment setup Failed !!!")
            log.info(f'Exception{str(type(e))}, {str(e)}')
            self.failed()
        
    @aetest.subsection
    def connect_to_devices(self, steps, devices):
        """Discover and Connect the devices from testbed file"""
        with steps.start("Connect trex") as step:
            log.info(f"list Devices: {devices}")
            for device in devices.keys():
                log.info(f"Connecting to Device: {device}")
                log.info(f"Device info: {devices[device]}")
                try:
                    con=devices[device].connect()
                    log.info("this is trex connected:",con)
                    log.info(f"Connection to {device} Successful")
                except Exception as e:
                    log.info(f"Connection to {device} Unsuccessful"+str(e))
                    step.failed(f'{str(type(e))} : {str(e)}')
        

    @aetest.subsection
    def functional_configuration(self,devices):

        log.info(banner("making interfaces no shutdown"))
        

class TC_01_to_verify_sync_between_bgp_andg_igp(aetest.Testcase):

    @aetest.setup
    def setup(self):
        """ test setup """
        log.info('Test setup passed')

    @aetest.test
    def tc_01_verify_sync_between_bgp_andg_igp(self,devices):
        
        log.info(banner("ixia_traffic_L3"))
        log.info(banner('assign_ip_on_interfaces'))

        log.info(banner('assign_ixia_configurations'))
        trex_conf=ixia_configurations.ixia_BGP_config(self,devices)
        log.info('assign_ixia_configurations',trex_conf)
        log.info(banner('clearing_ixia_configurations'))
        ixia_configurations.clear_ixia_configs(self,devices)
        log.info(banner("pass all the trex setup"))
        

    @aetest.cleanup
    def cleanup(self,devices):
        log.info("default the interfaces which are used")
        

class TC_02_Verfiy_EBGP_Neighbour_by_configuring_neighbor_commands(aetest.Testcase):

    @aetest.setup
    def setup(self):
        """ test setup """
        log.info('Test setup passed')

    @aetest.test
    def tc_02_Verfiy_EBGP_Neighbour_by_configuring_neighbor_commands(self,devices):
        log.info(banner("Clear the logging buffer"))
        devices['uut1'].api.clear_logging(device=devices['uut1'])
        devices['uut2'].api.clear_logging(device=devices['uut2'])
        devices['uut3'].api.clear_logging(device=devices['uut3'])
        devices['uut4'].api.clear_logging(device=devices['uut4'])
        log.info(banner("configure_interfaces_shutdown_EBGP"))
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf1_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf2_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf1_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf2_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf4_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf5_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf1_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf2_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf3_list)
        devices['uut4'].api.configure_interfaces_unshutdown(Variables.dut4_intf1_list)
        log.info(banner("configure_vtp_mode_EBGP"))
        devices['uut1'].api.configure_vtp_mode(mode1)
        devices['uut2'].api.configure_vtp_mode(mode1)
        devices['uut3'].api.configure_vtp_mode(mode1)
        devices['uut4'].api.configure_vtp_mode(mode1)
        log.info(banner("ip_routing_EBGP"))
        for count in range(1, 5):
            devices[f'uut{count}'].api.enable_ipv6_unicast_routing()
            devices[f'uut{count}'].api.enable_ip_routing()
        log.info(banner("loopback_interface_EBGP"))
        devices['uut1'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut1_Loopback_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut2_Loopback_ip_add,mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut3_Loopback_ip_add,mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut4_Loopback_ip_add,mask=loop_mask)
        log.info(banner("assign_ip_on_vlan_EBGP"))
        devices['uut1'].api.config_ip_on_vlan(uut_vlan_id[0],ipv4_address=uut1_vlan20_ip_add,subnetmask=loop_mask)
        devices['uut1'].api.configure_interfaces_unshutdown(uut_vlan_id1)
        devices['uut1'].api.config_ip_on_vlan(uut_vlan_id[1],ipv4_address=uut1_vlan30_ip_add,subnetmask=loop_mask)
        devices['uut1'].api.configure_interfaces_unshutdown(uut_vlan_id2)
        devices['uut2'].api.config_ip_on_vlan(uut_vlan_id[0],ipv4_address=uut2_vlan20_ip_add,subnetmask=loop_mask)
        devices['uut2'].api.configure_interfaces_unshutdown(uut_vlan_id1)
        devices['uut2'].api.config_ip_on_vlan(uut_vlan_id[2],ipv4_address=uut2_vlan40_ip_add,subnetmask=loop_mask)
        devices['uut2'].api.configure_interfaces_unshutdown(uut_vlan_id3)
        devices['uut3'].api.config_ip_on_vlan(uut_vlan_id[1],ipv4_address=uut3_vlan30_ip_add,subnetmask=loop_mask)
        devices['uut3'].api.configure_interfaces_unshutdown(uut_vlan_id2)
        devices['uut4'].api.config_ip_on_vlan(uut_vlan_id[2],ipv4_address=uut4_vlan40_ip_add,subnetmask=loop_mask)
        devices['uut4'].api.configure_interfaces_unshutdown(uut_vlan_id3)
        log.info(banner("switchport_mode_on_interfaces_EBGP"))
        devices['uut1'].api.configure_interface_switchport_mode(Variables.dut1_intf1_list[0],mode=mode11)
        devices['uut1'].api.configure_interface_switchport_access_vlan(Variables.dut1_intf1_list[0],uut_vlan_id[0])
        devices['uut1'].api.configure_interface_switchport_mode(Variables.dut1_intf3_list[0],mode=mode11)
        devices['uut1'].api.configure_interface_switchport_access_vlan(Variables.dut1_intf3_list[0],uut_vlan_id[1])
        devices['uut2'].api.configure_interface_switchport_mode(Variables.dut2_intf1_list[0],mode=mode11)
        devices['uut2'].api.configure_interface_switchport_access_vlan(Variables.dut2_intf1_list[0],uut_vlan_id[0])
        devices['uut2'].api.configure_interface_switchport_mode(Variables.dut2_intf5_list[0],mode=mode11)
        devices['uut2'].api.configure_interface_switchport_access_vlan(Variables.dut2_intf5_list[0],uut_vlan_id[2])
        devices['uut3'].api.configure_interface_switchport_mode(Variables.dut3_intf3_list[0],mode=mode11)
        devices['uut3'].api.configure_interface_switchport_access_vlan(Variables.dut3_intf3_list[0],uut_vlan_id[1])
        devices['uut4'].api.configure_interface_switchport_mode(Variables.dut4_intf1_list[0],mode=mode11)
        devices['uut4'].api.configure_interface_switchport_access_vlan(Variables.dut4_intf1_list[0],uut_vlan_id[2])

        log.info(banner("configure_bgp_router_id_EBGP"))
        devices['uut1'].api.unconfigure_router_bgp_synchronization(bgp_as[0])
        devices['uut2'].api.unconfigure_router_bgp_synchronization(bgp_as[3])
        devices['uut3'].api.unconfigure_router_bgp_synchronization(bgp_as[1])
        devices['uut4'].api.unconfigure_router_bgp_synchronization(bgp_as[2])
        devices['uut1'].api.configure_bgp_log_neighbor_changes(bgp_as[0])
        devices['uut2'].api.configure_bgp_log_neighbor_changes(bgp_as[3])
        devices['uut3'].api.configure_bgp_log_neighbor_changes(bgp_as[1])
        devices['uut4'].api.configure_bgp_log_neighbor_changes(bgp_as[2])
        devices['uut1'].api.unconfigure_bgp_auto_summary(bgp_as[0])
        devices['uut2'].api.unconfigure_bgp_auto_summary(bgp_as[3])
        devices['uut3'].api.unconfigure_bgp_auto_summary(bgp_as[1])
        devices['uut4'].api.unconfigure_bgp_auto_summary(bgp_as[2])
        log.info(banner("configure_bgp_neighbor_EBGP"))
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan20_ip_add)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan30_ip_add)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan20_ip_add)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[2],neighbor_address=uut4_vlan40_ip_add)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan30_ip_add)
        devices['uut4'].api.configure_bgp_neighbor(bgp_as=bgp_as[2],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan40_ip_add)
        log.info(banner("configure_bgp_address_advertisement_EBGP"))
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[0], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[3], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[4], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[6], mask=loop_mask)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        log.info(banner("verying_ping_check_EBGP"))
        time.sleep(60)
        if devices['uut1'].api.verify_ping(uut2_vlan40_ip_add):
            log.info(f"the ping verfication for {uut2_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("1 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_vlan40_ip_add):
            log.info(f"the ping verfication for {uut4_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("2 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_vlan30_ip_add):
            log.info(f"the ping verfication for {uut3_vlan30_ip_add} is passed on dut1")
        else:
            self.failed("3 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_vlan20_ip_add):
            log.info(f"the ping verfication for {uut2_vlan20_ip_add} is passed on dut1")
        else:
            self.failed("4 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_Loopback_ip_add):
            log.info(f"the ping verfication for {uut2_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("5 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_Loopback_ip_add):
            log.info(f"the ping verfication for {uut3_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("6 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_Loopback_ip_add):
            log.info(f"the ping verfication for {uut4_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("7 ping verfication failed in dut1")
        log.info(banner("show_ip_bgp_check"))
        try:
            devices['uut1'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut2'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut3'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut4'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        log.info(banner("show ip bgp router address"))
        try:
            out=devices['uut1'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass   
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass     
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass   
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass  
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass  
        try:
            out = devices['uut3'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass  
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass  
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass

        try:
            devices['uut1'].parse(f"show ip bgp summary")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut2'].parse(f"show ip bgp summary")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut3'].parse(f"show ip bgp summary")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut4'].parse(f"show ip bgp summary")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        log.info(banner("neighbor_remove"))
        devices['uut1'].api.unconfigure_bgp_neighbor_remote_as(bgp_as=bgp_as[0],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan20_ip_add)
        devices['uut1'].api.unconfigure_bgp_neighbor_remote_as(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan30_ip_add)
        log.info(banner("ixia_traffic_L3"))
        log.info(banner('assign_ip_on_interfaces'))

        log.info(banner('assign_ixia_configurations'))
        ixia_configurations.ixia_BGP_config(self,devices)
        log.info(banner('clearing_ixia_configurations'))
        ixia_configurations.clear_ixia_configs(self,devices)
    
    @aetest.cleanup
    def cleanup(self,devices):
        log.info("default the interfaces which are used")
        devices['uut1'].api.default_interface(Variables.dut1_intf1_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf2_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf1_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf2_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf4_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf5_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf1_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf2_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf3_list)
        devices['uut4'].api.default_interface(Variables.dut4_intf1_list)
        log.info("Removing vlans which are configured")
        devices['uut1'].api.remove_virtual_interface(uut_vlan_id1)
        devices['uut1'].api.remove_virtual_interface(uut_vlan_id2)
        devices['uut2'].api.remove_virtual_interface(uut_vlan_id1)
        devices['uut2'].api.remove_virtual_interface(uut_vlan_id3)
        devices['uut3'].api.remove_virtual_interface(uut_vlan_id2)
        devices['uut4'].api.remove_virtual_interface(uut_vlan_id3)
        log.info("removing loopback interfaces which are configured")
        devices['uut1'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut2'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut3'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut4'].api.remove_virtual_interface(remove_loopback_intf)
        log.info("removing bgp routers which are configured")
        devices['uut1'].api.remove_bgp_configuration(bgp_as[0])
        devices['uut2'].api.remove_bgp_configuration(bgp_as[3])
        devices['uut3'].api.remove_bgp_configuration(bgp_as[1])
        devices['uut4'].api.remove_bgp_configuration(bgp_as[2])

class TC_03_verify_devices_with_multihop_configs(aetest.Testcase):
    @aetest.setup
    def setup(self):
        """ test setup """
        log.info('Test setup passed')
        
    @aetest.test
    def tc_03verify_devices_with_multihop_configs(self,devices):
        log.info("Clear the logging buffer")
        devices['uut1'].api.clear_logging(device=devices['uut1'])
        devices['uut2'].api.clear_logging(device=devices['uut2'])
        devices['uut3'].api.clear_logging(device=devices['uut3'])
        devices['uut4'].api.clear_logging(device=devices['uut4'])
        log.info(banner("configure_interfaces_shutdown_multihop"))
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf1_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf2_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf1_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf2_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf4_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf5_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf1_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf2_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf3_list)
        devices['uut4'].api.configure_interfaces_unshutdown(Variables.dut4_intf1_list)
        log.info(banner("configure_vtp_mode_multihop"))
        devices['uut1'].api.configure_vtp_mode(mode1)
        devices['uut2'].api.configure_vtp_mode(mode1)
        devices['uut3'].api.configure_vtp_mode(mode1)
        devices['uut4'].api.configure_vtp_mode(mode1)
        log.info(banner("ip_routing_multihop"))
        devices['uut1'].api.enable_ip_routing()
        devices['uut2'].api.enable_ip_routing()
        devices['uut3'].api.enable_ip_routing()
        devices['uut4'].api.enable_ip_routing()
        log.info(banner("loopback_interface_multihop"))
        devices['uut1'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut1_Loopback_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut2_Loopback_ip_add,mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut3_Loopback_ip_add,mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut4_Loopback_ip_add,mask=loop_mask)
        log.info(banner("assign_ip_on_vlan_multihop"))
        devices['uut1'].api.config_ip_on_vlan(uut_vlan_id[0],ipv4_address=uut1_vlan20_ip_add,subnetmask=loop_mask)
        devices['uut1'].api.configure_interfaces_unshutdown(uut_vlan_id1)
        devices['uut1'].api.config_ip_on_vlan(uut_vlan_id[1],ipv4_address=uut1_vlan30_ip_add,subnetmask=loop_mask)
        devices['uut1'].api.configure_interfaces_unshutdown(uut_vlan_id2)
        devices['uut2'].api.config_ip_on_vlan(uut_vlan_id[0],ipv4_address=uut2_vlan20_ip_add,subnetmask=loop_mask)
        devices['uut2'].api.configure_interfaces_unshutdown(uut_vlan_id1)
        devices['uut2'].api.config_ip_on_vlan(uut_vlan_id[2],ipv4_address=uut2_vlan40_ip_add,subnetmask=loop_mask)
        devices['uut2'].api.configure_interfaces_unshutdown(uut_vlan_id3)
        devices['uut3'].api.config_ip_on_vlan(uut_vlan_id[1],ipv4_address=uut3_vlan30_ip_add,subnetmask=loop_mask)
        devices['uut3'].api.configure_interfaces_unshutdown(uut_vlan_id2)
        devices['uut4'].api.config_ip_on_vlan(uut_vlan_id[2],ipv4_address=uut4_vlan40_ip_add,subnetmask=loop_mask)
        devices['uut4'].api.configure_interfaces_unshutdown(uut_vlan_id3)
        log.info(banner("switchport_mode_on_interfaces_multihop"))
        devices['uut1'].api.configure_interface_switchport_mode(Variables.dut1_intf1_list[0],mode=mode11)
        devices['uut1'].api.configure_interface_switchport_access_vlan(Variables.dut1_intf1_list[0],uut_vlan_id[0])
        devices['uut1'].api.configure_interface_switchport_mode(Variables.dut1_intf3_list[0],mode=mode11)
        devices['uut1'].api.configure_interface_switchport_access_vlan(Variables.dut1_intf3_list[0],uut_vlan_id[1])
        devices['uut2'].api.configure_interface_switchport_mode(Variables.dut2_intf1_list[0],mode=mode11)
        devices['uut2'].api.configure_interface_switchport_access_vlan(Variables.dut2_intf1_list[0],uut_vlan_id[0])
        devices['uut2'].api.configure_interface_switchport_mode(Variables.dut2_intf5_list[0],mode=mode11)
        devices['uut2'].api.configure_interface_switchport_access_vlan(Variables.dut2_intf5_list[0],uut_vlan_id[2])
        devices['uut3'].api.configure_interface_switchport_mode(Variables.dut3_intf3_list[0],mode=mode11)
        devices['uut3'].api.configure_interface_switchport_access_vlan(Variables.dut3_intf3_list[0],uut_vlan_id[1])
        devices['uut4'].api.configure_interface_switchport_mode(Variables.dut4_intf1_list[0],mode=mode11)
        devices['uut4'].api.configure_interface_switchport_access_vlan(Variables.dut4_intf1_list[0],uut_vlan_id[2])
        log.info(banner("configure_bgp_router_id_multihop"))
        devices['uut1'].api.unconfigure_router_bgp_synchronization(bgp_as[0])
        devices['uut2'].api.unconfigure_router_bgp_synchronization(bgp_as[3])
        devices['uut3'].api.unconfigure_router_bgp_synchronization(bgp_as[1])
        devices['uut4'].api.unconfigure_router_bgp_synchronization(bgp_as[2])
        devices['uut1'].api.configure_bgp_log_neighbor_changes(bgp_as[0])
        devices['uut2'].api.configure_bgp_log_neighbor_changes(bgp_as[3])
        devices['uut3'].api.configure_bgp_log_neighbor_changes(bgp_as[1])
        devices['uut4'].api.configure_bgp_log_neighbor_changes(bgp_as[2])
        devices['uut1'].api.unconfigure_bgp_auto_summary(bgp_as[0])
        devices['uut2'].api.unconfigure_bgp_auto_summary(bgp_as[3])
        devices['uut3'].api.unconfigure_bgp_auto_summary(bgp_as[1])
        devices['uut4'].api.unconfigure_bgp_auto_summary(bgp_as[2])
        log.info(banner("configure_bgp_neighbor_multihop"))
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[0], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan30_ip_add)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[2],neighbor_address=uut4_vlan40_ip_add)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[4], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan30_ip_add)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[6], mask=loop_mask)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        devices['uut4'].api.configure_bgp_neighbor(bgp_as=bgp_as[2],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan40_ip_add)
        log.info(banner("configure_remote_neighbor_EBGP_Multihop"))
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[3], mask=loop_mask)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[3],neighbor_address=uut2_Loopback_ip_add,ebgp=ebgp)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[0], mask=loop_mask)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[0],neighbor_address=uut1_Loopback_ip_add,ebgp=ebgp,source_interface=intf_Loopback_num)
        log.info(banner("configure_ip_route_on_uut1_and_uut2"))
        devices['uut1'].api.configure_routing_ip_route(ip_address=network_ip_add[3],mask=loop_mask,dest_add=uut2_vlan20_ip_add)
        devices['uut2'].api.configure_routing_ip_route(ip_address=network_ip_add[0],mask=loop_mask,dest_add=uut1_vlan20_ip_add)
        log.info(banner("verying_ping_check_for_multi_hop"))
        time.sleep(60)
        if devices['uut1'].api.verify_ping(uut2_vlan40_ip_add):
            log.info(f"the ping verfication for {uut2_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("1 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_vlan40_ip_add):
            log.info(f"the ping verfication for {uut4_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("2 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_vlan30_ip_add):
            log.info(f"the ping verfication for {uut3_vlan30_ip_add} is passed on dut1")
        else:
            self.failed("3 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_vlan20_ip_add):
            log.info(f"the ping verfication for {uut2_vlan20_ip_add} is passed on dut1")
        else:
            self.failed("4 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_Loopback_ip_add):
            log.info(f"the ping verfication for {uut2_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("5 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_Loopback_ip_add):
            log.info(f"the ping verfication for {uut3_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("6 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_Loopback_ip_add):
            log.info(f"the ping verfication for {uut4_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("7 ping verfication failed in dut1")
        log.info(banner("ixia_traffic_L3"))
        log.info(banner('assign_ip_on_interfaces'))
        ixia_configurations.assign_ip_to_ixia_interfaces(self,devices)
        log.info(banner('assign_ixia_configurations'))
        ixia_configurations.ixia_BGP_config(self,devices)
        log.info(banner('clearing_ixia_configurations'))
        ixia_configurations.clear_ixia_configs(self,devices)
        log.info(banner("show_commands_check"))
        devices['uut1'].api.get_show_output_include(command=f'show ip bgp neighbor {uut2_Loopback_ip_add}', filter="BGP")
        devices['uut1'].api.get_show_output_include(command=f'show ip bgp neighbor {uut3_vlan30_ip_add}', filter="BGP")
        devices['uut2'].api.get_show_output_include(command=f'show ip bgp neighbor {uut1_Loopback_ip_add}', filter="BGP")
        devices['uut2'].api.get_show_output_include(command=f'show ip bgp neighbor {uut4_vlan40_ip_add}', filter="BGP")
        devices['uut3'].api.get_show_output_include(command=f'show ip bgp neighbor {uut1_vlan30_ip_add}', filter="BGP")
        devices['uut4'].api.get_show_output_include(command=f'show ip bgp neighbor {uut2_vlan40_ip_add}', filter="BGP")

    @aetest.cleanup
    def cleanup(self,devices):
        log.info("default the interfaces which are used")
        devices['uut1'].api.default_interface(Variables.dut1_intf1_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf2_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf1_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf2_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf4_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf5_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf1_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf2_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf3_list)
        devices['uut4'].api.default_interface(Variables.dut4_intf1_list)
        log.info("Removing vlans which are configured")
        devices['uut1'].api.remove_virtual_interface(uut_vlan_id1)
        devices['uut1'].api.remove_virtual_interface(uut_vlan_id2)
        devices['uut2'].api.remove_virtual_interface(uut_vlan_id1)
        devices['uut2'].api.remove_virtual_interface(uut_vlan_id3)
        devices['uut3'].api.remove_virtual_interface(uut_vlan_id2)
        devices['uut4'].api.remove_virtual_interface(uut_vlan_id3)
        log.info("removing loopback interfaces which are configured")
        devices['uut1'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut2'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut3'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut4'].api.remove_virtual_interface(remove_loopback_intf)
        log.info("removing bgp routers which are configured")
        devices['uut1'].api.remove_bgp_configuration(bgp_as[0])
        devices['uut2'].api.remove_bgp_configuration(bgp_as[3])
        devices['uut3'].api.remove_bgp_configuration(bgp_as[1])
        devices['uut4'].api.remove_bgp_configuration(bgp_as[2])
        log.info("unconfigure the ip route")
        devices['uut1'].api.remove_routing_ip_route(ip_address=network_ip_add[3],mask=loop_mask,dest_add=uut2_vlan20_ip_add)
        devices['uut2'].api.remove_routing_ip_route(ip_address=network_ip_add[0],mask=loop_mask,dest_add=uut1_vlan20_ip_add)

class TC_04_verify_load_balance_two_EBGP_over_paralle_lines(aetest.Testcase):

    @aetest.setup
    def setup(self):
        """ test setup """
        log.info('Test setup passed')

    @aetest.test
    def tc_04_verify_load_balance_two_EBGP_over_paralle_lines(self,devices):
        log.info("Clear the logging buffer")
        devices['uut1'].api.clear_logging(device=devices['uut1'])
        devices['uut2'].api.clear_logging(device=devices['uut2'])
        devices['uut3'].api.clear_logging(device=devices['uut3'])
        devices['uut4'].api.clear_logging(device=devices['uut4'])
        log.info(banner("configure_interfaces_shutdown_load_test"))
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf1_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf2_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf1_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf2_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf4_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf5_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf1_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf2_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf3_list)
        devices['uut4'].api.configure_interfaces_unshutdown(Variables.dut4_intf1_list)
        log.info(banner("configure_vtp_mode_load_test"))
        devices['uut1'].api.configure_vtp_mode(mode1)
        devices['uut2'].api.configure_vtp_mode(mode1)
        devices['uut3'].api.configure_vtp_mode(mode1)
        devices['uut4'].api.configure_vtp_mode(mode1)
        log.info(banner("ip_routing_load_test"))
        devices['uut1'].api.enable_ip_routing()
        devices['uut2'].api.enable_ip_routing()
        devices['uut3'].api.enable_ip_routing()
        devices['uut4'].api.enable_ip_routing()
        log.info(banner("loopback_interface_load_test"))
        devices['uut1'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut1_Loopback_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut2_Loopback_ip_add,mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut3_Loopback_ip_add,mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut4_Loopback_ip_add,mask=loop_mask)
        log.info(banner("no_switchport_on_interfaces"))
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf1_list[0])
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf2_list[0])
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf3_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf1_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf2_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf5_list[0])
        devices['uut3'].api.configure_interface_no_switchport(Variables.dut3_intf3_list[0])
        devices['uut4'].api.configure_interface_no_switchport(Variables.dut4_intf1_list[0])
        log.info(banner("assign_ip_on_interfaces"))
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf1_list[0],ip_address=uut1_vlan20_ip_add,mask=loop_mask)
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf2_list[0],ip_address=uut_ip_add_intf[0],mask=loop_mask)
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf3_list[0],ip_address=uut1_vlan30_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(Variables.dut2_intf1_list[0],ip_address=uut2_vlan20_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(Variables.dut2_intf2_list[0],ip_address=uut_ip_add_intf[1],mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(Variables.dut2_intf5_list[0],ip_address=uut2_vlan40_ip_add,mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(Variables.dut3_intf3_list[0],ip_address=uut3_vlan30_ip_add,mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(Variables.dut4_intf1_list[0],ip_address=uut4_vlan40_ip_add,mask=loop_mask)
        log.info(banner("configure_bgp_router_id_load_test"))
        devices['uut1'].api.unconfigure_router_bgp_synchronization(bgp_as[0])
        devices['uut2'].api.unconfigure_router_bgp_synchronization(bgp_as[3])
        devices['uut3'].api.unconfigure_router_bgp_synchronization(bgp_as[1])
        devices['uut4'].api.unconfigure_router_bgp_synchronization(bgp_as[2])
        devices['uut1'].api.configure_bgp_log_neighbor_changes(bgp_as[0])
        devices['uut2'].api.configure_bgp_log_neighbor_changes(bgp_as[3])
        devices['uut3'].api.configure_bgp_log_neighbor_changes(bgp_as[1])
        devices['uut4'].api.configure_bgp_log_neighbor_changes(bgp_as[2])
        devices['uut1'].api.unconfigure_bgp_auto_summary(bgp_as[0])
        devices['uut2'].api.unconfigure_bgp_auto_summary(bgp_as[3])
        devices['uut3'].api.unconfigure_bgp_auto_summary(bgp_as[1])
        devices['uut4'].api.unconfigure_bgp_auto_summary(bgp_as[2])
        log.info(banner("configure_bgp_neighbor_multihop"))
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[0], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=uut_ip_add_intf[2], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan30_ip_add)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[3], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=uut_ip_add_intf[2], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[2],neighbor_address=uut4_vlan40_ip_add)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[4], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan30_ip_add)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[6], mask=loop_mask)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        devices['uut4'].api.configure_bgp_neighbor(bgp_as=bgp_as[2],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan40_ip_add)
        log.info(banner("configure_remote_neighbor_EBGP_loadtest"))
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[3], mask=loop_mask)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[3],neighbor_address=uut2_Loopback_ip_add,ebgp=ebgp)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[0], mask=loop_mask)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[0],neighbor_address=uut1_Loopback_ip_add,ebgp=ebgp,source_interface=intf_Loopback_num)
        log.info(banner("configure_ip_route_on_uut1_and_uut2"))
        devices['uut1'].api.configure_routing_ip_route(ip_address=network_ip_add[3],mask=loop_mask,dest_add=uut2_vlan20_ip_add)
        devices['uut1'].api.configure_routing_ip_route(ip_address=network_ip_add[3],mask=loop_mask,dest_add=uut_ip_add_intf[1])
        devices['uut2'].api.configure_routing_ip_route(ip_address=network_ip_add[0],mask=loop_mask,dest_add=uut1_vlan20_ip_add)
        devices['uut2'].api.configure_routing_ip_route(ip_address=network_ip_add[0],mask=loop_mask,dest_add=uut_ip_add_intf[0])
        log.info(banner("show_commands"))
        devices['uut1'].parse(f"show ip route")
        devices['uut2'].parse(f"show ip route")
        devices['uut3'].parse(f"show ip route")
        devices['uut4'].parse(f"show ip route")
        log.info(banner("show_ip_bgp_check"))
        devices['uut1'].parse(f"show ip bgp")
        devices['uut2'].parse(f"show ip bgp")
        devices['uut3'].parse(f"show ip bgp")
        devices['uut4'].parse(f"show ip bgp")
        try:
            out = devices['uut1'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {route}")
            
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        out=devices['uut1'].api.get_show_output_include(command=f'show ip bgp neighbor {uut2_Loopback_ip_add}', filter="BGP")
        devices['uut1'].api.get_show_output_include(command=f'show ip bgp neighbor {uut3_vlan30_ip_add}', filter="BGP")
        devices['uut2'].api.get_show_output_include(command=f'show ip bgp neighbor {uut1_Loopback_ip_add}', filter="BGP")
        devices['uut2'].api.get_show_output_include(command=f'show ip bgp neighbor {uut4_vlan40_ip_add}', filter="BGP")
        devices['uut3'].api.get_show_output_include(command=f'show ip bgp neighbor {uut1_vlan30_ip_add}', filter="BGP")
        devices['uut4'].api.get_show_output_include(command=f'show ip bgp neighbor {uut2_vlan40_ip_add}', filter="BGP")
        log.info(banner("unconfigure_ip_route"))
        devices['uut1'].api.remove_routing_ip_route(ip_address=network_ip_add[3],mask=loop_mask,dest_add=uut_ip_add_intf[1])
        devices['uut2'].api.remove_routing_ip_route(ip_address=network_ip_add[0],mask=loop_mask,dest_add=uut_ip_add_intf[0])
        devices['uut1'].parse(f"show ip route")
        devices['uut2'].parse(f"show ip route")
        log.info(banner("ixia_ipv6_traffic"))
        log.info(banner('assign_ip_on_interfaces'))
        ixia_ipv6_traffic.assign_ip_to_ixia_interfaces(self,devices)
        log.info(banner('assign_ixia_configurations'))
        ixia_ipv6_traffic.ixia_ipv6_config(self, devices)
        log.info(banner('clearing_ixia_configurations'))
        ixia_ipv6_traffic.clearing_configs_on_interface(self, devices)


    @aetest.cleanup
    def cleanup(self,devices):
        log.info("default the interfaces which are used")
        devices['uut1'].api.default_interface(Variables.dut1_intf1_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf2_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf1_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf2_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf4_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf5_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf1_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf2_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf3_list)
        devices['uut4'].api.default_interface(Variables.dut4_intf1_list)
        log.info("removing loopback interfaces which are configured")
        devices['uut1'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut2'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut3'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut4'].api.remove_virtual_interface(remove_loopback_intf)
        log.info("removing bgp routers which are configured")
        devices['uut1'].api.remove_bgp_configuration(bgp_as[0])
        devices['uut2'].api.remove_bgp_configuration(bgp_as[3])
        devices['uut3'].api.remove_bgp_configuration(bgp_as[1])
        devices['uut4'].api.remove_bgp_configuration(bgp_as[2])
        log.info("unconfiguring the ip route")
        devices['uut1'].api.remove_routing_ip_route(ip_address=network_ip_add[3],mask=loop_mask,dest_add=uut2_vlan20_ip_add)
        devices['uut2'].api.remove_routing_ip_route(ip_address=network_ip_add[0],mask=loop_mask,dest_add=uut1_vlan20_ip_add)

class TC_05_verify_removed_network_dropped_from_BGP(aetest.Testcase):

    @aetest.setup
    def setup(self):
        """ test setup """
        log.info('Test setup passed')

    @aetest.test
    def tc_05_verify_removed_network_dropped_from_BGP(self,devices):
        log.info("Clear the logging buffer")
        devices['uut1'].api.clear_logging(device=devices['uut1'])
        devices['uut2'].api.clear_logging(device=devices['uut2'])
        devices['uut3'].api.clear_logging(device=devices['uut3'])
        devices['uut4'].api.clear_logging(device=devices['uut4'])
        log.info(banner("defaul_interfaces"))
        devices['uut1'].api.default_interface(Variables.dut1_intf1_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf2_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf1_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf2_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf4_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf5_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf1_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf2_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf3_list)
        devices['uut4'].api.default_interface(Variables.dut4_intf1_list)
        log.info(banner("configure_interfaces_shutdown_load_test"))
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf1_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf2_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf1_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf2_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf4_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf5_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf1_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf2_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf3_list)
        devices['uut4'].api.configure_interfaces_unshutdown(Variables.dut4_intf1_list)
        log.info(banner("configure_vtp_mode_load_test"))
        devices['uut1'].api.configure_vtp_mode(mode1)
        devices['uut2'].api.configure_vtp_mode(mode1)
        devices['uut3'].api.configure_vtp_mode(mode1)
        devices['uut4'].api.configure_vtp_mode(mode1)
        log.info(banner("ip_routing_load_test"))
        devices['uut1'].api.enable_ip_routing()
        devices['uut2'].api.enable_ip_routing()
        devices['uut3'].api.enable_ip_routing()
        devices['uut4'].api.enable_ip_routing()
        log.info(banner("loopback_interface_load_test"))
        devices['uut1'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut1_Loopback_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut2_Loopback_ip_add,mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut3_Loopback_ip_add,mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut4_Loopback_ip_add,mask=loop_mask)
        log.info(banner("no_switchport_on_interfaces"))
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf1_list[0])
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf2_list[0])
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf3_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf1_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf2_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf5_list[0])
        devices['uut3'].api.configure_interface_no_switchport(Variables.dut3_intf3_list[0])
        devices['uut4'].api.configure_interface_no_switchport(Variables.dut4_intf1_list[0])
        log.info(banner("assign_ip_on_interfaces"))
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf1_list[0],ip_address=inf_ip_add_list[0],mask=loop_mask)
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf3_list[0],ip_address=uut1_vlan20_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(Variables.dut2_intf1_list[0],ip_address=inf_ip_add_list[1],mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(Variables.dut2_intf5_list[0],ip_address=inf_ip_add_list[2],mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(Variables.dut3_intf3_list[0],ip_address=inf_ip_add_list[3],mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(Variables.dut4_intf1_list[0],ip_address=inf_ip_add_list[4],mask=loop_mask)
        log.info(banner("configure_bgp_router_id_load_test"))
        devices['uut1'].api.unconfigure_router_bgp_synchronization(bgp_as[0])
        devices['uut2'].api.unconfigure_router_bgp_synchronization(bgp_as[0])
        devices['uut3'].api.unconfigure_router_bgp_synchronization(bgp_as[0])
        devices['uut4'].api.unconfigure_router_bgp_synchronization(bgp_as[0])
        devices['uut1'].api.configure_bgp_log_neighbor_changes(bgp_as[0])
        devices['uut2'].api.configure_bgp_log_neighbor_changes(bgp_as[0])
        devices['uut3'].api.configure_bgp_log_neighbor_changes(bgp_as[0])
        devices['uut4'].api.configure_bgp_log_neighbor_changes(bgp_as[0])
        devices['uut1'].api.unconfigure_bgp_auto_summary(bgp_as[0])
        devices['uut2'].api.unconfigure_bgp_auto_summary(bgp_as[0])
        devices['uut3'].api.unconfigure_bgp_auto_summary(bgp_as[0])
        devices['uut4'].api.unconfigure_bgp_auto_summary(bgp_as[0])
        log.info(banner("configure_bgp_neighbor_multihop"))
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=inf_ip_add_list[5], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[0], mask=loop_mask)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[0],neighbor_address=inf_ip_add_list[1])
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[0],neighbor_address=inf_ip_add_list[3])
        devices['uut1'].api.configure_bgp_address_family_attributes(bgp_as=bgp_as[0], address_family=address_family,neighbor=inf_ip_add_list[3],route_reflector_client=True)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=inf_ip_add_list[5], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[3], mask=loop_mask)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[0],neighbor_address=inf_ip_add_list[0])
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[0],neighbor_address=inf_ip_add_list[4])
        devices['uut2'].api.configure_bgp_address_family_attributes(bgp_as=bgp_as[0], address_family=address_family,neighbor=inf_ip_add_list[4],route_reflector_client=True)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[4], mask=loop_mask)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan20_ip_add)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[6], mask=loop_mask)
        devices['uut4'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[0],neighbor_address=inf_ip_add_list[2])
        log.info(banner("verying_ping_check_for_multi_hop"))
        time.sleep(60)
        if devices['uut1'].api.verify_ping(inf_ip_add_list[3]):
            log.info(f"the ping verfication for {inf_ip_add_list[3]} is passed on dut1")
        else:
            self.failed("1 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(inf_ip_add_list[1]):
            log.info(f"the ping verfication for {inf_ip_add_list[1]} is passed on dut1")
        else:
            self.failed("2 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(inf_ip_add_list[2]):
            log.info(f"the ping verfication for {inf_ip_add_list[2]} is passed on dut1")
        else:
            self.failed("3 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(inf_ip_add_list[4]):
            log.info(f"the ping verfication for {inf_ip_add_list[4]} is passed on dut1")
        else:
            self.failed("4 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_Loopback_ip_add):
            log.info(f"the ping verfication for {uut2_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("5 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_Loopback_ip_add):
            log.info(f"the ping verfication for {uut3_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("6 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_Loopback_ip_add):
            log.info(f"the ping verfication for {uut4_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("7 ping verfication failed in dut1")
        log.info(banner("showcommands_check_1"))
        try:
            out1=devices['uut1'].parse("show ip route")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup'])
        try: 
            out2=devices['uut1'].parse(f"show ip route {protocol}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out3=devices['uut1'].parse(f"sh ip bgp neighbor {inf_ip_add_list[1]}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out4=devices['uut1'].parse(f"sh ip bgp neighbor {inf_ip_add_list[3]}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out5=devices['uut2'].parse(f"sh ip bgp neighbor {inf_ip_add_list[4]}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out6=devices['uut2'].parse("show ip route")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out7=devices['uut2'].parse(f"show ip route {protocol}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out8=devices['uut3'].parse(f"show ip bgp neighbors {uut1_vlan20_ip_add}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out9=devices['uut3'].parse("show ip route")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out10=devices['uut3'].parse(f"show ip route {protocol}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out11=devices['uut4'].parse(f"sh ip bgp neighbor {inf_ip_add_list[2]}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out12=devices['uut4'].parse("show ip route")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out13=devices['uut4'].parse(f"show ip route {protocol}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        log.info(banner("removing_bgp_on_switches"))
        devices['uut4'].api.remove_bgp_configuration(bgp_as[0])
        time.sleep(30)
        if devices['uut1'].api.verify_ping(inf_ip_add_list[3]):
            log.info(f"the ping verfication for {inf_ip_add_list[3]} is passed on dut1")
        else:
            self.failed("1 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(inf_ip_add_list[1]):
            log.info(f"the ping verfication for {inf_ip_add_list[1]} is passed on dut1")
        else:
            self.failed("2 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(inf_ip_add_list[2]):
            log.info(f"the ping verfication for {inf_ip_add_list[2]} is passed on dut1")
        else:
            self.failed("3 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_Loopback_ip_add):
            log.info(f"the ping verfication for {uut2_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("4 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_Loopback_ip_add):
            log.info(f"the ping verfication for {uut3_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("5 ping verfication failed in dut1")
        try:
            out1=devices['uut1'].parse("show ip route")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out2=devices['uut1'].parse(f"show ip route {protocol}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out3=devices['uut1'].parse(f"show ip bgp neighbors {inf_ip_add_list[1]}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out4=devices['uut1'].parse(f"show ip bgp neighbors {inf_ip_add_list[3]}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out5=devices['uut2'].parse(f"show ip bgp neighbors {inf_ip_add_list[0]}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out6=devices['uut2'].parse("show ip route")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out7=devices['uut2'].parse(f"show ip route {protocol}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out9=devices['uut3'].parse("show ip route")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out10=devices['uut3'].parse(f"show ip route {uut1_vlan20_ip_add}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out9=devices['uut4'].parse("show ip route")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        log.info("removing ip address on uut2")
        devices['uut2'].api.remove_bgp_configuration(bgp_as[0])
        time.sleep(30)
        if devices['uut1'].api.verify_ping(inf_ip_add_list[3]):
            log.info(f"the ping verfication for {inf_ip_add_list[3]} is passed on dut1")
        else:
            self.failed("1 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_Loopback_ip_add):
            log.info(f"the ping verfication for {uut3_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("2 ping verfication failed in dut1")
        try:
            out1=devices['uut1'].parse("show ip route")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup']) 
        try:
            out2=devices['uut1'].parse(f"show ip route {protocol}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup'])
        try:
            out4=devices['uut1'].parse(f"show ip bgp neighbors {inf_ip_add_list[3]}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup'])
        try:
            out6=devices['uut2'].parse("show ip route")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup'])
        try:
            out10=devices['uut3'].parse(f"show ip route {uut1_vlan20_ip_add}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup'])
        try:
            out9=devices['uut3'].parse("show ip route")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup'])
        try:
            out10=devices['uut3'].parse(f"show ip route {protocol}")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup'])
        try:
            out6=devices['uut4'].parse("show ip route")
        except Exception as e:
            self.failed("bgp route not present or parser output is empty", goto=['common_cleanup'])
        log.info(banner("ixia_traffic_L3"))
        log.info(banner('assign_ip_on_interfaces'))
        ixia_configurations.assign_ip_to_ixia_interfaces(self,devices)
        log.info(banner('assign_ixia_configurations'))
        ixia_configurations.ixia_BGP_config(self,devices)
        log.info(banner('clearing_ixia_configurations'))
        ixia_configurations.clear_ixia_configs(self,devices)

    @aetest.cleanup
    def cleanup(self,devices):
        log.info("default the interfaces which are used")
        devices['uut1'].api.default_interface(Variables.dut1_intf1_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf2_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf1_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf2_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf4_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf5_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf1_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf2_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf3_list)
        devices['uut4'].api.default_interface(Variables.dut4_intf1_list)
        log.info("removing loopback interfaces which are configured")
        devices['uut1'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut2'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut3'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut4'].api.remove_virtual_interface(remove_loopback_intf)
        log.info("removing bgp routers which are configured")
        devices['uut1'].api.remove_bgp_configuration(bgp_as[0])
        devices['uut2'].api.remove_bgp_configuration(bgp_as[0])
        devices['uut3'].api.remove_bgp_configuration(bgp_as[0])
        devices['uut4'].api.remove_bgp_configuration(bgp_as[0])

class TC_06_new_Ebgp_routes_added_to_BGP_Table(aetest.Testcase):

    @aetest.setup
    def setup(self):
        """ test setup """
        log.info('Test setup passed')

    @aetest.test
    def tc_06_new_Ebgp_routes_added_to_BGP_Table(self,devices):
        log.info("Clear the logging buffer")
        devices['uut1'].api.clear_logging(device=devices['uut1'])
        devices['uut2'].api.clear_logging(device=devices['uut2'])
        devices['uut3'].api.clear_logging(device=devices['uut3'])
        devices['uut4'].api.clear_logging(device=devices['uut4'])
        log.info(banner("configure_interfaces_shutdown_load_test"))
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf1_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf2_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf1_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf2_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf4_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf5_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf1_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf2_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf3_list)
        devices['uut4'].api.configure_interfaces_unshutdown(Variables.dut4_intf1_list)
        log.info(banner("configure_vtp_mode_EBGP_BGP"))
        devices['uut1'].api.configure_vtp_mode(mode1)
        devices['uut2'].api.configure_vtp_mode(mode1)
        devices['uut3'].api.configure_vtp_mode(mode1)
        devices['uut4'].api.configure_vtp_mode(mode1)
        log.info(banner("ip_routing_EBGP_BGP"))
        devices['uut1'].api.enable_ip_routing()
        devices['uut2'].api.enable_ip_routing()
        devices['uut3'].api.enable_ip_routing()
        devices['uut4'].api.enable_ip_routing()
        log.info(banner("loopback_interface_EBGP_BGP"))
        devices['uut1'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut1_Loopback_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut2_Loopback_ip_add,mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut3_Loopback_ip_add,mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut4_Loopback_ip_add,mask=loop_mask)
        log.info(banner("no_switchport_on_interfacesEBGP_BGP"))
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf1_list[0])
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf2_list[0])
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf3_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf1_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf2_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf5_list[0])
        devices['uut3'].api.configure_interface_no_switchport(Variables.dut3_intf3_list[0])
        devices['uut4'].api.configure_interface_no_switchport(Variables.dut4_intf1_list[0])
        log.info(banner("assign_ip_on_interface_EBGP_BGP"))
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf1_list[0],ip_address=inf_ip_add_list[0],mask=loop_mask)
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf3_list[0],ip_address=uut1_vlan20_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(Variables.dut2_intf1_list[0],ip_address=inf_ip_add_list[1],mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(Variables.dut2_intf5_list[0],ip_address=inf_ip_add_list[2],mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(Variables.dut3_intf3_list[0],ip_address=inf_ip_add_list[3],mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(Variables.dut4_intf1_list[0],ip_address=inf_ip_add_list[4],mask=loop_mask)
        log.info(banner("configure_bgp_router_id_load_test"))
        devices['uut1'].api.unconfigure_router_bgp_synchronization(bgp_as[0])
        devices['uut2'].api.unconfigure_router_bgp_synchronization(bgp_as[3])
        devices['uut3'].api.unconfigure_router_bgp_synchronization(bgp_as[1])
        devices['uut4'].api.unconfigure_router_bgp_synchronization(bgp_as[2])
        devices['uut1'].api.configure_bgp_log_neighbor_changes(bgp_as[0])
        devices['uut2'].api.configure_bgp_log_neighbor_changes(bgp_as[3])
        devices['uut3'].api.configure_bgp_log_neighbor_changes(bgp_as[1])
        devices['uut4'].api.configure_bgp_log_neighbor_changes(bgp_as[2])
        devices['uut1'].api.unconfigure_bgp_auto_summary(bgp_as[0])
        devices['uut2'].api.unconfigure_bgp_auto_summary(bgp_as[3])
        devices['uut3'].api.unconfigure_bgp_auto_summary(bgp_as[1])
        devices['uut4'].api.unconfigure_bgp_auto_summary(bgp_as[2])
        log.info(banner("configure_bgp_neighbor_multihop"))
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=inf_ip_add_list[5], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[0], mask=loop_mask)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[3],neighbor_address=inf_ip_add_list[1])
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=inf_ip_add_list[3])
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=inf_ip_add_list[5], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[3], mask=loop_mask)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[0],neighbor_address=inf_ip_add_list[0])
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[2],neighbor_address=inf_ip_add_list[4])
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[4], mask=loop_mask)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan20_ip_add)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[6], mask=loop_mask)
        devices['uut4'].api.configure_bgp_neighbor(bgp_as=bgp_as[2],neighbor_as=bgp_as[3],neighbor_address=inf_ip_add_list[2])
        log.info(banner("verying_ping_check_for_EBGP_BGP"))
        time.sleep(60)
        if devices['uut1'].api.verify_ping(inf_ip_add_list[3]):
            log.info(f"the ping verfication for {inf_ip_add_list[3]} is passed on dut1")
        else:
            self.failed("1 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(inf_ip_add_list[1]):
            log.info(f"the ping verfication for {inf_ip_add_list[1]} is passed on dut1")
        else:
            self.failed("2 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(inf_ip_add_list[2]):
            log.info(f"the ping verfication for {inf_ip_add_list[2]} is passed on dut1")
        else:
            self.failed("3 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(inf_ip_add_list[4]):
            log.info(f"the ping verfication for {inf_ip_add_list[4]} is passed on dut1")
        else:
            self.failed("4 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_Loopback_ip_add):
            log.info(f"the ping verfication for {uut2_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("5 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_Loopback_ip_add):
            log.info(f"the ping verfication for {uut3_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("6 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_Loopback_ip_add):
            log.info(f"the ping verfication for {uut4_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("7 ping verfication failed in dut1")
        log.info(banner("showcommands_check_1_ebgp_bgp"))
        try:
            out1=devices['uut1'].parse("show ip route") 
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out1=devices['uut2'].parse("show ip route") 
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out1=devices['uut3'].parse("show ip route") 
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out1=devices['uut3'].parse("show ip route") 
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut1'].parse(f"show ip route {protocol}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        log.info(banner("show_ip_bgp_check"))
        try:
            devices['uut1'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut2'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut3'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut4'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut1'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {route}")
            
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        log.info(banner("ixia_traffic_L3"))
        log.info(banner('assign_ip_on_interfaces'))
        ixia_configurations.assign_ip_to_ixia_interfaces(self,devices)
        log.info(banner('assign_ixia_configurations'))
        ixia_configurations.ixia_BGP_config(self,devices)
        log.info(banner('clearing_ixia_configurations'))
        ixia_configurations.clear_ixia_configs(self,devices)

    @aetest.cleanup
    def cleanup(self,devices):
        log.info("default the interfaces which are used")
        devices['uut1'].api.default_interface(Variables.dut1_intf1_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf2_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf1_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf2_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf4_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf5_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf1_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf2_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf3_list)
        devices['uut4'].api.default_interface(Variables.dut4_intf1_list)
        log.info("removing loopback interfaces which are configured")
        devices['uut1'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut2'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut3'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut4'].api.remove_virtual_interface(remove_loopback_intf)
        log.info("removing bgp configurationon device")
        devices['uut1'].api.remove_bgp_configuration(bgp_as[0])
        devices['uut2'].api.remove_bgp_configuration(bgp_as[3])
        devices['uut3'].api.remove_bgp_configuration(bgp_as[1])
        devices['uut4'].api.remove_bgp_configuration(bgp_as[2])
class TC_07_Verify_bgp_updates_send_out_using_route_map(aetest.Testcase):

    @aetest.setup
    def setup(self):
        """ test setup """
        log.info('Test setup passed')

    @aetest.test
    def tc_07_Verify_bgp_updates_send_out_using_route_map(self,devices):
        log.info("Clear the logging buffer")
        devices['uut1'].api.clear_logging(device=devices['uut1'])
        devices['uut2'].api.clear_logging(device=devices['uut2'])
        devices['uut3'].api.clear_logging(device=devices['uut3'])
        devices['uut4'].api.clear_logging(device=devices['uut4'])
        log.info(banner("configure_interfaces_shutdown_load_test"))
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf1_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf2_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf1_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf2_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf4_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf5_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf1_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf2_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf3_list)
        devices['uut4'].api.configure_interfaces_unshutdown(Variables.dut4_intf1_list)
        log.info(banner("configure_vtp_mode_EBGP_BGP"))
        devices['uut1'].api.configure_vtp_mode(mode1)
        devices['uut2'].api.configure_vtp_mode(mode1)
        devices['uut3'].api.configure_vtp_mode(mode1)
        devices['uut4'].api.configure_vtp_mode(mode1)
        log.info(banner("ip_routing_EBGP_BGP"))
        devices['uut1'].api.enable_ip_routing()
        devices['uut2'].api.enable_ip_routing()
        devices['uut3'].api.enable_ip_routing()
        devices['uut4'].api.enable_ip_routing()
        log.info(banner("loopback_interface_EBGP_BGP"))
        devices['uut1'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut1_Loopback_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut2_Loopback_ip_add,mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut3_Loopback_ip_add,mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut4_Loopback_ip_add,mask=loop_mask)
        log.info(banner("no_switchport_on_interfacesEBGP_BGP"))
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf1_list[0])
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf2_list[0])
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf3_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf1_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf2_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf5_list[0])
        devices['uut3'].api.configure_interface_no_switchport(Variables.dut3_intf3_list[0])
        devices['uut4'].api.configure_interface_no_switchport(Variables.dut4_intf1_list[0])
        log.info(banner("assign_ip_on_interface_EBGP_BGP"))
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf1_list[0],ip_address=uut1_vlan20_ip_add,mask=loop_mask)
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf3_list[0],ip_address=uut1_vlan30_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(Variables.dut2_intf1_list[0],ip_address=uut2_vlan20_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(Variables.dut2_intf5_list[0],ip_address=uut2_vlan40_ip_add,mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(Variables.dut3_intf3_list[0],ip_address=uut3_vlan30_ip_add,mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(Variables.dut4_intf1_list[0],ip_address=uut4_vlan40_ip_add,mask=loop_mask)
        log.info(banner("configure_bgp_router_id_load_test"))
        devices['uut1'].api.unconfigure_router_bgp_synchronization(bgp_as[0])
        devices['uut2'].api.unconfigure_router_bgp_synchronization(bgp_as[3])
        devices['uut3'].api.unconfigure_router_bgp_synchronization(bgp_as[1])
        devices['uut4'].api.unconfigure_router_bgp_synchronization(bgp_as[2])
        devices['uut1'].api.configure_bgp_log_neighbor_changes(bgp_as[0])
        devices['uut2'].api.configure_bgp_log_neighbor_changes(bgp_as[3])
        devices['uut3'].api.configure_bgp_log_neighbor_changes(bgp_as[1])
        devices['uut4'].api.configure_bgp_log_neighbor_changes(bgp_as[2])
        devices['uut1'].api.unconfigure_bgp_auto_summary(bgp_as[0])
        devices['uut2'].api.unconfigure_bgp_auto_summary(bgp_as[3])
        devices['uut3'].api.unconfigure_bgp_auto_summary(bgp_as[1])
        devices['uut4'].api.unconfigure_bgp_auto_summary(bgp_as[2])
        log.info(banner("configure_bgp_neighbor_multihop"))
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan20_ip_add)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan30_ip_add)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[0], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan20_ip_add)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[2],neighbor_address=uut4_vlan40_ip_add)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[3], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan30_ip_add)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[4], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut4'].api.configure_bgp_neighbor(bgp_as=bgp_as[2],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan40_ip_add)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[6], mask=loop_mask)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        log.info(banner("configure_route_map_on_BGP"))
        devices['uut1'].api.configure_route_map_route_map_to_bgp_neighbor(bgp_as=bgp_as[0],address_family="",vrf="",vrf_address_family="",route_map=route_map)
        devices['uut1'].api.configure_route_map_route_map(route_map=route_map4)
        devices['uut3'].api.configure_route_map_route_map_to_bgp_neighbor(bgp_as=bgp_as[1],address_family="",vrf="",vrf_address_family="",route_map=route_map3)
        devices['uut3'].api.configure_route_map_route_map(route_map=route_map5)
        log.info(banner("verying_ping_check"))
        log.info("Verfiy ping check from dut1")
        time.sleep(60)
        if devices['uut1'].api.verify_ping(uut2_vlan40_ip_add):
            log.info(f"the ping verfication for {uut2_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("1 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_vlan40_ip_add):
            log.info(f"the ping verfication for {uut4_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("2 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_vlan30_ip_add):
            log.info(f"the ping verfication for {uut3_vlan30_ip_add} is passed on dut1")
        else:
            self.failed("3 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_vlan20_ip_add):
            log.info(f"the ping verfication for {uut2_vlan20_ip_add} is passed on dut1")
        else:
            self.failed("4 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_Loopback_ip_add):
            log.info(f"the ping verfication for {uut2_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("5 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_Loopback_ip_add):
            log.info(f"the ping verfication for {uut3_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("6 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_Loopback_ip_add):
            log.info(f"the ping verfication for {uut4_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("7 ping verfication failed in dut1")
        log.info(banner("show_ip_bgp_check"))
        try:
            devices['uut1'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut2'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut3'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut4'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut1'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {route}")
            
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        log.info(banner("ixia_traffic_L3"))
        log.info(banner('assign_ip_on_interfaces'))
        ixia_configurations.assign_ip_to_ixia_interfaces(self,devices)
        log.info(banner('assign_ixia_configurations'))
        ixia_configurations.ixia_BGP_config(self,devices)
        log.info(banner('clearing_ixia_configurations'))
        ixia_configurations.clear_ixia_configs(self,devices)

    @aetest.cleanup
    def cleanup(self,devices):
        log.info("default the interfaces which are used")
        devices['uut1'].api.default_interface(Variables.dut1_intf1_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf2_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf1_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf2_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf4_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf5_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf1_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf2_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf3_list)
        devices['uut4'].api.default_interface(Variables.dut4_intf1_list)
        log.info("removing loopback interfaces which are configured")
        devices['uut1'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut2'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut3'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut4'].api.remove_virtual_interface(remove_loopback_intf)
        log.info("removing bgp configurationon device")
        devices['uut1'].api.remove_bgp_configuration(bgp_as[0])
        devices['uut2'].api.remove_bgp_configuration(bgp_as[3])
        devices['uut3'].api.remove_bgp_configuration(bgp_as[1])
        devices['uut4'].api.remove_bgp_configuration(bgp_as[2])

class TC_08_Verify_bgp_updates_from_inbound_bgp_filter_using_route_maps(aetest.Testcase):


    @aetest.setup
    def setup(self):
        """ test setup """
        log.info('Test setup passed')

    @aetest.test
    def tc_08_Verify_bgp_updates_from_inbound_bgp_filter_using_route_maps(self,devices):
        log.info("Clear the logging buffer")
        devices['uut1'].api.clear_logging(device=devices['uut1'])
        devices['uut2'].api.clear_logging(device=devices['uut2'])
        devices['uut3'].api.clear_logging(device=devices['uut3'])
        devices['uut4'].api.clear_logging(device=devices['uut4'])
        log.info(banner("configure_interfaces_shutdown_load_test"))
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf1_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf2_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf1_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf2_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf4_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf5_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf1_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf2_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf3_list)
        devices['uut4'].api.configure_interfaces_unshutdown(Variables.dut4_intf1_list)
        log.info(banner("configure_vtp_mode_EBGP_BGP"))
        devices['uut1'].api.configure_vtp_mode(mode1)
        devices['uut2'].api.configure_vtp_mode(mode1)
        devices['uut3'].api.configure_vtp_mode(mode1)
        devices['uut4'].api.configure_vtp_mode(mode1)
        log.info(banner("ip_routing_EBGP_BGP"))
        devices['uut1'].api.enable_ip_routing()
        devices['uut2'].api.enable_ip_routing()
        devices['uut3'].api.enable_ip_routing()
        devices['uut4'].api.enable_ip_routing()
        log.info(banner("loopback_interface_EBGP_BGP"))
        devices['uut1'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut1_Loopback_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut2_Loopback_ip_add,mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut3_Loopback_ip_add,mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut4_Loopback_ip_add,mask=loop_mask)
        log.info(banner("no_switchport_on_interfacesEBGP_BGP"))
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf1_list[0])
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf2_list[0])
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf3_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf1_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf2_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf5_list[0])
        devices['uut3'].api.configure_interface_no_switchport(Variables.dut3_intf3_list[0])
        devices['uut4'].api.configure_interface_no_switchport(Variables.dut4_intf1_list[0])
        log.info(banner("assign_ip_on_interface_EBGP_BGP"))
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf1_list[0],ip_address=uut1_vlan20_ip_add,mask=loop_mask)
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf3_list[0],ip_address=uut1_vlan30_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(Variables.dut2_intf1_list[0],ip_address=uut2_vlan20_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(Variables.dut2_intf5_list[0],ip_address=uut2_vlan40_ip_add,mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(Variables.dut3_intf3_list[0],ip_address=uut3_vlan30_ip_add,mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(Variables.dut4_intf1_list[0],ip_address=uut4_vlan40_ip_add,mask=loop_mask)
        log.info(banner("configure_bgp_router_id_load_test"))
        devices['uut1'].api.unconfigure_router_bgp_synchronization(bgp_as[0])
        devices['uut2'].api.unconfigure_router_bgp_synchronization(bgp_as[3])
        devices['uut3'].api.unconfigure_router_bgp_synchronization(bgp_as[1])
        devices['uut4'].api.unconfigure_router_bgp_synchronization(bgp_as[2])
        devices['uut1'].api.configure_bgp_log_neighbor_changes(bgp_as[0])
        devices['uut2'].api.configure_bgp_log_neighbor_changes(bgp_as[3])
        devices['uut3'].api.configure_bgp_log_neighbor_changes(bgp_as[1])
        devices['uut4'].api.configure_bgp_log_neighbor_changes(bgp_as[2])
        devices['uut1'].api.unconfigure_bgp_auto_summary(bgp_as[0])
        devices['uut2'].api.unconfigure_bgp_auto_summary(bgp_as[3])
        devices['uut3'].api.unconfigure_bgp_auto_summary(bgp_as[1])
        devices['uut4'].api.unconfigure_bgp_auto_summary(bgp_as[2])
        log.info(banner("configure_bgp_neighbor_multihop"))
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan20_ip_add)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan30_ip_add)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[0], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan20_ip_add)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[2],neighbor_address=uut4_vlan40_ip_add)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[3], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan30_ip_add)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[4], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut4'].api.configure_bgp_neighbor(bgp_as=bgp_as[2],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan40_ip_add)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[6], mask=loop_mask)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        log.info(banner("configure_route_map_on_BGP"))
        devices['uut1'].api.configure_route_map_route_map_to_bgp_neighbor(bgp_as=bgp_as[0],address_family="",vrf="",vrf_address_family="",route_map=route_map6)
        devices['uut1'].api.configure_route_map_route_map(route_map=route_map7)
        devices['uut1'].api.configure_route_map_route_map_to_bgp_neighbor(bgp_as=bgp_as[0],address_family="",vrf="",vrf_address_family="",route_map=route_map8)
        devices['uut1'].api.configure_route_map_route_map(route_map=route_map9)
        out=devices['uut1'].api.get_show_output_include(command="show running-config", filter=routemap)
        log.info(out)
        out=devices['uut1'].api.get_show_output_include(command="show running-config", filter=routemap1)
        log.info(out)
        log.info(banner("verying_ping_check"))
        log.info("Verfiy ping check from dut1")
        time.sleep(60)
        if devices['uut1'].api.verify_ping(uut2_vlan40_ip_add):
            log.info(f"the ping verfication for {uut2_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("1 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_vlan40_ip_add):
            log.info(f"the ping verfication for {uut4_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("2 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_vlan30_ip_add):
            log.info(f"the ping verfication for {uut3_vlan30_ip_add} is passed on dut1")
        else:
            self.failed("3 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_vlan20_ip_add):
            log.info(f"the ping verfication for {uut2_vlan20_ip_add} is passed on dut1")
        else:
            self.failed("4 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_Loopback_ip_add):
            log.info(f"the ping verfication for {uut2_Loopback_ip_add} is passed on dut1")
        else:
           self.failed("5 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_Loopback_ip_add):
            log.info(f"the ping verfication for {uut3_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("6 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_Loopback_ip_add):
            log.info(f"the ping verfication for {uut4_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("7 ping verfication failed in dut1")
        log.info(banner("show_ip_bgp_check"))
        try:
            devices['uut1'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut2'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut3'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut4'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut1'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {route}")
            
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        log.info(banner("ixia_ipv6_traffic"))
        log.info(banner('assign_ip_on_interfaces'))
        ixia_ipv6_traffic.assign_ip_to_ixia_interfaces(self,devices)
        log.info(banner('assign_ixia_configurations'))
        ixia_ipv6_traffic.ixia_ipv6_config(self, devices)
        log.info(banner('clearing_ixia_configurations'))
        ixia_ipv6_traffic.clearing_configs_on_interface(self, devices)

    @aetest.cleanup
    def cleanup(self,devices):
        log.info("default the interfaces which are used")
        devices['uut1'].api.default_interface(Variables.dut1_intf1_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf2_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf1_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf2_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf4_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf5_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf1_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf2_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf3_list)
        devices['uut4'].api.default_interface(Variables.dut4_intf1_list)
        log.info("removing loopback interfaces which are configured")
        devices['uut1'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut2'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut3'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut4'].api.remove_virtual_interface(remove_loopback_intf)
        log.info("removing bgp configurationon device")
        devices['uut1'].api.remove_bgp_configuration(bgp_as[0])
        devices['uut2'].api.remove_bgp_configuration(bgp_as[3])
        devices['uut3'].api.remove_bgp_configuration(bgp_as[1])
        devices['uut4'].api.remove_bgp_configuration(bgp_as[2])
        

class TC_10_To_verify_L3_orwarding_behavior_routes_learnt_from_adjacent_router(aetest.Testcase):


    @aetest.setup
    def setup(self):
        """ test setup """
        log.info('Test setup passed')

    @aetest.test
    def tc_10_To_verify_L3_orwarding_behavior_routes_learnt_from_adjacent_router(self,devices):
        log.info("Clear the logging buffer")
        devices['uut1'].api.clear_logging(device=devices['uut1'])
        devices['uut2'].api.clear_logging(device=devices['uut2'])
        devices['uut3'].api.clear_logging(device=devices['uut3'])
        devices['uut4'].api.clear_logging(device=devices['uut4'])
        log.info(banner("configure_interfaces_shutdown_load_test"))
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf1_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf2_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf1_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf2_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf4_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf5_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf1_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf2_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf3_list)
        devices['uut4'].api.configure_interfaces_unshutdown(Variables.dut4_intf1_list)
        log.info(banner("configure_vtp_mode_EBGP_BGP"))
        devices['uut1'].api.configure_vtp_mode(mode1)
        devices['uut2'].api.configure_vtp_mode(mode1)
        devices['uut3'].api.configure_vtp_mode(mode1)
        devices['uut4'].api.configure_vtp_mode(mode1)
        log.info(banner("ip_routing_EBGP_BGP"))
        devices['uut1'].api.enable_ip_routing()
        devices['uut2'].api.enable_ip_routing()
        devices['uut3'].api.enable_ip_routing()
        devices['uut4'].api.enable_ip_routing()
        log.info(banner("loopback_interface_EBGP_BGP"))
        devices['uut1'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut1_Loopback_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut2_Loopback_ip_add,mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut3_Loopback_ip_add,mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut4_Loopback_ip_add,mask=loop_mask)
        log.info(banner("no_switchport_on_interfacesEBGP_BGP"))
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf1_list[0])
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf2_list[0])
        devices['uut1'].api.configure_interface_no_switchport(Variables.dut1_intf3_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf1_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf2_list[0])
        devices['uut2'].api.configure_interface_no_switchport(Variables.dut2_intf5_list[0])
        devices['uut3'].api.configure_interface_no_switchport(Variables.dut3_intf3_list[0])
        devices['uut4'].api.configure_interface_no_switchport(Variables.dut4_intf1_list[0])
        log.info(banner("assign_ip_on_interface_EBGP_BGP"))
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf1_list[0],ip_address=uut1_vlan20_ip_add,mask=loop_mask)
        devices['uut1'].api.config_ip_on_interface(Variables.dut1_intf3_list[0],ip_address=uut1_vlan30_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(Variables.dut2_intf1_list[0],ip_address=uut2_vlan20_ip_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(Variables.dut2_intf5_list[0],ip_address=uut2_vlan40_ip_add,mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(Variables.dut3_intf3_list[0],ip_address=uut3_vlan30_ip_add,mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(Variables.dut4_intf1_list[0],ip_address=uut4_vlan40_ip_add,mask=loop_mask)
        log.info(banner("configure_bgp_router_id_load_test"))
        devices['uut1'].api.unconfigure_router_bgp_synchronization(bgp_as[0])
        devices['uut2'].api.unconfigure_router_bgp_synchronization(bgp_as[3])
        devices['uut3'].api.unconfigure_router_bgp_synchronization(bgp_as[1])
        devices['uut4'].api.unconfigure_router_bgp_synchronization(bgp_as[2])
        devices['uut1'].api.configure_bgp_log_neighbor_changes(bgp_as[0])
        devices['uut2'].api.configure_bgp_log_neighbor_changes(bgp_as[3])
        devices['uut3'].api.configure_bgp_log_neighbor_changes(bgp_as[1])
        devices['uut4'].api.configure_bgp_log_neighbor_changes(bgp_as[2])
        devices['uut1'].api.unconfigure_bgp_auto_summary(bgp_as[0])
        devices['uut2'].api.unconfigure_bgp_auto_summary(bgp_as[3])
        devices['uut3'].api.unconfigure_bgp_auto_summary(bgp_as[1])
        devices['uut4'].api.unconfigure_bgp_auto_summary(bgp_as[2])
        log.info(banner("configure_bgp_neighbor_multihop"))
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[0],neighbor_address=uut2_vlan20_ip_add)       
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan20_ip_add)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan30_ip_add)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[0], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan20_ip_add)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[2],neighbor_address=uut4_vlan40_ip_add)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[3], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan30_ip_add)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[4], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut4'].api.configure_bgp_neighbor(bgp_as=bgp_as[2],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan40_ip_add)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[6], mask=loop_mask)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        log.info(banner("verying_ping_check"))
        time.sleep(40)
        if devices['uut1'].api.verify_ping(uut2_vlan40_ip_add):
            log.info(f"the ping verfication for {uut2_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("1 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_vlan40_ip_add):
            log.info(f"the ping verfication for {uut4_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("2 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_vlan30_ip_add):
            log.info(f"the ping verfication for {uut3_vlan30_ip_add} is passed on dut1")
        else:
            self.failed("3 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_vlan20_ip_add):
            log.info(f"the ping verfication for {uut2_vlan20_ip_add} is passed on dut1")
        else:
            self.failed("4 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_Loopback_ip_add):
            log.info(f"the ping verfication for {uut2_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("5 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_Loopback_ip_add):
            log.info(f"the ping verfication for {uut3_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("6 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_Loopback_ip_add):
            log.info(f"the ping verfication for {uut4_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("7 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut1_Loopback_ip_add):
            log.info(f"the ping verfication for {uut1_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("8 ping verfication failed in dut1")
        log.info(banner("verify_show_command1"))
        out=devices['uut1'].api.get_show_output_include(command="show version", filter="System image file")
        log.info(banner("show_ip_bgp_check_1"))
        try:
            devices['uut1'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut2'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut3'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut4'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut1'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {route}")
            
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        log.info(banner(" configure_no_boot_manual1"))
        if reload:
            log.info(banner("Do reload on both uut's"))
            devices['uut1'].api.configure_no_boot_manual()
            log.info(banner("Reload on uut1"))
            log.info(("saving the configuration"))
            devices.uut1.api.execute_write_memory(timeout=600)
            log.info("reloading the stack")
            devices.uut1.reload(timeout=2400,prompt_recovery=True)
        log.info(banner("Reconfigure_bgp_neighbor_multihop1"))
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[0],neighbor_address=uut2_vlan20_ip_add)       
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan20_ip_add)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan30_ip_add)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[0], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan20_ip_add)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[2],neighbor_address=uut4_vlan40_ip_add)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[3], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan30_ip_add)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[4], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut4'].api.configure_bgp_neighbor(bgp_as=bgp_as[2],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan40_ip_add)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[6], mask=loop_mask)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        time.sleep(30)
        devices['uut1'].api.execute_write_memory()
        devices['uut2'].api.execute_write_memory()
        devices['uut3'].api.execute_write_memory()
        devices['uut4'].api.execute_write_memory()
        log.info(banner("verify_show_command_after_reconfig"))
        devices['uut1'].api.get_show_output_section(command="show running-config", filter="router bgp")
        devices['uut2'].api.get_show_output_section(command="show running-config", filter="router bgp")
        devices['uut3'].api.get_show_output_section(command="show running-config", filter="router bgp")
        devices['uut4'].api.get_show_output_section(command="show running-config", filter="router bgp")
        log.info(banner("verying_ping_check_after_reload1"))
        time.sleep(40)
        if devices['uut1'].api.verify_ping(uut2_vlan40_ip_add):
            log.info(f"the ping verfication for {uut2_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("1 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_vlan40_ip_add):
            log.info(f"the ping verfication for {uut4_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("2 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_vlan30_ip_add):
            log.info(f"the ping verfication for {uut3_vlan30_ip_add} is passed on dut1")
        else:
            self.failed("3 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_vlan20_ip_add):
            log.info(f"the ping verfication for {uut2_vlan20_ip_add} is passed on dut1")
        else:
            self.failed("4 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_Loopback_ip_add):
            log.info(f"the ping verfication for {uut2_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("5 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_Loopback_ip_add):
            log.info(f"the ping verfication for {uut3_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("6 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_Loopback_ip_add):
            log.info(f"the ping verfication for {uut4_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("7 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut1_Loopback_ip_add):
            log.info(f"the ping verfication for {uut1_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("8 ping verfication failed in dut1") 
        log.info(banner("Reconfigure_bgp_neighbor_multihop2"))
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[0],neighbor_address=uut2_vlan20_ip_add)       
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan20_ip_add)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan30_ip_add)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[0], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan20_ip_add)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[2],neighbor_address=uut4_vlan40_ip_add)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[3], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan30_ip_add)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[4], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut4'].api.configure_bgp_neighbor(bgp_as=bgp_as[2],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan40_ip_add)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[6], mask=loop_mask)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        log.info(banner("verying_ping_check_after_again_reconfigure"))
        time.sleep(40)
        if devices['uut1'].api.verify_ping(uut2_vlan40_ip_add):
            log.info(f"the ping verfication for {uut2_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("1 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_vlan40_ip_add):
            log.info(f"the ping verfication for {uut4_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("2 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_vlan30_ip_add):
            log.info(f"the ping verfication for {uut3_vlan30_ip_add} is passed on dut1")
        else:
            self.failed("3 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_vlan20_ip_add):
            log.info(f"the ping verfication for {uut2_vlan20_ip_add} is passed on dut1")
        else:
            self.failed("4 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_Loopback_ip_add):
            log.info(f"the ping verfication for {uut2_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("5 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_Loopback_ip_add):
            log.info(f"the ping verfication for {uut3_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("6 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_Loopback_ip_add):
            log.info(f"the ping verfication for {uut4_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("7 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut1_Loopback_ip_add):
            log.info(f"the ping verfication for {uut1_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("8 ping verfication failed in dut1") 
        log.info(banner("show_ip_bgp_check_2"))
        try:
            devices['uut1'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut2'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut3'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut4'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut1'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {route}")
            
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        log.info(banner("verify_show_command2"))
        out=devices['uut1'].api.get_show_output_include(command="show version", filter="System image file")
        log.info(banner("configure_no_boot_manual2"))
        if reload:
            log.info(banner("Do reload on both uut's"))
            devices['uut1'].api.configure_no_boot_manual()
            log.info(banner("Reload on uut1"))
            log.info(("saving the configuration"))
            devices.uut1.api.execute_write_memory(timeout=600)
            log.info("reloading the stack")
            devices.uut1.reload(timeout=2400,prompt_recovery=True)
        log.info(banner("Reconfigure_bgp_neighbor_multihop3"))
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[0],neighbor_address=uut2_vlan20_ip_add)       
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan20_ip_add)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan30_ip_add)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[0], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan20_ip_add)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[2],neighbor_address=uut4_vlan40_ip_add)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[3], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan30_ip_add)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[4], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut4'].api.configure_bgp_neighbor(bgp_as=bgp_as[2],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan40_ip_add)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[6], mask=loop_mask)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        time.sleep(30)
        devices['uut1'].api.execute_write_memory()
        devices['uut2'].api.execute_write_memory()
        devices['uut3'].api.execute_write_memory()
        devices['uut4'].api.execute_write_memory()
        log.info(banner("verify_show_command_after_reconfig3"))
        devices['uut1'].api.get_show_output_section(command="show running-config", filter="router bgp")
        devices['uut2'].api.get_show_output_section(command="show running-config", filter="router bgp")
        devices['uut3'].api.get_show_output_section(command="show running-config", filter="router bgp")
        devices['uut4'].api.get_show_output_section(command="show running-config", filter="router bgp")
        log.info(banner("verying_ping_check_after_Again_reconfigure_3"))
        time.sleep(60)
        if devices['uut1'].api.verify_ping(uut2_vlan40_ip_add):
            log.info(f"the ping verfication for {uut2_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("1 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_vlan40_ip_add):
            log.info(f"the ping verfication for {uut4_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("2 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_vlan30_ip_add):
            log.info(f"the ping verfication for {uut3_vlan30_ip_add} is passed on dut1")
        else:
            self.failed("3 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_vlan20_ip_add):
            log.info(f"the ping verfication for {uut2_vlan20_ip_add} is passed on dut1")
        else:
            self.failed("4 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_Loopback_ip_add):
            log.info(f"the ping verfication for {uut2_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("5 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_Loopback_ip_add):
            log.info(f"the ping verfication for {uut3_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("6 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_Loopback_ip_add):
            log.info(f"the ping verfication for {uut4_Loopback_ip_add} is passed on dut1")
        else:
           self.failed("7 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut1_Loopback_ip_add):
            log.info(f"the ping verfication for {uut1_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("8 ping verfication failed in dut1")
        log.info(banner("configure_no_boot_manual_3"))
        if reload:
            log.info(banner("Do reload on both uut's"))
            devices['uut1'].api.configure_no_boot_manual()
            log.info(banner("Reload on uut1"))
            log.info(("saving the configuration"))
            devices.uut1.api.execute_write_memory(timeout=600)
            log.info("reloading the stack")
            devices.uut1.reload(timeout=2400,prompt_recovery=True)
        log.info(banner("clear_logging"))
        log.info("Clear the logging buffer")
        devices['uut1'].api.clear_logging(device=devices['uut1'])
        devices['uut2'].api.clear_logging(device=devices['uut2'])
        devices['uut3'].api.clear_logging(device=devices['uut3'])
        devices['uut4'].api.clear_logging(device=devices['uut4'])
        log.info(banner("show_ip_bgp_check_3"))
        try:
            devices['uut1'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut2'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut3'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut4'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut1'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {route}")
            
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        log.info(banner("Reconfigure_bgp_neighbor_multihop_4"))
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[0],neighbor_address=uut2_vlan20_ip_add)       
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan20_ip_add)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan30_ip_add)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[0], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan20_ip_add)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[2],neighbor_address=uut4_vlan40_ip_add)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[3], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan30_ip_add)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[4], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut4'].api.configure_bgp_neighbor(bgp_as=bgp_as[2],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan40_ip_add)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[6], mask=loop_mask)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        time.sleep(30)
        devices['uut1'].api.execute_write_memory()
        devices['uut2'].api.execute_write_memory()
        devices['uut3'].api.execute_write_memory()
        devices['uut4'].api.execute_write_memory()
        log.info(banner("verify_show_command_after_reconfig_4"))
        devices['uut1'].api.get_show_output_section(command="show running-config", filter="router bgp")
        devices['uut2'].api.get_show_output_section(command="show running-config", filter="router bgp")
        devices['uut3'].api.get_show_output_section(command="show running-config", filter="router bgp")
        devices['uut4'].api.get_show_output_section(command="show running-config", filter="router bgp")  
        log.info(banner("verying_ping_check_4"))
        time.sleep(40)
        if devices['uut1'].api.verify_ping(uut2_vlan40_ip_add):
            log.info(f"the ping verfication for {uut2_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("1 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_vlan40_ip_add):
            log.info(f"the ping verfication for {uut4_vlan40_ip_add} is passed on dut1")
        else:
            self.failed("2 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_vlan30_ip_add):
            log.info(f"the ping verfication for {uut3_vlan30_ip_add} is passed on dut1")
        else:
            self.failed("3 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_vlan20_ip_add):
            log.info(f"the ping verfication for {uut2_vlan20_ip_add} is passed on dut1")
        else:
            self.failed("4 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut2_Loopback_ip_add):
            log.info(f"the ping verfication for {uut2_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("5 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut3_Loopback_ip_add):
            log.info(f"the ping verfication for {uut3_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("6 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut4_Loopback_ip_add):
            log.info(f"the ping verfication for {uut4_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("7 ping verfication failed in dut1")
        if devices['uut1'].api.verify_ping(uut1_Loopback_ip_add):
            log.info(f"the ping verfication for {uut1_Loopback_ip_add} is passed on dut1")
        else:
            self.failed("8 ping verfication failed in dut1")
        log.info(banner("show_ip_bgp_check_4"))
        try:
            devices['uut1'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut2'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut3'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut4'].parse(f"show ip bgp")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut1'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut1'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut2'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {route}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut3'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {route}")
            
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[1]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[3]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[2]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[4]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[5]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        try:
            out = devices['uut4'].parse(f"show ip bgp {network_ip_add[6]}")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass 
        log.info(banner("ixia_traffic_L3"))
        log.info(banner('assign_ip_on_interfaces'))
        ixia_configurations.assign_ip_to_ixia_interfaces(self,devices)
        log.info(banner('assign_ixia_configurations'))
        ixia_configurations.ixia_BGP_config(self,devices)
        log.info(banner('clearing_ixia_configurations'))
        ixia_configurations.clear_ixia_configs(self,devices)

    @aetest.cleanup
    def cleanup(self,devices):
        log.info("default the interfaces which are used")
        devices['uut1'].api.default_interface(Variables.dut1_intf1_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf2_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf1_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf2_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf4_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf5_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf1_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf2_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf3_list)
        devices['uut4'].api.default_interface(Variables.dut4_intf1_list)
        log.info("removing loopback interfaces which are configured")
        devices['uut1'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut2'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut3'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut4'].api.remove_virtual_interface(remove_loopback_intf)
        log.info("removing bgp configurationon device")
        devices['uut1'].api.remove_bgp_configuration(bgp_as[0])
        devices['uut2'].api.remove_bgp_configuration(bgp_as[3])
        devices['uut3'].api.remove_bgp_configuration(bgp_as[1])
        devices['uut4'].api.remove_bgp_configuration(bgp_as[2])

class TC_17_To_verify_EBGP_load_balancing_with_maximum_paths(aetest.Testcase):

    @aetest.setup
    def setup(self):
        """ test setup """
        log.info('Test setup passed')

    @aetest.test
    def tc_17_To_verify_EBGP_load_balancing_with_maximum_paths(self,devices):
        log.info("Clear the logging buffer")
        devices['uut1'].api.clear_logging(device=devices['uut1'])
        devices['uut2'].api.clear_logging(device=devices['uut2'])
        devices['uut3'].api.clear_logging(device=devices['uut3'])
        devices['uut4'].api.clear_logging(device=devices['uut4'])
        log.info(banner("configure_interfaces_shutdown_load_test"))
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf1_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf2_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf3_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf4_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf5_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf6_list)
        devices['uut1'].api.configure_interfaces_unshutdown(Variables.dut1_intf7_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf1_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf2_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf3_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf4_list)
        devices['uut2'].api.configure_interfaces_unshutdown(Variables.dut2_intf5_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf1_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf2_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf3_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf4_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf5_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf6_list)
        devices['uut3'].api.configure_interfaces_unshutdown(Variables.dut3_intf7_list)
        devices['uut4'].api.configure_interfaces_unshutdown(Variables.dut4_intf1_list)
        log.info(banner("configure_vtp_mode_EBGP_BGP"))
        devices['uut1'].api.configure_vtp_mode(mode1)
        devices['uut2'].api.configure_vtp_mode(mode1)
        devices['uut3'].api.configure_vtp_mode(mode1)
        devices['uut4'].api.configure_vtp_mode(mode1)
        log.info(banner("ip_routing_EBGP_BGP"))
        devices['uut1'].api.enable_ip_routing()
        devices['uut2'].api.enable_ip_routing()
        devices['uut3'].api.enable_ip_routing()
        devices['uut4'].api.enable_ip_routing()
        log.info(banner("loopback_interface_EBGP_BGP"))
        devices['uut1'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut1_loop_add,mask=loop_mask)
        devices['uut2'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut2_loop_add,mask=loop_mask)
        devices['uut3'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut3_loop_add,mask=loop_mask)
        devices['uut4'].api.config_ip_on_interface(intf_Loopback_num,ip_address=uut4_loop_add,mask=loop_mask)
        log.info(banner("assign_ip_on_vlan"))
        devices['uut1'].api.config_vlan(uut_vlan_id[0])
        devices['uut1'].api.config_ip_on_vlan(uut_vlan_id[0],ipv4_address=uut1_vlan20_ip_add,subnetmask=loop_mask)
        devices['uut1'].api.configure_interfaces_unshutdown(uut_vlan_id1)
        devices['uut1'].api.config_vlan(uut_vlan_id[1])
        devices['uut1'].api.config_ip_on_vlan(uut_vlan_id[1],ipv4_address=uut1_vlan30_ip_add,subnetmask=loop_mask)
        devices['uut1'].api.configure_interfaces_unshutdown(uut_vlan_id2)
        devices['uut1'].api.config_vlan(uut_vlan_id0[3])
        devices['uut1'].api.config_ip_on_vlan(uut_vlan_id0[3],ipv4_address=uut1_vlan31_add,subnetmask=loop_mask)
        devices['uut1'].api.configure_interfaces_unshutdown(uut1_vlan_31_id)
        devices['uut1'].api.config_vlan(uut_vlan_id0[4])
        devices['uut1'].api.config_ip_on_vlan(uut_vlan_id0[4],ipv4_address=uut1_vlan32_add,subnetmask=loop_mask)
        devices['uut1'].api.configure_interfaces_unshutdown(uut1_vlan_32_id)
        devices['uut1'].api.config_vlan(uut_vlan_id0[5])
        devices['uut1'].api.config_ip_on_vlan(uut_vlan_id0[5],ipv4_address=uut1_vlan33_add,subnetmask=loop_mask)
        devices['uut1'].api.configure_interfaces_unshutdown(uut1_vlan_33_id)
        devices['uut2'].api.config_vlan(uut_vlan_id[0])
        devices['uut2'].api.config_ip_on_vlan(uut_vlan_id[0],ipv4_address=uut2_vlan20_ip_add,subnetmask=loop_mask)
        devices['uut2'].api.configure_interfaces_unshutdown(uut_vlan_id1)
        devices['uut3'].api.config_vlan(uut_vlan_id[1])
        devices['uut3'].api.config_ip_on_vlan(uut_vlan_id[1],ipv4_address=uut3_vlan30_ip_add,subnetmask=loop_mask)
        devices['uut3'].api.configure_interfaces_unshutdown(uut_vlan_id2)
        devices['uut3'].api.config_vlan(uut_vlan_id0[3])
        devices['uut3'].api.config_ip_on_vlan(uut_vlan_id0[3],ipv4_address=uut3_vlan31_add,subnetmask=loop_mask)
        devices['uut3'].api.configure_interfaces_unshutdown(uut1_vlan_31_id)
        devices['uut3'].api.config_vlan(uut_vlan_id0[4])
        devices['uut3'].api.config_ip_on_vlan(uut_vlan_id0[4],ipv4_address=uut3_vlan32_add,subnetmask=loop_mask)
        devices['uut3'].api.configure_interfaces_unshutdown(uut1_vlan_32_id)
        devices['uut3'].api.config_vlan(uut_vlan_id0[5])
        devices['uut3'].api.config_ip_on_vlan(uut_vlan_id0[5],ipv4_address=uut3_vlan33_add,subnetmask=loop_mask)
        devices['uut3'].api.configure_interfaces_unshutdown(uut1_vlan_33_id)
        devices['uut3'].api.config_vlan(uut_vlan_id[2])
        devices['uut3'].api.config_ip_on_vlan(uut_vlan_id[2],ipv4_address=uut4_vlan40_ip_add,subnetmask=loop_mask)
        devices['uut3'].api.configure_interfaces_unshutdown(uut_vlan_id3)
        devices['uut4'].api.config_vlan(uut_vlan_id[2])
        devices['uut4'].api.config_ip_on_vlan(uut_vlan_id[2],ipv4_address=uut2_vlan40_ip_add,subnetmask=loop_mask)
        devices['uut4'].api.configure_interfaces_unshutdown(uut_vlan_id3)
        log.info(banner("switchport_mode_access_on_intf"))
        devices['uut1'].api.configure_interface_switchport_mode(Variables.dut1_intf1_list[0],mode=mode11)
        devices['uut1'].api.configure_interface_switchport_access_vlan(Variables.dut1_intf1_list[0],uut_vlan_id[0])
        devices['uut1'].api.configure_interface_switchport_mode(Variables.dut1_intf2_list[0],mode=mode11)
        devices['uut1'].api.configure_interface_switchport_access_vlan(Variables.dut1_intf2_list[0],uut_vlan_id[1])
        devices['uut1'].api.configure_interface_switchport_mode(Variables.dut1_intf3_list[0],mode=mode11)
        devices['uut1'].api.configure_interface_switchport_access_vlan(Variables.dut1_intf3_list[0],uut_vlan_id0[3])
        devices['uut1'].api.configure_interface_switchport_mode(Variables.dut1_intf6_list[0],mode=mode11)
        devices['uut1'].api.configure_interface_switchport_access_vlan(Variables.dut1_intf6_list[0],uut_vlan_id0[4])
        devices['uut1'].api.configure_interface_switchport_mode(Variables.dut1_intf7_list[0],mode=mode11)
        devices['uut1'].api.configure_interface_switchport_access_vlan(Variables.dut1_intf7_list[0],uut_vlan_id0[5])
        devices['uut2'].api.configure_interface_switchport_mode(Variables.dut2_intf1_list[0],mode=mode11)
        devices['uut2'].api.configure_interface_switchport_access_vlan(Variables.dut2_intf1_list[0],uut_vlan_id[0])
        devices['uut3'].api.configure_interface_switchport_mode(Variables.dut3_intf1_list[0],mode=mode11)
        devices['uut3'].api.configure_interface_switchport_access_vlan(Variables.dut3_intf1_list[0],uut_vlan_id[1])
        devices['uut3'].api.configure_interface_switchport_mode(Variables.dut3_intf2_list[0],mode=mode11)
        devices['uut3'].api.configure_interface_switchport_access_vlan(Variables.dut3_intf2_list[0],uut_vlan_id0[3])
        devices['uut3'].api.configure_interface_switchport_mode(Variables.dut3_intf3_list[0],mode=mode11)
        devices['uut3'].api.configure_interface_switchport_access_vlan(Variables.dut3_intf3_list[0],uut_vlan_id0[4])
        devices['uut3'].api.configure_interface_switchport_mode(Variables.dut3_intf6_list[0],mode=mode11)
        devices['uut3'].api.configure_interface_switchport_access_vlan(Variables.dut3_intf6_list[0],uut_vlan_id0[5])
        devices['uut3'].api.configure_interface_switchport_mode(Variables.dut3_intf7_list[0],mode=mode11)
        devices['uut3'].api.configure_interface_switchport_access_vlan(Variables.dut3_intf7_list[0],uut_vlan_id[2])
        devices['uut4'].api.configure_interface_switchport_mode(Variables.dut4_intf1_list[0],mode=mode11)
        devices['uut4'].api.configure_interface_switchport_access_vlan(Variables.dut4_intf1_list[0],uut_vlan_id[2])
        log.info(banner("configure_bgp_router_id_EBGP"))
        devices['uut1'].api.unconfigure_router_bgp_synchronization(bgp_as[0])
        devices['uut2'].api.unconfigure_router_bgp_synchronization(bgp_as[3])
        devices['uut3'].api.unconfigure_router_bgp_synchronization(bgp_as[1])
        devices['uut4'].api.unconfigure_router_bgp_synchronization(bgp_as[2])
        devices['uut1'].api.configure_bgp_log_neighbor_changes(bgp_as[0])
        devices['uut2'].api.configure_bgp_log_neighbor_changes(bgp_as[3])
        devices['uut3'].api.configure_bgp_log_neighbor_changes(bgp_as[1])
        devices['uut4'].api.configure_bgp_log_neighbor_changes(bgp_as[2])
        devices['uut1'].api.unconfigure_bgp_auto_summary(bgp_as[0])
        devices['uut2'].api.unconfigure_bgp_auto_summary(bgp_as[3])
        devices['uut3'].api.unconfigure_bgp_auto_summary(bgp_as[1])
        devices['uut4'].api.unconfigure_bgp_auto_summary(bgp_as[2])
        log.info(banner("configuring_bgp_networks"))
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=ipadd1[0], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=ipadd1[1], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=ipadd1[2], mask=loop_mask)
        devices['uut1'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[0], address_family=address_family, ip_address=ipadd1[3], mask=loop_mask)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[3],neighbor_address=uut2_vlan20_ip_add)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan30_ip_add)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan31_add)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan32_add)
        devices['uut1'].api.configure_bgp_neighbor(bgp_as=bgp_as[0],neighbor_as=bgp_as[1],neighbor_address=uut3_vlan33_add)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=ipadd1[4], mask=loop_mask)
        devices['uut2'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[3], address_family=address_family, ip_address=network_ip_add[1], mask=loop_mask)
        devices['uut2'].api.configure_bgp_neighbor(bgp_as=bgp_as[3],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan20_ip_add)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=ipadd1[5], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[2], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=ipadd1[1], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=ipadd1[2], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=ipadd1[3], mask=loop_mask)
        devices['uut3'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[1], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan30_ip_add)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan31_add)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan32_add)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[0],neighbor_address=uut1_vlan33_add)
        devices['uut3'].api.configure_bgp_neighbor(bgp_as=bgp_as[1],neighbor_as=bgp_as[2],neighbor_address=uut2_vlan40_ip_add)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=ipadd1[6], mask=loop_mask)
        devices['uut4'].api.configure_bgp_address_advertisement(bgp_as=bgp_as[2], address_family=address_family, ip_address=network_ip_add[5], mask=loop_mask)
        devices['uut4'].api.configure_bgp_neighbor(bgp_as=bgp_as[2],neighbor_as=bgp_as[1],neighbor_address=ipadd1[7])
        log.info(banner("setting_maximum_paths"))
        devices['uut1'].api.configure_router_bgp_maximum_paths(system=system,paths=paths)
        try:
            devices['uut1'].parse(f"show ip route")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut2'].parse(f"show ip route")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut3'].parse(f"show ip route")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut4'].parse(f"show ip route")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        log.info(banner("unsetting_maximum_paths"))
        devices['uut1'].api.unconfigure_router_bgp_maximum_paths(system=system,paths=paths)
        try:
            devices['uut1'].parse(f"show ip route")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut2'].parse(f"show ip route")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut3'].parse(f"show ip route")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        try:
            devices['uut4'].parse(f"show ip route")
        except Exception as error:
            if 'Parser Output is empty' in str(error):
                pass
        log.info(banner("ixia_ipv6_traffic"))
        log.info(banner('assign_ip_on_interfaces'))
        ixia_ipv6_traffic.assign_ip_to_ixia_interfaces(self,devices)
        log.info(banner('assign_ixia_configurations'))
        ixia_ipv6_traffic.ixia_ipv6_config(self, devices)
        log.info(banner('clearing_ixia_configurations'))
        ixia_ipv6_traffic.clearing_configs_on_interface(self, devices)

    @aetest.cleanup
    def cleanup(self,devices):
        devices['uut1'].api.default_interface(Variables.dut1_intf1_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf2_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf3_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf4_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf5_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf6_list)
        devices['uut1'].api.default_interface(Variables.dut1_intf7_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf1_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf2_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf3_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf4_list)
        devices['uut2'].api.default_interface(Variables.dut2_intf5_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf1_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf2_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf3_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf4_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf5_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf6_list)
        devices['uut3'].api.default_interface(Variables.dut3_intf7_list)
        devices['uut4'].api.default_interface(Variables.dut4_intf1_list)
        log.info("unconfiguring loopback")
        devices['uut1'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut2'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut3'].api.remove_virtual_interface(remove_loopback_intf)
        devices['uut4'].api.remove_virtual_interface(remove_loopback_intf)
        log.info("removing vlan")
        devices['uut1'].api.remove_virtual_interface(uut_vlan_id1)
        devices['uut1'].api.remove_virtual_interface(uut_vlan_id2)
        devices['uut1'].api.remove_virtual_interface(uut1_vlan_31_id)
        devices['uut1'].api.remove_virtual_interface(uut1_vlan_32_id)
        devices['uut1'].api.remove_virtual_interface(uut1_vlan_33_id)
        devices['uut2'].api.remove_virtual_interface(uut_vlan_id1)
        devices['uut3'].api.remove_virtual_interface(uut_vlan_id2)
        devices['uut3'].api.remove_virtual_interface(uut1_vlan_31_id)
        devices['uut3'].api.remove_virtual_interface(uut1_vlan_32_id)
        devices['uut3'].api.remove_virtual_interface(uut1_vlan_33_id)
        devices['uut3'].api.remove_virtual_interface(uut_vlan_id3)
        devices['uut4'].api.remove_virtual_interface(uut_vlan_id3)
        log.info("removing bgp configurationon device")
        devices['uut1'].api.remove_bgp_configuration(bgp_as[0])
        devices['uut2'].api.remove_bgp_configuration(bgp_as[3])
        devices['uut3'].api.remove_bgp_configuration(bgp_as[1])
        devices['uut4'].api.remove_bgp_configuration(bgp_as[2])

class CommonCleanup(aetest.CommonCleanup):
    '''
    Step 1: Disconnect dut 
    '''
    @aetest.subsection
    def disconnect_from_devices(self, devices):
        log.info(banner("Disconnect all the devices"))
        """ Disconnect all the devices """
        for device in devices.keys():
            # Disconnecting  devices
            log.info("Disconnecting Device:%s", device)
            try:
                devices[device].disconnect()
            except Exception as e:
                log.info(f'Disconnection to {device} Unsuccessful')
                log.info(f'Exception- {str(type(e))}, {str(e)}')
                self.failed(goto=['exit'])
