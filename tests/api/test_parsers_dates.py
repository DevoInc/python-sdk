import calendar
import unittest
from datetime import datetime, timedelta
from devo.api.client import Client
import pytz
class ParserDateCase(unittest.TestCase):

     def test_from_Date_Days(self):
        now = datetime.now().astimezone(pytz.UTC)
        response_miliseconds = Client._fromDate_parser("2d",now)
        now_miliseconds = (now.timestamp() * 1000 )
        self.assertEqual(response_miliseconds,now_miliseconds-1.728e+8)
     
     def test_from_abosulte_date_Days(self):
        now = datetime.now().astimezone(pytz.UTC)
        response_miliseconds = Client._fromDate_parser("2ad",now)
        adate_miliseconds= datetime.strptime(str(now.date()),'%Y-%m-%d').replace(tzinfo=pytz.utc).timestamp()*1000
        self.assertEqual(response_miliseconds,adate_miliseconds-1.728e+8)
    
     def test_from_date_hours(self):
        now = datetime.now().astimezone(pytz.UTC)
        response_miliseconds = Client._fromDate_parser("2h",now)
        now_miliseconds = (now.timestamp() * 1000 )
        self.assertEqual(response_miliseconds,now_miliseconds-7.2e+6)
     
     def test_from_abosulte_date_hours(self):
        now = datetime.now().astimezone(pytz.UTC)
        response_miliseconds = Client._fromDate_parser("2ah",now)
        adate_miliseconds= datetime.strptime(str(now.date()),'%Y-%m-%d').replace(tzinfo=pytz.utc).timestamp()*1000
        self.assertEqual(response_miliseconds,adate_miliseconds-7.2e+6)

     def test_from_date_minutes(self):
        now = datetime.now().astimezone(pytz.UTC)
        response_miliseconds = Client._fromDate_parser("2m",now)
        now_miliseconds = (now.timestamp() * 1000 )
        self.assertEqual(response_miliseconds,now_miliseconds-120000)
     
     def test_from_abosulte_date_minutes(self):
        now = datetime.now().astimezone(pytz.UTC)
        response_miliseconds = Client._fromDate_parser("2am",now)
        adate_miliseconds= datetime.strptime(str(now.date()),'%Y-%m-%d').replace(tzinfo=pytz.utc).timestamp()*1000
        self.assertEqual(response_miliseconds,adate_miliseconds-120000)

     def test_from_date_seconds(self):
        now = datetime.now().astimezone(pytz.UTC)
        response_miliseconds = Client._fromDate_parser("2s",now)
        now_miliseconds = (now.timestamp() * 1000 )
        self.assertEqual(response_miliseconds,now_miliseconds-2000)
     
     def test_from_abosulte_date_seconds(self):
        now = datetime.now().astimezone(pytz.UTC)
        response_miliseconds = Client._fromDate_parser("2as",now)
        adate_miliseconds= datetime.strptime(str(now.date()),'%Y-%m-%d').replace(tzinfo=pytz.utc).timestamp()*1000
        self.assertEqual(response_miliseconds,adate_miliseconds-2000)

     def test_from_today_date(self):
        now = datetime.now().astimezone(pytz.UTC)
        response_miliseconds = Client._fromDate_parser("today",now)
        adate_miliseconds= datetime.strptime(str(now.date()),'%Y-%m-%d').replace(tzinfo=pytz.utc).timestamp()*1000
        self.assertEqual(response_miliseconds,adate_miliseconds)

     def test_from_endday_date(self):
        now = datetime.now().astimezone(pytz.UTC)
        response_miliseconds = Client._fromDate_parser("endday",now)
        adate_miliseconds= (datetime.strptime(str(now.date()),'%Y-%m-%d').replace(tzinfo=pytz.utc)+ timedelta(hours=23,minutes=59,seconds=59)).timestamp()*1000
        self.assertEqual(response_miliseconds,adate_miliseconds)

     def test_from_endmonth_date(self):
        now = datetime.now().astimezone(pytz.UTC)
        response_miliseconds = Client._fromDate_parser("endmonth",now)
        adate = datetime.strptime(str(now.date()),'%Y-%m-%d').replace(tzinfo=pytz.utc)
        adate_miliseconds= (adate.replace(day = calendar.monthrange(adate.year, adate.month)[1])+ timedelta(hours=23,minutes=59,seconds=59)).timestamp()*1000
        self.assertEqual(response_miliseconds,adate_miliseconds)

     def test_from_now_date(self):
        now = datetime.now().astimezone(pytz.UTC)
        response_miliseconds = Client._fromDate_parser("now",now)
        self.assertEqual(response_miliseconds,now.timestamp()*1000)

     # FromDate in miliseconds (1663664778239.2002) corresponds to "Tue Sep 20 2022 09:06:18 UTC"
     # FromDate in miliseconds Abosulte (1663632000000) corresponds to "Tue Sep 20 2022 00:00:00 UTC"
     def test_to_Date_Days(self):
        fromDateMiliseconds = 1663664778239.2002
        response_miliseconds = Client._toDate_parser(fromDateMiliseconds,"2d")
        self.assertEqual(response_miliseconds,fromDateMiliseconds+1.728e+8)
    
     def test_to_Date_absolute_Days(self):
        fromDateMiliseconds = 1663664778239.2002
        fromDateMilisecondsAbosulte = 1663632000000
        response_miliseconds = Client._toDate_parser(fromDateMiliseconds,"2ad")
        self.assertEqual(response_miliseconds,fromDateMilisecondsAbosulte+1.728e+8)
     
     def test_to_Date_hours(self):
        fromDateMiliseconds = 1663664778239.2002
        response_miliseconds = Client._toDate_parser(fromDateMiliseconds,"2h")
        self.assertEqual(response_miliseconds,fromDateMiliseconds+7.2e+6)
    
     def test_to_Date_absolute_hours(self):
        fromDateMiliseconds = 1663664778239.2002
        fromDateMilisecondsAbosulte = 1663632000000
        response_miliseconds = Client._toDate_parser(fromDateMiliseconds,"2ah")
        self.assertEqual(response_miliseconds,fromDateMilisecondsAbosulte+7.2e+6)
     
     def test_to_Date_minutes(self):
        fromDateMiliseconds = 1663664778239.2002
        response_miliseconds = Client._toDate_parser(fromDateMiliseconds,"2m")
        self.assertEqual(response_miliseconds,fromDateMiliseconds+120000)
    
     def test_to_Date_absolute_minutes(self):
        fromDateMiliseconds = 1663664778239.2002
        fromDateMilisecondsAbosulte = 1663632000000
        response_miliseconds = Client._toDate_parser(fromDateMiliseconds,"2am")
        self.assertEqual(response_miliseconds,fromDateMilisecondsAbosulte+120000)

     def test_to_Date_seconds(self):
        fromDateMiliseconds = 1663664778239.2002
        response_miliseconds = Client._toDate_parser(fromDateMiliseconds,"2s")
        self.assertEqual(response_miliseconds,fromDateMiliseconds+2000)
    
     def test_to_Date_absolute_seconds(self):
        fromDateMiliseconds = 1663664778239.2002
        fromDateMilisecondsAbosulte = 1663632000000
        response_miliseconds = Client._toDate_parser(fromDateMiliseconds,"2as")
        self.assertEqual(response_miliseconds,fromDateMilisecondsAbosulte+2000)

     def test_to_Date_today(self):
        fromDateMiliseconds = 1663664778239.2002
        now = datetime.now().astimezone(pytz.UTC)
        aNowdate = datetime.strptime(str(now.date()),'%Y-%m-%d').replace(tzinfo=pytz.utc)
        response_miliseconds = Client._toDate_parser(fromDateMiliseconds,"today",now)

        self.assertEqual(response_miliseconds,aNowdate.timestamp()*1000)

     def test_to_Date_endday(self):
        fromDateMiliseconds = 1663664778239.2002
        response = 1663718399000 #Corresponds to Tue Sep 20 2022 23:59:59
        response_miliseconds = Client._toDate_parser(fromDateMiliseconds,"endday")

        self.assertEqual(response_miliseconds,response)

     def test_to_Date_endmonth(self):
        fromDateMiliseconds = 1663664778239.2002
        response = 1664582399000 #Corresponds to Fri Sep 30 2022 23:59:59
        response_miliseconds = Client._toDate_parser(fromDateMiliseconds,"endmonth")

        self.assertEqual(response_miliseconds,response)

     def test_to_Date_now(self):
        fromDateMiliseconds = 1663664778239.2002
        now = datetime.now().astimezone(pytz.UTC)
        response_miliseconds = Client._toDate_parser(fromDateMiliseconds,"now",now)

        self.assertEqual(response_miliseconds,now.timestamp()*1000)

if __name__ == '__main__':
    unittest.main()