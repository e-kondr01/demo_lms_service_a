import math
from random import choice, randint

from locust import FastHttpUser, LoadTestShape, between, task
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import Assessment, Institution, Unit
from app.models.foreign import ServiceBInstitution, ServiceCUnit


class StepLoadShape(LoadTestShape):
    """
    A step load shape


    Keyword arguments:

        step_time -- Time between steps
        step_load -- User increase amount at each step
        spawn_rate -- Users to stop/start per second at every step
        time_limit -- Time limit in seconds

    """

    hold_time = 10
    ramp_up_time = 5
    step_time = hold_time + ramp_up_time
    step_load = 100
    spawn_rate = step_load / ramp_up_time
    time_limit = step_time * 20

    def tick(self):
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        current_step = math.floor(run_time / self.step_time) + 1
        return (current_step * self.step_load, self.spawn_rate)


# Get values for filtering from DB
engine = create_engine("postgresql://postgres:postgres@localhost:5432/service_a")
session_factory = sessionmaker(engine, expire_on_commit=False)

with session_factory() as session:
    service_a_unit_ids = session.execute(select(Unit.id)).scalars().all()
    service_a_institution_ids = session.execute(select(Institution.id)).scalars().all()
    service_a_unit_names = session.execute(select(Unit.name).distinct()).scalars().all()
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
    wait_time = between(0.5, 1.1)


class SharedDBTwoTablesUser(AssessmentUser):
    @task
    def get_assessments(self):
        url = f"/api/assessments/shared-db?size={SIZE}"

        page_number = randint(1, MAX_PAGE_NUMBER)
        url += f"&page={page_number}"
        params = {}
        params = add_filter(params, service_a_unit_ids, "unit_id")

        params = add_filter(params, service_a_institution_ids, "institution_id")

        self.client.get(url, params=params)


class SharedDBThreeTablesUser(AssessmentUser):
    @task
    def get_assessments(self):
        url = f"/api/assessments/shared-db?size={SIZE}"

        page_number = randint(1, MAX_PAGE_NUMBER)
        url += f"&page={page_number}"
        params = {}
        params = add_filter(params, service_c_unit_names, "unit_name")
        params = add_filter(params, service_a_assessment_grades, "assessment_grade")
        params = add_filter(params, service_a_institution_ids, "institution_id")

        self.client.get(url, params=params)


class APICompositionTwoServicesUser(AssessmentUser):
    @task
    def get_assessments(self):
        url = f"/api/assessments/api-composition/two-services?size={SIZE}"

        page_number = randint(1, MAX_PAGE_NUMBER)
        url += f"&page={page_number}"
        params = {}
        params = add_filter(params, service_a_unit_ids, "unit_id")

        params = add_filter(params, service_a_institution_ids, "institution_id")

        self.client.get(url, params=params)


class APICompositionThreeServicesUser(AssessmentUser):
    @task
    def get_assessments(self):
        url = f"/api/assessments/api-composition/three-services?size={SIZE}"

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


# Для сценария, когда есть нагрузка и на хост A, и на другие


class ServiceBUser(AssessmentUser):
    host = settings.SERVICE_B_HOST

    @task
    def get_students(self):
        url = "/api/students"

        params = {}
        params = add_filter(params, service_b_institution_ids, "institution_id")

        self.client.get(url, params=params)


class ServiceCUser(AssessmentUser):
    host = settings.SERVICE_C_HOST

    @task
    def get_units(self):
        url = "/api/units"

        params = {}
        params = add_filter(params, service_c_unit_names, "name")

        self.client.get(url, params=params)
