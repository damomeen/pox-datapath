from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr

log = core.getLogger()


def _handle_ConnectionUp (event):
  msg = of.ofp_flow_mod()
  msg.actions.append(of.ofp_action_output(port = 1))
  event.connection.send(msg)
  log.info("Redirecting all traffic to port 1 %s", dpidToStr(event.dpid))
  
def _handle_PacketIn (event):
  log.info("Packet in %s %s", str(event), str(event.parsed))

def launch ():
  core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
  core.openflow.addListenerByName("PacketIn", _handle_PacketIn)

  log.info("Testing controller running.")