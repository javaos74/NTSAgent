from dotenv import find_dotenv, load_dotenv
from langchain.agents import tool
import os, requests

@tool
def nts_check_business_status_tool( reg_no: str) -> str:
    """
    입력한 사업자등록번호의 상태를 확인합니다.

    Args:
        reg_no (str): 사업자등록번호
    Returns:
        str: 사업자등록번호의 상태 메세지를 반환합니다.
    """
    body = {
            "b_no": [reg_no.replace("-", "")]
        }
    nts_api_key = os.getenv("NTS_API_KEY")
    url = f"https://api.odcloud.kr/api/nts-businessman/v1/status?serviceKey={nts_api_key}"
    resp = requests.post(url, json=body)
    if resp.status_code == 200:
        data = resp.json()
        status_code = data.get("status_code")
        if status_code == "OK":
            b_stt = data["data"][0]["b_stt"]
            tax_type = data["data"][0]["tax_type"]
            if "match_cnt" in data:
                return f"요청한 사업자등록번호는 {reg_no}는 {b_stt}이며 {tax_type}입니다."
            else:
                return f"요청한 사업자등록번호는 {reg_no}는 {tax_type}"
        else:
            return f"오류가 발생했으며 오류 코드 값은 {status_code}입니다."
    else:
        return f"오류가 발생했으며 오류 코드 값은 {resp.status_code}입니다."

    
if __name__ == "__main__":
    load_dotenv(find_dotenv())
    result = nts_check_business_status_tool("142-87-00979")
    print(result)