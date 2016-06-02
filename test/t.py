def do_thing(rec):
    fields = {
      'pid' : None,
      'devicetype' : 2,
      'cost' : 0.0,
      'eol_ann' : None,
      'eos' : None,
      'last_ship_date' : None,
      'end_sw_maint' : None,
      'end_routine_fail' : None,
      'end_new_service' : None,
      'end_vul_support' : None,
      'end_srvc_renewal' : None,
      'last_date_support' : None,
    }

    for key in rec.keys():
      if key in fields:
        fields[key] = rec[key]


    ins = "insert into device2(" + ",".join(fields.keys()) + ") values(" + ','.join(["%s"] * len(fields)) + ")"
    ans = fields.values()
    print("Thing=%s=" % ins)
    print(ans)


rec = {'pid' : 'WS-TEST-THING', 'cost' : 20.00, 'eos' : '1964-10-20'}
do_thing(rec)
