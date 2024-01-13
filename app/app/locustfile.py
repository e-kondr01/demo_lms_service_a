from random import choice, randint

from locust import FastHttpUser, between, task

unit_ids = [
    "18c44983-ecae-407c-86b8-b71bf2ac5469",
    "6eb162a3-0b9e-4e63-bf7c-32c34553d774",
    "a1d577e3-8407-4b1b-ba65-7512b71004ed",
    "b0fd3160-0a0d-4f6d-8c0b-896abd39a32b",
    "d86c77ad-618e-4c42-911e-f2f96402dace",
    None,
]

institution_ids = [
    "75f030c7-9119-46d8-8596-50df8f0cdd4b",
    "9c33d459-36c0-41be-b320-cb1ffe9a5e69",
    "d7099ee5-97f2-4362-9751-06945552ddcd",
    "da922717-436f-40a6-aa74-864d398e2633",
    None,
]


class AssessmentUser(FastHttpUser):
    host = "http://127.0.0.1:8000"
    wait_time = between(0.5, 1.5)


class CQRSAssessmentUser(AssessmentUser):
    @task
    def get_assessments(self):
        url = "/api/assessments/cqrs?size=20"
        page_number = randint(1, 178)
        url += f"&page={page_number}"
        unit_id = choice(unit_ids)
        if unit_id:
            url += f"&unit_id={unit_id}"
        institution_id = choice(institution_ids)
        if institution_id:
            url += f"&institution_id={institution_id}"
        self.client.get(url)


class CyclicCompositionAssessmentUser(AssessmentUser):
    @task
    def get_assessments(self):
        url = "/api/assessments/cyclic-api-composition?size=20"
        unit_id = choice(unit_ids)
        if unit_id:
            url += f"&unit_id={unit_id}"
        institution_id = choice(institution_ids)
        if institution_id:
            url += f"&institution_id={institution_id}"
        self.client.get(url)


class PaginatedCompositionAssessmentUser(AssessmentUser):
    @task
    def get_assessments(self):
        url = "/api/assessments/paginated-api-composition?size=20"
        page_number = randint(1, 178)
        url += f"&page={page_number}"
        unit_id = choice(unit_ids)
        if unit_id:
            url += f"&unit_id={unit_id}"
        institution_id = choice(institution_ids)
        if institution_id:
            url += f"&institution_id={institution_id}"
        self.client.get(url)
