import unittest
from devo.common import Buffer


class TestLtBuffer(unittest.TestCase):

    def test_proccess_first_line(self):
        self.assertTrue(self.buffer.proccess_first_line(self.first_line))
        self.assertIsNot(self.buffer.size(), 0)

    def test_proccess_data_line(self):
        self.buffer.proccess_recv(self.data_line)
        self.assertIsNot(self.buffer.size(), 0)

    def setUp(self):
        self.buffer = Buffer()
        self.data_first_line = '{"eventdate":1519913235053,' \
                               '"clientIpAddress":2452954210,' \
                               '"timestamp":"01/Mar/2018:14:07:14 +0000",' \
                               '"method":"GET","url":' \
                               '"/product.screen?product_id=235-40LSZ-09823&' \
                               'JSESSIONID=SD8SL6FF10ADFF6","protocol":' \
                               '"HTTP 1.1","statusCode":404,"bytesTransfe' \
                               'rred":3069,"referralUri":"http://www.yahoo.' \
                               'com/cart.do?action=view&itemId=LOG-90&' \
                               'product_id=235-40LSZ-09823&JSESSIONID=SD8SL' \
                               '6FF10ADFF6","userAgent":"Mozilla/4.0 ' \
                               '(compatible; MSIE 6.0; Windows NT 5.1; SV1; ' \
                               '.NET CLR 1.1.4322)","cookie":"gaqfse5dpcm' \
                               '690jdh5ho1f00o2:-","timeTaken":768}\r\n\r\n'

        self.first_line = 'HTTP/1.1 200 OK\r\nServer: nginx\r\nDate: Thu, ' \
                          '01 Mar 2018 14:08:15 GMT\r\nContent-Type: ' \
                          'application/json\r\nTransfer-Encoding: ' \
                          'chunked\r\nConnection: keep-alive\r\nVary: ' \
                          'Accept-Encoding\r\nStrict-Transport-Security: ' \
                          'max-age=15768000; includeSubDomains\r\n' \
                          'X-Content-Type-Options: nosniff\r\n' \
                          'X-Frame-Options: SAMEORIGIN\r\nX-XSS-Protection: ' \
                          '1; mode=block\r\nReferrer-Policy: ' \
                          'same-origin\r\n\r\n20d\r\n' + self.data_first_line

        self.data_line = '190\r\n {"eventdate":1519913684245,"clientIpAddress' \
                         '":1142130470,"timestamp":"01/Mar/2018:14:14:44 ' \
                         '+0000","method":"GET","url":"/","protocol":"HTTP ' \
                         '1.1","statusCode":200,"bytesTransferred":523,' \
                         '"referralUri":"http://www.devo.com/product.' \
                         'screen?product_id=009-73CKH-JASKD&JSESSIONID=' \
                         'SD2SL1FF3ADFF2","userAgent":"Opera/9.20 (Windows ' \
                         'NT 6.0; U; en)","cookie":"3djv1l0ebi7cmsai1131p' \
                         'f2a65:-","timeTaken":589}\r\n\r\n'


if __name__ == '__main__':
    unittest.main()
