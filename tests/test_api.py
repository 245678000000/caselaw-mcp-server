import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "CaseLaw MCP Server"
    assert data["status"] == "running"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_search_cases(client):
    response = client.get("/api/v1/search", params={"query": "合同"})
    assert response.status_code == 200
    data = response.json()
    assert "cases" in data
    assert "total" in data
    assert data["total"] > 0
    for case in data["cases"]:
        assert "id" in case
        assert "case_name" in case


def test_search_no_results(client):
    response = client.get("/api/v1/search", params={"query": "ZZZZNOTFOUND"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["cases"] == []


def test_get_case_detail(client):
    response = client.get("/api/v1/cases/1001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1001
    assert data["case_name"] == "张三与李四房屋买卖合同纠纷案"
    assert data["full_text"] != ""


def test_get_case_not_found(client):
    response = client.get("/api/v1/cases/9999")
    assert response.status_code == 404


def test_summarize_case(client):
    response = client.get("/api/v1/cases/1001/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "(2023)京01民终1234号"
    assert data["facts"] != ""
    assert data["court_opinion"] != ""
    assert data["judgment_result"] != ""


def test_summarize_not_found(client):
    response = client.get("/api/v1/cases/9999/summary")
    assert response.status_code == 404


def test_compare_cases(client):
    response = client.post("/api/v1/compare", json={"case_ids": [1001, 1004]})
    assert response.status_code == 200
    data = response.json()
    assert len(data["similarities"]) > 0
    assert data["fact_comparison"] != ""
    assert data["judgment_comparison"] != ""


def test_compare_not_found(client):
    response = client.post("/api/v1/compare", json={"case_ids": [1001, 9999]})
    assert response.status_code == 404


def test_extract_rules(client):
    response = client.get("/api/v1/cases/1001/rules")
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == 1001
    assert len(data["rules"]) > 0
    for rule in data["rules"]:
        assert "rule" in rule
        assert "legal_basis" in rule


def test_extract_rules_not_found(client):
    response = client.get("/api/v1/cases/9999/rules")
    assert response.status_code == 404


def test_mcp_list_tools(client):
    response = client.get("/mcp/v1/tools")
    assert response.status_code == 200
    data = response.json()
    assert len(data["tools"]) == 5
    tool_names = [t["name"] for t in data["tools"]]
    assert "search_cases" in tool_names
    assert "get_case_detail" in tool_names
    assert "summarize_case" in tool_names
    assert "compare_cases" in tool_names
    assert "extract_rules" in tool_names


def test_mcp_call_search(client):
    response = client.post(
        "/mcp/v1/tools/search_cases",
        json={"query": "合同"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert data["result"]["total"] > 0


def test_mcp_call_get_detail(client):
    response = client.post(
        "/mcp/v1/tools/get_case_detail",
        json={"case_id": 1001},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["case_name"] == "张三与李四房屋买卖合同纠纷案"


def test_mcp_call_summarize(client):
    response = client.post(
        "/mcp/v1/tools/summarize_case",
        json={"case_id": 1002},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["case_name"] == "王五盗窃案"


def test_mcp_call_compare(client):
    response = client.post(
        "/mcp/v1/tools/compare_cases",
        json={"case_ids": [1001, 1004]},
    )
    assert response.status_code == 200


def test_mcp_call_extract_rules(client):
    response = client.post(
        "/mcp/v1/tools/extract_rules",
        json={"case_id": 1002},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["result"]["rules"]) > 0


def test_mcp_unknown_tool(client):
    response = client.post(
        "/mcp/v1/tools/unknown_tool",
        json={},
    )
    assert response.status_code == 404
