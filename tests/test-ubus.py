import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import ubus

u = ubus.ubus_listener(None)

# split into chunks
assert ubus._split_into_chunks("01") == [0x01]
assert ubus._split_into_chunks("99") == [0x99]
assert ubus._split_into_chunks("FF") == [0xFF]
assert ubus._split_into_chunks("1234", n=2) == [0x12, 0x34]
assert ubus._split_into_chunks("1234", n=4) == [0x1234]

# decode
opcode, data = u.decode("U410102")
assert opcode == 0x41
assert data == [0x01, 0x02]

opcode, data = u.decode("U61123456")
assert opcode == 0x61
assert data == [0x12, 0x34, 0x56]

# convert to actions
action, data = u.convert_to_action(*u.decode("U400102"))
assert action == "play"
assert data == {"node":0x01, "event":0x02}

action, data = u.convert_to_action(*u.decode("U411234"))
assert action == "stop"
assert data == {"node":0x12, "event":0x34}

action, data = u.convert_to_action(*u.decode("U61123456"))
assert action == "play"
assert data == {"loco":0x1234, "function":0x56}

action, data = u.convert_to_action(*u.decode("U62000102"))
assert action == "stop"
assert data == {"loco":0x01, "function":0x02}

# sound from details
u.mappings = []
assert u.sound_from_details(ubus.ACON, {"node":0x01, "event":0x02}) == None

u.mappings = [{"opcode":["ACON", "ACOF"], "node":1, "event":1, "sound":"crow"}]
assert u.sound_from_details(ubus.ACON, {"node":0x01, "event":0x02}) == None
assert u.sound_from_details(ubus.ACON, {"node":0x01, "event":0x01}) == "crow"
assert u.sound_from_details(ubus.ACOF, {"node":0x01, "event":0x01}) == "crow"
assert u.sound_from_details(ubus.ACON, {"node":0x02, "event":0x01}) == None
assert u.sound_from_details(ubus.ACOF, {"node":0x02, "event":0x01}) == None

u.mappings.append({"opcode":["ACON"], "node":"*", "event":1, "sound":"woof"})
assert u.sound_from_details(ubus.ACON, {"node":0x01, "event":0x02}) == None
assert u.sound_from_details(ubus.ACON, {"node":0x02, "event":0x01}) == "woof"
assert u.sound_from_details(ubus.ACON, {"node":0x01, "event":0x01}) == "crow"
assert u.sound_from_details(ubus.ACOF, {"node":0x02, "event":0x01}) == None

u.mappings.append({"opcode":["DFON"], "loco":0x1234, "function":3, "sound":"horn"})
assert u.sound_from_details(ubus.ACOF, {"node":0x02, "event":0x01}) == None
assert u.sound_from_details(ubus.DFON, {"loco":0x1234, "function":0}) == None
assert u.sound_from_details(ubus.DFON, {"loco":0x1234, "function":1}) == None
assert u.sound_from_details(ubus.DFON, {"loco":0x123, "function":3}) == None
assert u.sound_from_details(ubus.DFON, {"loco":0x1234, "function":3}) == "horn"
assert u.sound_from_details(ubus.DFON, {"loco":4660, "function":3}) == "horn"

u.mappings.append({"opcode":["DFON"], "loco":"*", "function":3, "sound":"whistle"})
assert u.sound_from_details(ubus.DFON, {"loco":0x1234, "function":3}) == "horn"
assert u.sound_from_details(ubus.DFON, {"loco":0x123, "function":3}) == "whistle"
assert u.sound_from_details(ubus.DFON, {"loco":0x1234, "function":1}) == None

# packet formatting
assert ubus.format_packet(ubus.ACON, [0x12, 0x34]) == "U401234"
assert ubus.format_packet(ubus.ACON, ["255", 0x34]) == "U40FF34"
assert ubus.format_packet(ubus.ACON, ["0xFF", 0x34]) == "U40FF34"
assert ubus.format_packet(ubus.ACON, ["10", 0x34]) == "U400A34"