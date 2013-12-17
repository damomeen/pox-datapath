from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr

log = core.getLogger()


def __addFlowmod1 (event):
  msg = of.ofp_flow_mod()
  msg.actions.append(of.ofp_action_output(port = 1))
  try:
    msg.buffer_id = event.ofp.buffer_id
  except: pass
  event.connection.send(msg)
  log.info("Redirecting all traffic to port 1 %s", dpidToStr(event.dpid))

def __addFlowmod2 (event):
  msg = of.ofp_flow_mod()
  msg.match.dl_dst = EthAddr("35:35:35:35:35:35")
  msg.match.dl_src = EthAddr("45:45:45:45:45:45")
  msg.match.dl_vlan = 1234
  msg.match.dl_vlan_pcp = 1
  msg.match.dl_type = 0x0806
  msg.actions.append(of.ofp_action_output(port = 1))
  try:
    msg.buffer_id = event.ofp.buffer_id
  except: pass
  event.connection.send(msg)
  log.info("Redirecting all traffic to port 1 %s", dpidToStr(event.dpid))

  
def __redirectPacket (event):
  msg = of.ofp_packet_out()
  msg.data = event.ofp
  # Add an action to send to the specified port
  action = of.ofp_action_output(port = 1)
  msg.actions.append(action)
  # Send message to switch
  event.connection.send(msg)
  log.info("Packet redirected to port 1")

def _handle_ConnectionUp (event):
  msg = of.ofp_stats_request(body=of.ofp_port_stats_request())
  #event.connection.send(msg)
  #log.info("Port stats request sent")
  __addFlowmod2(event)


def _handle_PacketIn (event):
  log.info("Packet in %s %s", str(event), str(event.ofp))
  __redirectPacket(event)

def _handle_PortStats (event):
  log.info("Port stats received")
  for port in event.ofp[0].body:
    log.info("\n%s\n", port.show())

def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
  #core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
  #core.openflow.addListenerByName("PortStatsReceived",  _handle_PortStats)
  log.info("Testing controller running.")
