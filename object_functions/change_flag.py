def effect(obj_name, flags_name, flags_val, mode, arbiters=None):
    for arb in arbiters:
        if arb.config["name"] == obj_name:
            if mode == 'e':
                arb.flags[flags_name] = flags_val
            if mode == 's':
                if flags_name not in arb.params:
                    arb.flags[flags_name] = 0
                arb.flags[flags_name] += flags_val
            if mode == 'm':
                if flags_name not in arb.params:
                    arb.flags[flags_name] = 1
                arb.flags[flags_name] *= flags_val
