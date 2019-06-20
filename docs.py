from freezegun import freeze_time
from webtest import TestApp
import openprocurement.audit.inspection.tests.base as base_test
import ConfigParser
import json
import mock
import uuid
import os


class DumpsTestAppwebtest(TestApp):
    def do_request(self, req, status=None, expect_errors=None):
        req.headers.environ["HTTP_HOST"] = "audit-api-dev.prozorro.gov.ua"
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            self.file_obj.write(req.as_bytes(True))
            self.file_obj.write("\n")
            if req.body:
                try:
                    self.file_obj.write(
                        '\n' + json.dumps(json.loads(req.body), indent=2, ensure_ascii=False).encode('utf8'))
                    self.file_obj.write("\n")
                except:
                    pass
            self.file_obj.write("\n")
        resp = super(DumpsTestAppwebtest, self).do_request(req, status=status, expect_errors=expect_errors)
        if hasattr(self, 'file_obj') and not self.file_obj.closed:
            headers = [(n.title(), v)
                       for n, v in resp.headerlist
                       if n.lower() != 'content-length']
            headers.sort()
            self.file_obj.write(str('\n%s\n%s\n') % (
                resp.status,
                str('\n').join([str('%s: %s') % (n, v) for n, v in headers]),
            ))

            if resp.testbody:
                try:
                    self.file_obj.write('\n' + json.dumps(json.loads(resp.testbody), indent=2, ensure_ascii=False).encode('utf8'))
                except:
                    pass
            self.file_obj.write("\n\n")
        return resp


@freeze_time("2018.01.01 00:00")
class BaseDocWebTest(base_test.BaseWebTest):

    def setUp(self):
        self.app = DumpsTestAppwebtest(
            "config:tests.ini", relative_to=os.path.dirname(base_test.__file__))
        self.app.RequestClass = base_test.PrefixedRequestClass
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db

        config = ConfigParser.RawConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'openprocurement/audit/inspection/tests/auth.ini'))
        self.sas_token = config.get("sas", "test_sas")
        self.broker_token = config.get("brokers", "broker")

        self.uuid_counter = 0
        self.uuid_patches = [
            mock.patch(path, side_effect=self._generate_test_uuid)
            for path in (
                'openprocurement.api.utils.uuid4',
                'openprocurement.audit.api.tests.base.uuid4',
                'openprocurement.api.models.uuid4',
                'openprocurement.audit.api.models.uuid4',
            )
        ]
        for p in self.uuid_patches:
            p.start()

    def tearDown(self):
        for p in self.uuid_patches:
            p.stop()
        super(BaseDocWebTest, self).tearDown()

    def _generate_test_uuid(self):
        self.uuid_counter += 1
        return uuid.uuid3(uuid.UUID(int=0), self.id() + str(self.uuid_counter))



class InspectionResourceTest(BaseDocWebTest):
    def setUp(self):
        super(InspectionResourceTest, self).setUp()
        self.app.app.registry.docservice_url = 'http://docs-sandbox.openprocurement.org'

    def test_tutorial(self):

        self.app.authorization = ('Basic', (self.sas_token, ''))

        with open('docs/source/tutorial/http/inspection-list-empty.http', 'w') as self.app.file_obj:
            response = self.app.get('/inspections', status=200)
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['data'], [])

        with open('docs/source/tutorial/http/inspection-post.http', 'w') as self.app.file_obj:
            response = self.app.post_json(
                '/inspections',
                {
                    "data": {

                        "monitoring_ids": [
                            "a6b2b18977f24277b238c7b7a5342b1d",
                            "580997bb06674235801d75f2f6e6c6c6",
                            "2c5cc4a289d747a5b8dacd72adaea4d9",
                        ],
                        "description": "Inspection is an official visit to a building or organization to check "
                                       "that everything is satisfactory and that rules are being obeyed",
                    }
                }
            )
        inspection_id = response.json["data"]["id"]
        self.assertEqual(response.status, '201 Created')

        with freeze_time("2018.01.01 00:01"):
            with open('docs/source/tutorial/http/inspection-document-post.http', 'w') as self.app.file_obj:
                response = self.app.post_json(
                    '/inspections/{}/documents'.format(inspection_id),
                    {
                        "data": {
                            'title': 'doc.txt',
                            'url': self.generate_docservice_url(),
                            'hash': 'md5:' + '0' * 32,
                            'format': 'plain/text',
                        }
                    }
                )
        document_id = response.json["data"]["id"]
        self.assertEqual(response.status, '201 Created')

        with freeze_time("2018.01.01 00:02"):
            with open('docs/source/tutorial/http/inspection-document-put.http', 'w') as self.app.file_obj:
                response = self.app.put_json(
                    '/inspections/{}/documents/{}'.format(inspection_id, document_id),
                    {
                        "data": {
                            'title': 'doc(1).json',
                            'url': self.generate_docservice_url(),
                            'hash': 'md5:' + '0' * 32,
                            'format': 'application/json',
                        }
                    }
                )
        self.assertEqual(response.status, '200 OK')

        with freeze_time("2018.01.01 00:03"):
            with open('docs/source/tutorial/http/inspection-patch.http', 'w') as self.app.file_obj:
                response = self.app.patch_json(
                    '/inspections/{}'.format(inspection_id),
                    {
                        "data": {
                            "description": "I regretted my decision",
                            "monitoring_ids": [
                                "a6b2b18977f24277b238c7b7a5342b1d",
                                "580997bb06674235801d75f2f6e6c6c6",
                            ]
                        }
                    }
                )
        self.assertEqual(response.status, '200 OK')


class InspectionsByMonitoringResourceTest(BaseDocWebTest):
    def setUp(self):
        super(InspectionsByMonitoringResourceTest, self).setUp()
        self.app.app.registry.docservice_url = 'http://docs-sandbox.openprocurement.org'

    def test_tutorial(self):

        self.app.authorization = ('Basic', (self.sas_token, ''))

        monitoring_id = "580997bb06674235801d75f2f6e6c6c6"

        response = self.app.post_json(
            '/inspections',
            {
                "data": {
                    "monitoring_ids": [monitoring_id],
                    "description": "La-la",
                }
            }
        )
        self.assertEqual(response.status, '201 Created')

        with freeze_time("2018.01.01 00:01"):
            response = self.app.post_json(
                '/inspections',
                {
                    "data": {
                        "monitoring_ids": [monitoring_id],
                        "description": "Inspection is an official visit to a building or organization to check "
                                       "that everything is satisfactory and that rules are being obeyed",
                    }
                }
            )
            self.assertEqual(response.status, '201 Created')

        with open('docs/source/inspections_by_monitoring/http/inspections-by-monitoring_id.http', 'w') \
                  as self.app.file_obj:
            response = self.app.get('/monitorings/{}/inspections'.format(monitoring_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json["data"]), 2)

        with open('docs/source/inspections_by_monitoring/http/inspections-by-monitoring_id-opt_fields.http', 'w') \
                  as self.app.file_obj:
            response = self.app.get('/monitorings/{}/inspections?opt_fields=description'.format(monitoring_id))
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json["data"]), 2)
