from datetime import datetime, timedelta
from textwrap import dedent

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

from utils.callbacks import failure_callback, success_callback

local_timezone = pendulum.timezone("Asia/Seoul")

with DAG(
    dag_id="simple_dag", # "simple_dag"이라는 이름의 DAG 설정
    default_args={ # default_args에는 다음 내용이 들어감
        "owner": "user", # "user" 사용자가 소유한 DAG
        "depends_on_past": False,
        "email": "temp@example.com", # 본인의 이메일
        "email_on_failure": False, # 실패 및 재시도 시 이메일 알림 여부 x
        "email_on_retry": False, # 실패 및 재시도 시 이메일 알림 여부 x
        "retries": 1, # 재시도 1회
        "retry_delay": timedelta(minutes=5), # 재시도 간격 5분
        "on_failure_callback": failure_callback, # 실패 시 callback
        "on_success_callback": success_callback, # 성공 시 callback
    },
    description="Simple airflow dag",
    schedule="0 15 * * *",
    start_date=datetime(2025, 3, 1, tzinfo=local_timezone),
    catchup=False,
    tags=["lgcns", "mlops"],
) as dag:
    task1 = BashOperator(
        task_id="print_date",
        bash_command="date", # 현재 시간을 출력하는 bash_command 입력
    )
    task2 = BashOperator(
        task_id="sleep",
        depends_on_past=False,
        bash_command="sleep 5", # 5초 sleep하는 bash_command
        retries=3, # 3회 재시도하도록 설정
    )

    loop_command = dedent(
        """
        {% for i in range(5) %}
            echo "ds = {{ ds }}"
            echo "macros.ds_add(ds, {{ i }}) = {{ macros.ds_add(ds, i) }}"
        {% endfor %}
        """
    )
    task3 = BashOperator(
        task_id="print_with_loop",
        bash_command=loop_command,
    )

    task1 >> [task2, task3]
