FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /audit

COPY scripts/e2b_datadog_audit/requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY scripts/e2b_datadog_audit/audit_e2b.py ./

CMD ["python", "audit_e2b.py", "--help"]
