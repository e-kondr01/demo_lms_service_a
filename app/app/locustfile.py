import urllib.parse
from random import choice, randint

from locust import FastHttpUser, between, task
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models import Assessment, Institution, Unit
from app.models.foreign import ServiceBInstitution, ServiceCUnit

# Get values for filtering from DB
engine = create_engine("postgresql://postgres:postgres@localhost:5432/service_a")
session_factory = sessionmaker(engine, expire_on_commit=False)

with session_factory() as session:
    service_a_unit_ids = session.execute(select(Unit.id)).scalars().all()
    service_a_institution_ids = session.execute(select(Institution.id)).scalars().all()
    service_a_assessment_grades = (
        session.execute(select(Assessment.grade).distinct()).scalars().all()
    )
    service_b_institution_ids = (
        session.execute(select(ServiceBInstitution.id)).scalars().all()
    )
    service_c_unit_names = (
        session.execute(select(ServiceCUnit.name).distinct()).scalars().all()
    )


def add_filter(params: dict, choices, filter: str) -> dict:
    filter_value = choice(choices)
    return params | {filter: filter_value}


# Менять в сценарии с изменением размера страницы
SIZE = 20
TOTAL_ASSESSMENTS = 275000
MAX_PAGE_NUMBER = int(TOTAL_ASSESSMENTS / SIZE)


class AssessmentUser(FastHttpUser):
    host = "http://127.0.0.1:8000"
    wait_time = between(0.5, 1)


class SharedDBUser(AssessmentUser):
    @task
    def get_assessments(self):
        url = f"/api/assessments/shared-db?size={SIZE}"

        page_number = randint(1, MAX_PAGE_NUMBER)
        url += f"&page={page_number}"
        params = {}
        params = add_filter(params, service_a_unit_ids, "unit_id")

        params = add_filter(params, service_a_institution_ids, "institution_id")

        self.client.get(url, params=params)


class APICompositionTwoServicesCyclicUser(AssessmentUser):
    @task
    def get_assessments(self):
        url = f"/api/assessments/api-composition/two-services/cyclic?size={SIZE}"
        params = {}
        params = add_filter(params, service_a_unit_ids, "unit_id")
        params = add_filter(params, service_a_institution_ids, "institution_id")
        self.client.get(url, params=params)


class APICompositionTwoServicesPrefilterUser(AssessmentUser):
    @task
    def get_assessments(self):
        url = f"/api/assessments/api-composition/two-services/prefilter?size={SIZE}"

        page_number = randint(1, MAX_PAGE_NUMBER)
        url += f"&page={page_number}"
        params = {}
        params = add_filter(params, service_a_unit_ids, "unit_id")

        params = add_filter(params, service_a_institution_ids, "institution_id")

        self.client.get(url, params=params)


class APICompositionThreeServicesCyclicUser(AssessmentUser):
    @task
    def get_assessments(self):
        url = f"/api/assessments/api-composition/three-services/cyclic?size={SIZE}"
        params = {}
        params = add_filter(params, service_c_unit_names, "unit_name")
        params = add_filter(params, service_a_institution_ids, "institution_id")
        params = add_filter(params, service_a_assessment_grades, "assessment_grade")
        self.client.get(url, params=params)


class APICompositionThreeServicesPrefilterUser(AssessmentUser):
    @task
    def get_assessments(self):
        url = f"/api/assessments/api-composition/three-services/prefilter?size={SIZE}"

        page_number = randint(1, MAX_PAGE_NUMBER)
        url += f"&page={page_number}"
        params = {}
        params = add_filter(params, service_c_unit_names, "unit_name")
        params = add_filter(params, service_a_institution_ids, "institution_id")
        params = add_filter(params, service_a_assessment_grades, "assessment_grade")

        self.client.get(url, params=params)


class FDWTwoServicesUser(AssessmentUser):
    @task
    def get_assessments(self):
        url = f"/api/assessments/fdw/two-services?size={SIZE}"

        page_number = randint(1, MAX_PAGE_NUMBER)
        url += f"&page={page_number}"
        params = {}
        params = add_filter(params, service_a_unit_ids, "unit_id")

        params = add_filter(params, service_a_institution_ids, "institution_id")

        self.client.get(url, params=params)


class FDWThreeServicesUser(AssessmentUser):
    @task
    def get_assessments(self):
        url = f"/api/assessments/fdw/three-services?size={SIZE}"

        page_number = randint(1, MAX_PAGE_NUMBER)
        url += f"&page={page_number}"

        params = {}
        params = add_filter(params, service_c_unit_names, "unit_name")
        params = add_filter(params, service_a_assessment_grades, "assessment_grade")
        params = add_filter(params, service_a_institution_ids, "institution_id")
        self.client.get(url, params=params)
