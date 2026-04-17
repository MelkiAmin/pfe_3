from django.test import SimpleTestCase

class HealthCheckTests(SimpleTestCase):
    def test_health_endpoint(self):
        response = self.client.get('/api/health/', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
