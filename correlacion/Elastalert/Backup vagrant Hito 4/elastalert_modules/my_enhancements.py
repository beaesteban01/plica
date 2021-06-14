from elastalert.enhancements import BaseEnhancement
import time

class Delay(BaseEnhancement):
    def process(self, match):
        time.sleep(180)


class AddRuleName1(BaseEnhancement):
    # ElastAlert will do this for each enhancement linked to a rule
    def process(self, match):
        if 'imei' in match:
            #url = "http://who.is/whois/%s" % (match['domain'])
            rule_name = "regla1"
            match['rule_name1'] = rule_name


class AddRuleName2(BaseEnhancement):
    # The enhancement is run against every match The match is passed to the process function where it can be modified in any way 
    # ElastAlert will do this for each enhancement linked to a rule
    def process(self, match):
        if 'address' in match:
            #url = "http://who.is/whois/%s" % (match['domain'])
            rule_name = "regla2"
            match['rule_name2'] = rule_name


class AddRuleName3(BaseEnhancement):
    # The enhancement is run against every match The match is passed to the process function where it can be modified in any way 
    # ElastAlert will do this for each enhancement linked to a rule
    def process(self, match):
        if 'freq' in match:
            #url = "http://who.is/whois/%s" % (match['domain'])
            rule_name = "regla3"
            match['rule_name3'] = rule_name



class AddRelatedCardinality(BaseEnhancement):
    # The enhancement is run against every match The match is passed to the process function where it can be modified in any way 
    # ElastAlert will do this for each enhancement linked to a rule
    def process(self, match):
        #R1 redes mov
        if 'imei' in match:
            #url = "http://who.is/whois/%s" % (match['domain'])
            related_events_r1 = "imei: %s" % (match['imei'])
            match['related_events1'] = related_events_r1
#	if 'match_body.rule_name2' in match:
#            #url = "http://who.is/whois/%s" % (match['domain'])
#            related_events_r2 = "auth: %s" % (match['match_body.auth'])
#            match['related_events2'] = related_events_r2





